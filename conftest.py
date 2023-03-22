"""Test configurations"""

import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.django_test_settings"
sys.path.append("tests")
