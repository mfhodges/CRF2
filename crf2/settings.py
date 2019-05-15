"""
Django settings for crf2 project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from configparser import ConfigParser
import django_heroku


config = ConfigParser()
config.read('config/config.ini')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("basedir",BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('django','secret_key',raw=True)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ['127.0.0.1:8000','127.0.0.1','localhost'#'demo-crf.herokuapp.com'#'128.91.177.58'
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")#'/Users/mfhodges/Desktop/CRF2/course/static'#os.path.join(BASE_DIR, "static")



EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = 'course/static/emails' # change this to a proper location
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # to have it sent to console
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # to actually use it
EMAIL_USE_TLS = True
#EMAIL_HOST = config.get('email', 'emailhost')
EMAIL_PORT = 587
#EMAIL_HOST_USER = config.get('email', 'emailhostuser')
#EMAIL_HOST_PASSWORD = config.get('email', 'password')
#DEFAULT_FROM_EMAIL = config.get('email', 'defaultfromemail')




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'course',
	'rest_framework',
    'django_filters',
    'admin_auto_filters',
    'django_celery_beat',
    'django_extensions',
    'rest_framework_swagger',

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

ROOT_URLCONF = 'crf2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            #'libraries':{
            #'template_extra'
            #}
        },
    },
]

WSGI_APPLICATION = 'crf2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'



USE_I18N = True

USE_L10N = True


USE_TZ = True
TIME_ZONE = 'America/New_York'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        #'rest_framework.renderers.TemplateHTMLRenderer', # this line messes up the browsable api
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.SearchFilter','django_filters.rest_framework.DjangoFilterBackend',),
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'drf_link_header_pagination.LinkHeaderPagination',
    'PAGE_SIZE': 30#,
    #'EXCEPTION_HANDLER': 'course.views.custom_exception_handler'
}

from celery.schedules import crontab

# Celery application definition
#
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
# Other Celery settings

CELERY_BEAT_SCHEDULE = {
    'task-number-one': {
        'task': 'course.tasks.task_process_approved',
        'schedule': crontab(minute='*/1')#,
        #'args': (*args)
    }
}
CELERY_BEAT_SCHEDULER: 'django_celery_beat.schedulers:DatabaseScheduler'


django_heroku.settings(locals())
