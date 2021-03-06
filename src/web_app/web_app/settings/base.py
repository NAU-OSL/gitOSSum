"""
Django settings for web_app project.

Generated by 'django-admin startproject' using Django 1.11.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from celery.schedules import crontab   
from kombu import Queue, Exchange

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1x1n@2p)h^@%0v7gckznov25z_m81#jb9q8e$vp#)@j&7*h%o('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    'gitossum.com',
    '138.68.40.43', 
    '127.0.0.1', 
    'mongodb-s-3vcpu-1gb-sfo2-01',
    'mongodb-s-3vcpu-1gb-sfo2-01:8080',
    'git_oss_um_worker@mongodb-s-3vcpu-1gb-sfo2-01',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user_app',
    'django_nose',
    'bootstrap3', 
    'django_mysql',
    'django_celery_beat',
    'celerybeat_status',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Add our templates folder 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'MST'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'gitossum@gmail.com'
EMAIL_HOST_PASSWORD = 'Django123'
EMAIL_PORT = 587

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'static'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Stuff for celery
BROKER_URL='amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTENT = False
CELERY_ACCEPT_CONTENT=['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'MST'
CELERYD_MAX_TASKS_PER_CHILD = 2
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {}
