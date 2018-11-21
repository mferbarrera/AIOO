"""
Django settings for AIOO project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/

"""

# k_7vL#mJ$%-{LMR$
# 7gGj5gVgxU+kry<?

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qcsxx3bp-*j4d=m0qyy*no$7m(wv#p##gtyykw$pf6cfv7p2lh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMIN_TITLE = "AIOO - Bee Projects"


ALLOWED_HOSTS = ['*']

DATA_UPLOAD_MAX_MEMORY_SIZE = None

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'crispy_forms',
    'projects',
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

ROOT_URLCONF = 'DEVOPS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'DEVOPS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'djongo',
        #'ENFORCE_SCHEMA': False,
        #'NAME': 'AIOO',
        #'HOST' : '127.0.0.1',
        ##'HOST': '216.230.145.88',
        #'PORT': 8887,
        #'USER': 'AIOO',
        #'PASSWORD': 'pjHF6YeyE33DDABJNjO_UB_4jGUub-hJ9LKCYYqBfRw',
        #'AUTH_SOURCE': 'AIOO',
        #'AUTH_MECHANISM': 'SCRAM-SHA-1',
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '~/DEVOPS/DEVOPS/DEVOPS/aioo.cnf'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

LOGIN_URL = '/login'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Guatemala'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR,'projects/media/')

EMAIL_HOST = 'a2plcpnl0649.prod.iad2.secureserver.net'
EMAIL_PORT =  587
EMAIL_HOST_USER = "robot@rissotechnologies.com"
EMAIL_HOST_PASSWORD = 'r0b07'
EMAIL_USE_TLS = True


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'