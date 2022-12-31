# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.
import os
DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "pl(@#n^(g3kb*&4s_ah)^+e(b4q(%6!)1!+49urwedjz1z#dzb"
NEVERCACHE_KEY = "gfl-q+ak#3onuipxt=3am@0e@iz@3^!ks(+rb1sa_n(49$0s=)"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        # DB name or path to database file if using sqlite3.
        "NAME": "aavin",
        # Not used with sqlite3.
        "USER": "aavin",
        # Not used with sqlite3.
        "PASSWORD": "kultivate",
        # "PASSWORD":"aavinlocall",
        # "PASSWORD":"aavinlocall",
        # Set to empty string for localhost. Not used with sqlite3.
        # "HOST": "localhost",
        # "HOST": "139.59.80.236",
        "HOST":"65.1.212.193",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "5432",
        # "PORT": "165.22.220.62",
    }
}

# Allowed development hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "::1", "*"]


#static & Media 
STATIC_URL = '/static/'
MEDIA_URL = STATIC_URL + '/media/' 
DATA_DIR = '/opt/aavin-assets/'
STATIC_ROOT = os.path.join(DATA_DIR, STATIC_URL.strip("/"))
MEDIA_ROOT = os.path.join(DATA_DIR, MEDIA_URL.strip("/"))

###################
# DEPLOY SETTINGS #
###################

# These settings are used by the default fabfile.py provided.
# Check fabfile.py for defaults.

# FABRIC = {
#     "DEPLOY_TOOL": "rsync",  # Deploy with "git", "hg", or "rsync"
#     "SSH_USER": "",  # VPS SSH username
#     "HOSTS": [""],  # The IP address of your VPS
#     "DOMAINS": [""],  # Will be used as ALLOWED_HOSTS in production
#     "REQUIREMENTS_PATH": "requirements.txt",  # Project's pip requirements
#     "LOCALE": "en_US.UTF-8",  # Should end with ".UTF-8"
#     "DB_PASS": "",  # Live database password
#     "ADMIN_PASS": "",  # Live admin user password
#     "SECRET_KEY": SECRET_KEY,
#     "NEVERCACHE_KEY": NEVERCACHE_KEY,
# }