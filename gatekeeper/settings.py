import os
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
CUSTOM_SETTINGS_PATH = "/etc/gatekeeper/settings.py"
if os.path.exists(CUSTOM_SETTINGS_PATH):
    exec(open(CUSTOM_SETTINGS_PATH, "rb").read())
else:
    LOG.warn("Missing custom settings file: %s. " % CUSTOM_SETTINGS_PATH)
