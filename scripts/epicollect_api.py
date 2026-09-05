###############################################################################
## Program  : epicollect_api.py
##
## Purpose  : EpiCollect API calls and functions
##
## Requires : pandas - EpiCollect results are in a Pandas DataFrame
##            pyepicollect - for reading EpiCollect 5 data
##            print_functions - to assist with printing
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-03-09 Initial Version
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
##            2026-07-22 <hkr> Storing access tokens in file (was using .env)
##            2026-09-05 <hkr> Make token caching safe for GitHub Actions
###############################################################################

# Python libraries
import os
from pathlib import Path

import pandas as pd
import pyepicollect as pyep

# Kenster libraries
from print_functions import *


def _token_path(token_file):
    """Return the local token-cache path without ever exposing its contents."""
    token_directory = os.getenv("EPICOLLECT_TOKEN_DIR")
    if token_directory:
        return Path(token_directory) / Path(token_file).name
    return Path(token_file)


def epicollect_get_access_token(epicollect_attribs) -> str:
    """
    Validate our access_token. If it's not valid, get a new one.
    """

    # Read our current access_token from a local file. A missing or empty cache is
    # normal on a fresh GitHub runner and simply causes a new token to be requested.
    file_path = _token_path(epicollect_attribs['TOKEN_FILE'])
    access_token = ""
    try:
        access_token = file_path.read_text(encoding='utf-8').strip()
    except FileNotFoundError:
        print("No cached EpiCollect access token was found.")
    except OSError as error:
        print(f"The cached EpiCollect access token could not be read: {error}")

    if access_token:
        # Try using the cached token. An API error means it is stale or invalid.
        try:
            project = pyep.api.get_project(epicollect_attribs['PROJECT_SLUG'], access_token)
            if isinstance(project, dict) and 'errors' not in project:
                print("\nThe cached EpiCollect access token is still valid.")
                return access_token
        except Exception as error:
            print(f"The cached EpiCollect access token could not be validated: {error}")

    print("\nRequesting a new EpiCollect access token...")
    return epicollect_get_new_access_token(epicollect_attribs)


def epicollect_get_new_access_token(epicollect_attribs):
    """
    Get (and save) a new Epicollect access_token.
    """
    if not epicollect_attribs.get('CLIENT_SECRET'):
        raise RuntimeError("The required EpiCollect client secret is not configured.")

    print('Getting a new access token...')
    new_access_token = pyep.auth.request_token(epicollect_attribs['CLIENT_ID'], epicollect_attribs['CLIENT_SECRET'])
    access_token = new_access_token.get('access_token')
    if not access_token:
        raise RuntimeError("EpiCollect did not return an access token.")

    # Store the token in a private local cache. GitHub Actions points this at the
    # runner's temporary directory so the token can never enter the public site.
    file_path = _token_path(epicollect_attribs['TOKEN_FILE'])
    file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    file_path.write_text(access_token, encoding='utf-8')
    file_path.chmod(0o600)

    return access_token


def epicollect_print_detailed_project_info(epicollect_attribs, access_token):
    #-----------------------------------------------------------------------------------------
    # Get EpiCollect detailed Project Info (forms, mapping, stats)
    #-----------------------------------------------------------------------------------------
    project = pyep.api.get_project(epicollect_attribs['PROJECT_SLUG'], access_token)
    my_pretty_print(project)


def epicollect_print_project_info(epicollect_attribs):
    """
    Get EpiCollect project info.
    """
    project = pyep.api.search_project(epicollect_attribs['PROJECT_NAME'])
    my_pretty_print(project)


def epicollect_get_project_data(epicollect_attribs, access_token):
    #-----------------------------------------------------------------------------------------
    # Gets the first 50 data entries
    #
    # Note: EpiCollect paginates returned data with 50 (by default) records per page.
    #       We could specify upp to 1000 entries per page.
    #       But lets leave it at 50 so we know how to step through multiple pages.
    #-----------------------------------------------------------------------------------------
    entries = pyep.api.get_entries(
        epicollect_attribs['PROJECT_SLUG'],
        access_token,
        filter_by=epicollect_attribs['FILTER_BY'],
        filter_from=epicollect_attribs['FILTER_FROM'],
        filter_to=epicollect_attribs['FILTER_TO'],
        map_index=epicollect_attribs['MAP_INDEX'],
    )

    #-----------------------------------------------------------------------------------------
    # Show user total number of entries and number of pages
    #-----------------------------------------------------------------------------------------
    print('\n' + 'Number of EpiCollect entries: ' + str(entries['meta']['total']))
    print('Number of pages: ' + str(entries['meta']['last_page']) + '\n')
    data = entries['data']['entries']

    #-----------------------------------------------------------------------------------------
    # Collect the data for the first 50 records from the entries
    #-----------------------------------------------------------------------------------------
    data = entries['data']['entries']

    #-----------------------------------------------------------------------------------------
    # Get the rest of the data from the remaining pages (if any)
    #-----------------------------------------------------------------------------------------
    while entries['meta']['current_page'] < entries['meta']['last_page']:
        entries = pyep.api.get_entries(
            epicollect_attribs['PROJECT_SLUG'],
            access_token,
            filter_by=epicollect_attribs['FILTER_BY'],
            filter_from=epicollect_attribs['FILTER_FROM'],
            filter_to=epicollect_attribs['FILTER_TO'],
            map_index=epicollect_attribs['MAP_INDEX'],
            page=(entries['meta']['current_page'] + 1)
        )
        data = data + entries['data']['entries']

    return data


def zulu_to_eastern(df):
    """
    Convert the 'created_at' and 'uploaded_at' columns of a pandas dataframe to Eastern time zone.
    Also, keep only the date part of the 'created_at' column.
    """
    # Ensure the columns are a datetime object (Zulu 'Z' is automatically recognized as UTC)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['uploaded_at'] = pd.to_datetime(df['uploaded_at'], utc=True)

    # Convert to Eastern Time and format as a date string
    # 'US/Eastern' handles both EST and EDT automatically
    df['created_at'] = df['created_at'].dt.tz_convert('US/Eastern').dt.strftime('%Y-%m-%d')
    df['uploaded_at'] = df['uploaded_at'].dt.tz_convert('US/Eastern') # Keep the time on this column

    return df
