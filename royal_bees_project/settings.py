import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (for local development)
# This line will load variables from a .env file if it exists in your project root.
# On PythonAnywhere, you'll set these variables directly in the web app configuration.
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Get SECRET_KEY from environment variable for production.
# Provide a dummy (insecure) key for local development if the environment variable is not set.
# IMPORTANT: Replace the 'your_new_highly_secure_and_random_secret_key_generated_by_django_goes_here!'
# with the actual key you generated in the Django shell!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your_new_highly_secure_and_random_secret_key_generated_by_django_goes_here!')


# SECURITY WARNING: don't run with debug turned on in production!
# ALWAYS set DEBUG to False in production for security and performance.
DEBUG = False


# Allowed hosts for your production environment.
# Replace 'your-username.pythonanywhere.com' with your actual PythonAnywhere username.
# Add your custom domain (e.g., 'www.royalbeesschools.com') if you have one.
# '.pythonanywhere.com' is a wildcard for all PythonAnywhere subdomains, which is useful.
ALLOWED_HOSTS = ['your-username.pythonanywhere.com', '.pythonanywhere.com', '127.0.0.1']
# If you add a custom domain (e.g., royalbeesschools.com), add it here as well.


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic', # Recommended for Whitenoise during local development
    'core',
    'results',
    # Add any other custom apps here if you have them, e.g., 'news', 'events', 'admissions'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # IMPORTANT: Add Whitenoise middleware right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'royal_bees_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Project-wide templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # Add this back for debug context processor (useful for local dev)
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'royal_bees_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# PythonAnywhere's free tier uses SQLite by default, so this configuration is fine.
# For paid accounts, you might use their PostgreSQL, in which case you'd update this section
# with the provided database credentials from PythonAnywhere.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Set timezone to Africa/Lagos (Nigeria)
TIME_ZONE = 'Africa/Lagos'

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
# Directory where Django will look for static files within your apps
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Your project-wide static folder (e.g., core/static)
]
# The absolute path to the directory where `collectstatic` will gather all static files.
# This is the directory PythonAnywhere will serve from.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # <--- This line is essential for collectstatic

# Use Whitenoise for serving static files efficiently in production.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # <--- This line is essential for Whitenoise


# Media files (user-uploaded content)
# IMPORTANT: For PythonAnywhere free tier, user-uploaded media files stored here
# will NOT persist across server restarts or web app reloads.
# For persistent storage, you'd need to integrate a cloud storage solution (e.g., AWS S3).
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Optional: Redirect URLs after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'