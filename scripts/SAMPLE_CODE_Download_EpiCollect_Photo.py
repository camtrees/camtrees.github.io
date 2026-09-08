##########################################################################################
## Program  : Example_Download_EpiCollect_Photo.py
##
## Purpose  : Download a hard coded EpiCollect photo
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-07-11 Initial Version
##          : 2026-09-07 Updates for hkr and ChatGPT code revisions
##########################################################################################

# load globals from config.py file
from config import *

# from dotenv import load_dotenv
import os

import requests

# Kenster libraries
from epicollect_api import *


load_dotenv()

epicollect_attribs = {
    # ------------------------------------------------------------------------------------------
    # Get EpiCollect project access tokens
    # ------------------------------------------------------------------------------------------
    # 'CLIENT_ID': os.getenv("MAINT_CLIENT_ID"),
    # 'CLIENT_SECRET': os.getenv("MAINT_CLIENT_SECRET"),
    # 'PROJECT_SLUG': os.getenv("MAINT_PROJECT_SLUG"),
    # 'ACCESS_TOKEN': 'MAINT_ACCESS_TOKEN',
    'CLIENT_ID': MAINT_CLIENT_ID,
    'CLIENT_SECRET': MAINT_CLIENT_SECRET,
    'PROJECT_NAME': MAINT_PROJECT_NAME,
    'PROJECT_SLUG': MAINT_PROJECT_SLUG,
    # ------------------------------------------------------------------------------------------
    # File that stores our access_token
    # ------------------------------------------------------------------------------------------
    'TOKEN_FILE': 'epicollect_cam_tree_maintenance_access_token'
}


# PHOTO_NAME = 'ed45b058-aa0c-4fa5-845b-3873ae3bbdb2_1763582909.jpg'
PHOTO_NAME = '88c67b66-1408-40bf-a7a2-01426061c2de_1778877470.jpg'


# Get Authentication Token
access_token = epicollect_get_access_token(epicollect_attribs)

# Download the Photo
headers = {'Authorization': f'Bearer {access_token}'}
media_url = f"https://five.epicollect.net/api/export/media/{epicollect_attribs['PROJECT_SLUG']}"
params = {
    'type': 'photo',
    'format': 'entry_original', # Use 'entry' for standard photos
    'name': PHOTO_NAME
    }

media_response = requests.get(media_url, params=params, headers=headers, stream=True)

if media_response.status_code == 200:
    with open(PHOTO_NAME, 'wb') as f:
        for chunk in media_response.iter_content(1024):
            f.write(chunk)
    print(f"Successfully downloaded {PHOTO_NAME}")
else:
    print(f"Failed to download: {media_response.status_code}")
