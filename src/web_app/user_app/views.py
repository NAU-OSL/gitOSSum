# Import necessary django libraries
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


# Import all handwritten libraries
from permissions.permissions import login_forbidden
from .forms import MiningRequestForm, SignUpForm, LoginForm, FeedbackForm
from mining_scripts.mining import *
from .models import *
from .tokens import account_activation_token
from .visualizations import *


# Import external libraries
from nvd3 import multiBarHorizontalChart
import random 
import json
from io import BytesIO
from PIL import Image



# Begin views

class HomeView(TemplateView):
    template_name = 'home.html'

def about_us(request):
    template_name = 'about_us.html'
    return render(request, template_name, {})

# Only allow people that are not signed in to access the signup page
@login_forbidden
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your Git-OSS-um account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please  confirm your email address to complete the registration')
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


# Utility function taken from https://medium.com/@frfahim/django-registration-with-confirmation-email-bb5da011e4ef
# That will allow a user to activate their account 
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank  you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation  link is invalid!')


# Only allow people that are logged in to access the mining request form 
@login_required
def mining_request_form_view(request):
    context = {}
    requests = MiningRequest.objects.all()
    template = "form.html"
    
    if request.method == 'POST':
        form = MiningRequestForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your request has been submitted!') 

                # Only create a database object if what is being passed matches our DB form
            obj = MiningRequest.objects.create(
                repo_name=form.cleaned_data.get('repo_name'),
                email=request.user.email,
                send_email=form.cleaned_data.get("email"),
                requested_by=request.user.username
            )

            form = MiningRequestForm()
            return render(request, template, {'form': form})
        
        return render(request, template, {'form': form})

    else:
        form = MiningRequestForm()
        return render(request, template, {'form': form}) 

@login_required
def feedback_form(request):
    context = {}
    template = "feedbackForm.html"
    form = FeedbackForm()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent. Thank you for your feedback!')
            obj = FeebackForm.objects.create(
                subject = form.cleaned_data.get('subject'),
                message = form.cleaned_data.get('message'),
                sender_email = request.user.email,
                requested_by = request.user.username
            )
            EmailMessage(obj.subject, obj.message, obj.sender_email, ['gitossum@gmail.com'])
            return HttpResponseRedirect("")
        return render(request, template, {'form': form})
    else: 
        form = FeedbackForm()
        return render(request, template, {'form': form})
    #return render(request, template, {'form': form}) 



# A page accessible by anyone to see all mined repos (with hyperlinks)
def mined_repos(request):
    template_name = 'repos.html'
    mined_repos = list(MinedRepo.objects.values_list('repo_name', flat=True)) # Obtain all the mining requests          
             
    context = dict()
    try:
        for item in range(0, len(mined_repos)):
            context.update({
                f"repo{item}": [mined_repos[item], find_repo_main_page(mined_repos[item])["owner"]["avatar_url"]]
            })
        print(context)
        return render(request, template_name, {"context":context})
    except Exception:
         return render(request, template_name, {})


# A function that will be used to generate interactive visualizations of 
# mined JSON data for any repo.
def get_repo_data(request, repo_owner, repo_name):
    template_name = 'mined_repo_display.html'
    original_repo = repo_owner.lower() + "/" + repo_name.lower()
    mined_repos = list(MinedRepo.objects.values_list('repo_name', flat=True)) # Obtain all the mining requests
    
    if original_repo in mined_repos:
        repo = mined_repo_sql_obj = MinedRepo.objects.get(repo_name=original_repo)
        context = get_repo_table_context(original_repo)
        context.update({
            "repo_name":original_repo,
            "repo_img":find_repo_main_page(original_repo)['owner']['avatar_url'],
            "bar_chart_html":getattr(repo, "bar_chart_html"),
            "pull_line_chart_html":getattr(repo, "pull_line_chart_html")
        })
        return render(request, template_name, context) 

    else:
        return HttpResponseNotFound('<h1>404 Repo Not Found</h1>')


def compare_two_repos(request, repo_owner1, repo_name1, repo_owner2, repo_name2):
    template_name = 'mined_repo_display_2.html'
    repo_one_full_name = repo_owner1.lower() + "/" + repo_name1.lower()
    repo_two_full_name = repo_owner2.lower() + "/" + repo_name2.lower()

    mined_repos = list(MinedRepo.objects.values_list('repo_name', flat=True)) # Obtain all the mining requests

    if repo_one_full_name in mined_repos and repo_two_full_name in mined_repos:
        context = get_dual_repo_table_context(repo_one_full_name, repo_two_full_name)
        context.update({
            "repo_one_name":repo_one_full_name,
            "repo_one_img":find_repo_main_page(repo_one_full_name)['owner']['avatar_url'],
            "repo_two_name":repo_two_full_name,
            "repo_two_img":find_repo_main_page(repo_two_full_name)['owner']['avatar_url'],
        })
        return render(request, template_name, context) 

    else:
        return HttpResponseNotFound('<h1>404 Repo Not Found</h1>')

def compare_three_repos(request, repo_owner1, repo_name1, repo_owner2, repo_name2, repo_owner3, repo_name3):
    template_name = 'mined_repo_display_3.html'
    repo_one_full_name = repo_owner1.lower() + "/" + repo_name1.lower()
    repo_two_full_name = repo_owner2.lower() + "/" + repo_name2.lower()
    repo_three_full_name = repo_owner3.lower() + "/" + repo_name3.lower()

    mined_repos = list(MinedRepo.objects.values_list('repo_name', flat=True)) # Obtain all the mining requests

    if repo_one_full_name in mined_repos and repo_two_full_name in mined_repos and repo_three_full_name in mined_repos:
        context = get_three_repo_table_context(repo_one_full_name, repo_two_full_name, repo_three_full_name)
        context.update({
            "repo_one_name":repo_one_full_name,
            "repo_one_img":find_repo_main_page(repo_one_full_name)['owner']['avatar_url'],
            "repo_two_name":repo_two_full_name,
            "repo_two_img":find_repo_main_page(repo_two_full_name)['owner']['avatar_url'],
            "repo_three_name":repo_three_full_name,
            "repo_three_img":find_repo_main_page(repo_three_full_name)['owner']['avatar_url'],
        })
        return render(request, template_name, context)

    else:
        return HttpResponseNotFound('<h1>404 Repo Not Found</h1>')
    

     