import re

ALBUMID_ONLY_EXTRACT = re.compile('/([0-9]+)/.*?([0-9]+)')
ALBUMNAME_ONLY_EXTRACT = re.compile('/([0-9]+)/([^#]+)')
ALBUMID_PHOTO_EXTRACT = re.compile('/([0-9]+)/.*?([0-9]+)/.*?([0-9]+)')
ALBUMNAME_PHOTO_EXTRACT = re.compile('/([0-9]+)/([^#/]+)#([0-9]+)')
