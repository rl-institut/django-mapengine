"""Module to run django tests for standalone app"""

import sys
import pathlib

import django
import environ
from django.conf import settings
from django.core.management import call_command

env = environ.Env()

DATABASES = {"default": env.db("DATABASE_URL")}

TEST_FOLDER = pathlib.Path(__file__).parent / "django_oemof" / "tests"
TEST_PATH = "django_oemof.tests"


def runtests(test_module=TEST_PATH):
    """Sets up django settings an runs tests"""

    if not settings.configured:
        # Configure test environment
        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=(
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sites",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.admin.apps.SimpleAdminConfig",
                "django.contrib.staticfiles",
                "rest_framework",
                "django_oemof",
            ),
            ROOT_URLCONF="",  # tests override urlconf, but it still needs to be defined
            MIDDLEWARE=(
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ),
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
            MEDIA_ROOT=TEST_FOLDER / "test_data",
        )

    if django.VERSION >= (1, 7):
        django.setup()
    failures = call_command("test", test_module, interactive=False, keepdb=True, failfast=False, verbosity=2)

    sys.exit(bool(failures))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        runtests(test_module=f"{TEST_PATH}.{sys.argv[1]}")
    else:
        runtests()
