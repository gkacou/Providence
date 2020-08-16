"""
Django settings for providence_project project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'blog.apps.BlogConfig',
    'baton',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'baton.autodiscover',
    'admin_reorder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'providence_project.urls'

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

WSGI_APPLICATION = 'providence_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Configuration du template admin : Baton
BATON = {
    'SITE_HEADER': 'Providence',
    'SITE_TITLE': 'Providence',
    'INDEX_TITLE': 'Administration du site',
    'SUPPORT_HREF': '',
    'COPYRIGHT': '', # noqa
    'POWERED_BY': 'Providence',
    'MENU': (
        {'type': 'model', 'app': 'blog', 'name': 'cas', 'label': 'Cas', 'icon': 'fa fa-heart',},
        {'type': 'model', 'app': 'blog', 'name': 'beneficiaire', 'label': 'Bénéficiaires', 'icon': 'fa fa-user-plus',},
        {'type': 'model', 'app': 'blog', 'name': 'reunion', 'label': 'Réunions', 'icon': 'fa fa-users',},
        {'type': 'model', 'app': 'blog', 'name': 'membre', 'label': 'Membres', 'icon': 'fa fa-address-book',},
        {
            'type': 'app',
            'name': 'blog',
            'label': 'Paramètres',
            'icon': 'fa fa-cog',
            'models': (
                {'name': 'communaute', 'label': 'Communautés chrétiennes'},
                {'name': 'naturebesoin', 'label': 'Natures de besoins'},
            )
        },
        {
            'type':'free',
            'label': 'Administration',
            'icon': 'fa fa-lock',
            'perms': ('auth.change_group',),
            'children': [
                {'type': 'model', 'app': 'blog', 'name': 'provuser', 'label': 'Utilisateurs', 'icon': 'fa fa-user',},
                {'type': 'model', 'app': 'auth', 'name': 'group', 'label': 'Groupes', 'icon': 'fa fa-street-view',},
            ]
        },
    )
}

# Organisation des objets sur la page d'accueil
ADMIN_REORDER = (
    # Objets de l'appli
    {
        'app': 'blog',
        'models': ('blog.Cas', 'blog.Beneficiaire', 'blog.Reunion', 'blog.Membre',)
    },

    # Paramètres
    {
        'app': 'blog',
        'label': 'Paramètres',
        'models': ('blog.Communaute', 'blog.NatureBesoin',)
    },
    # Gestion des utilisateurs et des groupes
    {
        'app': 'auth',
        'label': 'Administration',
        'models': ('blog.ProvUser', 'auth.Group',)
    },
)

# Pour le bon fonctionnement de l'appli à la fois en local et sur Heroku
django_heroku.settings(locals())


# Supprimer l'exigence du SSL pour l'utilisation en local et activer le debug
if os.path.isfile(os.path.join(BASE_DIR, ".env")):
    if 'OPTIONS' in DATABASES['default']:
        del DATABASES['default']['OPTIONS']['sslmode']
    DEBUG = True

# Classe User personnalisée pour Providence
AUTH_USER_MODEL = 'blog.ProvUser'

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
             'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}