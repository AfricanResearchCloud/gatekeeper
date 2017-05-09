import os
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
CUSTOM_SETTINGS_PATH = "/etc/gatekeeper/"
CUSTOM_SETTINGS_FILE = CUSTOM_SETTINGS_PATH + "settings.py"
if os.path.exists(CUSTOM_SETTINGS_FILE):
    exec(open(CUSTOM_SETTINGS_FILE, "rb").read())
else:
    LOG.warn("Missing custom settings file: %s. " % CUSTOM_SETTINGS_FILE)
