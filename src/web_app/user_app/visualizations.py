# This file will contain all necessary functionality to
# Produce interactive visualizations of data

from mining_scripts.mining import *
from user_app.models import MinedRepo
from nvd3 import multiBarHorizontalChart, discreteBarChart
import random 
import datetime

import plotly.plotly as py
import plotly.offline as opy
import plotly.graph_objs as go
import plotly.tools as tls
import pandas as pd
import numpy as np

# Example using mutli-bar chart 
def multi_bar_chart():
    type = "multiBarHorizontalChart"
    chart = multiBarHorizontalChart(name=type, height=350)
    chart.set_containerheader("\n\n<h2>" + type + "</h2>\n\n")
    nb_element = 10
    xdata = list(range(nb_element))
    ydata = [random.randint(-10, 10) for i in range(nb_element)]
    ydata2 = [x * 2 for x in ydata]
    extra_serie = {"tooltip": {"y_start": "", "y_end": " Calls"}}
    chart.add_serie(name="Count", y=ydata, x=xdata, extra=extra_serie)
    extra_serie = {"tooltip": {"y_start": "", "y_end": " Min"}}
    chart.add_serie(name="Duration", y=ydata2, x=xdata, extra=extra_serie)
    chart.buildhtml()
    return chart.htmlcontent

def get_repo_table_context(repo_name):
    mined_repo_sql_obj = MinedRepo.objects.get(repo_name=repo_name)
    landing_page = find_repo_main_page(repo_name)
    num_pulls = getattr(mined_repo_sql_obj, 'num_pulls')
    num_closed_merged_pulls = getattr(mined_repo_sql_obj, 'num_closed_merged_pulls')
    num_closed_unmerged_pulls = getattr(mined_repo_sql_obj, 'num_closed_unmerged_pulls')
    num_open_pulls = getattr(mined_repo_sql_obj, 'num_open_pulls')
    description = landing_page['description']
    created_at = landing_page['created_at']
    updated_at = landing_page['updated_at']
    clone_url = landing_page['clone_url']
    homepage = str(landing_page['homepage'])
    if str(homepage) == "" or str(homepage) == "None" or str(homepage) == "null":
        homepage = False
    stargazers_count = landing_page['stargazers_count']
    language = landing_page['language']
    has_wiki = landing_page['has_wiki']
    try:
        license_key = landing_page['license']["key"]
        license_name = landing_page['license']['name']
    except Exception:
        license_key = None
        license_name = None 
    open_issues = landing_page['open_issues']
    network_count = landing_page['network_count']
    subscribers_count = landing_page['subscribers_count']

    return {
        "num_pulls":num_pulls,
        "num_closed_merged_pulls":num_closed_merged_pulls,
        "num_closed_unmerged_pulls":num_closed_unmerged_pulls, 
        "num_open_pulls":num_open_pulls,
        "description":str(description),
        "created_at":datetime.datetime.strptime(str(created_at), "%Y-%m-%dT%H:%M:%SZ"),
        "updated_at":datetime.datetime.strptime(str(updated_at), "%Y-%m-%dT%H:%M:%SZ"),
        "clone_url":str(clone_url),
        "homepage":homepage,
        "stargazers_count":int(stargazers_count),
        "language":str(language),
        "has_wiki":bool(has_wiki),
        "license_key":str(license_key),
        "license_name":str(license_name),
        "open_issues":int(open_issues),
        "network_count":int(network_count),
        "subscribers_count":int(subscribers_count)
    }

def pull_request_charts(repo_name):
    mined_repo_sql_obj = MinedRepo.objects.get(repo_name=repo_name)
    num_closed_merged_pulls = getattr(mined_repo_sql_obj, 'num_closed_merged_pulls')
    num_closed_unmerged_pulls = getattr(mined_repo_sql_obj, 'num_closed_unmerged_pulls')
    num_open_pulls = getattr(mined_repo_sql_obj, 'num_open_pulls')

    trace2 = go.Bar(
        x=["Closed-Merged", "Closed-Unmerged", "Open"],
        y=[num_closed_merged_pulls, num_closed_unmerged_pulls, num_open_pulls], 
        name='Pulls Bar Chart',
        marker=dict(
            color=['rgba(255,0,0,1)', 
                   'rgba(0,94,255,1)',
                   'rgba(8,154,105,1)']
        )
    )

    data2 = [trace2]

    layout1=go.Layout(title="Pull Request Types Pie Chart")


    layout2 = go.Layout(
        title='Pull Request Bar Chart',
        xaxis=dict(
            title='Pull Request Type',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title='Number of Pull Requests',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )


    figure2=go.Figure(data=data2,layout=layout2)

    div2 = opy.plot(figure2,  output_type='div')

    return {"bar_chart":div2}
    

def pull_requests_per_month_line_chart(repo_name):
    mined_repo_sql_obj = MinedRepo.objects.get(repo_name=repo_name)
    created_dates_str = getattr(mined_repo_sql_obj, "created_at_list")
    closed_dates_str = getattr(mined_repo_sql_obj, "closed_at_list")
    merged_dates_str = getattr(mined_repo_sql_obj, "merged_at_list")

    try:
        created_dates = pd.to_datetime(pd.Series(created_dates_str), format="%Y-%m-%d %H:%M:%S")
        created_dates.index = created_dates.dt.to_period('m')
        created_dates = created_dates.groupby(level=0).size()
        created_dates = created_dates.reindex(pd.period_range(created_dates.index.min(),
                                            created_dates.index.max(), freq='m'), fill_value=0)
        created_indices = np.array(created_dates.index.astype(str))
        created_date_freq = np.array(created_dates)
    except Exception:
        created_indices = []
        created_date_freq = []

    try:
        closed_dates = pd.to_datetime(pd.Series(closed_dates_str), format="%Y-%m-%d %H:%M:%S")
        closed_dates.index = closed_dates.dt.to_period('m')
        closed_dates = closed_dates.groupby(level=0).size()
        closed_dates = closed_dates.reindex(pd.period_range(closed_dates.index.min(),
                                            closed_dates.index.max(), freq='m'), fill_value=0)
        closed_indices = np.array(closed_dates.index.astype(str))
        closed_date_freq = np.array(closed_dates)
    except:
        closed_indices = []
        closed_date_freq = []

    try:
        merged_dates = pd.to_datetime(pd.Series(merged_dates_str), format="%Y-%m-%d %H:%M:%S")
        merged_dates.index = merged_dates.dt.to_period('m')
        merged_dates = merged_dates.groupby(level=0).size()
        merged_dates = merged_dates.reindex(pd.period_range(merged_dates.index.min(),
                                            merged_dates.index.max(), freq='m'), fill_value=0)
        merged_indices = np.array(merged_dates.index.astype(str))
        merged_date_freq = np.array(merged_dates)
    except Exception:
        merged_indices = []
        merged_date_freq = []
    
    data = [
        go.Scatter(
            x=created_indices, 
            y=created_date_freq,
            mode = 'lines+markers',
            name="Created"
        ),
        go.Scatter(
            x=closed_indices, 
            y=closed_date_freq,
            mode = 'lines+markers',
            name="Closed"
        ),
        go.Scatter(
            x=merged_indices, 
            y=merged_date_freq,
            mode = 'lines+markers',
            name="Merged"
        )
    ]

    layout = go.Layout(
        title='Pull Request Frequency by Month',
        xaxis=dict(
            title='Date',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        ),
        yaxis=dict(
            title='Number of Pull Requests',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )

    figure=go.Figure(data=data,layout=layout)

    div = opy.plot(figure,  output_type='div')
    return div


