# Source - https://stackoverflow.com/a/59342269
# Posted by Kieran Wood
# Retrieved 2026-09-27, License - CC BY-SA 4.0

from whitenoise.storage import CompressedManifestStaticFilesStorage
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class AstroEduManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
