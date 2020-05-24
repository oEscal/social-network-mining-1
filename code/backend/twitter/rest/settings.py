"""
Django settings for rest project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from credentials import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_%1@c-&2&h@c1ysee8s&xtzikk=!m+^09qtk^8-hv6*f-02k8-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'api.apps.ApiConfig',
	'rest_framework_swagger',
	'corsheaders',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'rest.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'rest.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_ROUTERS = ["rest.db_router.DB_Router"]
# Change Database names, if necessary
DATABASES = {
	'default': {},
	'mongo': {
		'ENGINE': 'djongo',
		'NAME': MONGO_DB,
		'HOST': "mongodb://" + (f"{MONGO_URL}:{MONGO_PORT}/{MONGO_DB}" if MONGO_USERNAME == '' and MONGO_PASSWORD == ''
		                        else MONGO_FULL_URL),
		'ENFORCE_SCHEMA': False,
	},
	'postgres': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': POSTGRES_DB,
		'USER': POSTGRES_USERNAME,
		'PASSWORD': POSTGRES_PASSWORD,
		'HOST': POSTGRES_URL,
		'PORT': POSTGRES_PORT,
	}
}

CACHE_TTL = 60 * 60 * 24             # 1 day
CACHES = {
	"default": {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": "redis://172.26.0.2:6379/1",
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient"
		},
		"KEY_PREFIX": "pi_rest"
	}
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'}

CORS_ORIGIN_ALLOW_ALL = True

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
