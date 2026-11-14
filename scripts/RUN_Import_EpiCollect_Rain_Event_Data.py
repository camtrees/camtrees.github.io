###############################################################################
## Program  : RUN_Import_EpiCollect_Rain_Event_Data.py
##
## Purpose  : Get EpiCollect Rain Event data not yet processed
##
## Requires : datetime to calculate date offsets from today
##            pandas - so EpiCollect results can be placed into a Pandas DataFrame
##            tabulate - prints the Pandas DataFrame
##            camtrees_sql - to access CAMTREES PostgreSQL database
##            epicollect_api - our functions for interacting with EpiCollect
##            execute_query - executes SQL queries on our CAMTREES database
##            print_functions - assists with printing
##            sys - in case we want to call sys.exit()
##
## Author   : Ken Rosenberry <ken.rosenberry@gmail.com>
##
## Revised  : 2026-04-20 Initial Version
##            2026-05-07 Change EpiCollect 'Notes' filed to 'Note'
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
##            2026-07-09 Use .env file to load EpiCollect access tokens
##            2026-07-22 Changes for using config.py file
##            2026-10-15 Ignore HUB entries which don't contain any sites
##            2026-10-19 New LIVE or TEST EpiCollect question
##            2026-11-14 Mods for new Tree TAG System
##            2026-11-14 Use the shared EpiCollect import runner
###############################################################################

# load globals from config.py file
from config import *

# Kenster libraries
from camtrees_sql import *
from epicollect_import_runner import EpicollectImportConfig, run_epicollect_import
from execute_query import execute_query
from print_functions import *

# import sys
# sys.exit()

IMPORT_CONFIG = EpicollectImportConfig(
    project_key="rain",
    client_id=RAIN_CLIENT_ID,
    client_secret=RAIN_CLIENT_SECRET,
    project_name=RAIN_PROJECT_NAME,
    project_slug=RAIN_PROJECT_SLUG,
    token_file="epicollect_cam_tree_rain_event_access_token",
    map_index=3,
    string_columns=("Note",),
)


def epicollect_process_data(df):
    """
    Process the prepared EpiCollect Rain Event DataFrame.
    """
    #------------------------------------------------------------------------------------------
    # Iterate through the EpiCollect records using itertuples()
    #------------------------------------------------------------------------------------------
    for row in df.itertuples():
        # ------------------------------------------------------------------------------------------
        # Skip EpiCollect TEST records
        # ------------------------------------------------------------------------------------------
        if row.LIVE_or_TEST == 'TEST':
            print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. Hubs: {row.rainHubs} Sites: {row.rainSites}")
            print(f"\t ***** NOTE *****: Skipping EpiCollect TEST entry.")
            continue # Skip to next record
        match row.selectBY:
            case 'Site':
                process_epicollect_site_record(row)
            case 'Hub':
                process_epicollect_hub_record(row)
            case _:
                print_with_separator_line(f"Ignoring EpiCollect entry with UNKNOWN record type. selectBy = {row.selectBY}")


def process_epicollect_site_record(row):
    """
    Process a SITE Epicollect record.
    """
    print_with_separator_line(
        f"Processing EpiCollect SITE Record {row.Index}..."
        f"\n\t Sites: {row.rainSites}"
    )

    for rainSite in row.rainSites:
        # ------------------------------------------------------------------------------------------
        # Split the rainSite into cam_org and site
        # ------------------------------------------------------------------------------------------
        cam_org, site = rainSite.split(' - ', 1)
        site = prepare_string_for_sql(site)

        print(f"Processing Site: {site}")

        # ------------------------------------------------------------------------------------------
        # Add water event via SQL
        # ------------------------------------------------------------------------------------------
        sql_camtrees_add_care_action('rain', 'water', '000', 'ZZZ-9999', row.rainDate, row.created_by, site, row.Note)
    return


def process_epicollect_hub_record(row):
    """
    Process a HUB Epicollect record.
    """
    print_with_separator_line(
        f"Processing EpiCollect HUB Record {row.Index}..."
        f"\n\t Hubs: {row.rainHubs}"
    )
    for rainHub in row.rainHubs:
        rainHub = prepare_string_for_sql(rainHub)
        # ------------------------------------------------------------------------------------------
        # Get the Sites linked to a given Hub
        # ------------------------------------------------------------------------------------------
        sql_command = f"SELECT site from cam_sites_hubs where hub = '{rainHub}' ;"
        sites_in_hub = execute_query(sql_command)
        if not sites_in_hub:
            continue

        # ------------------------------------------------------------------------------------------
        # Convert sites_in_hub (a list of single-element tuples) into a comma-separated string
        # ------------------------------------------------------------------------------------------
        sites = ", ".join(item[0] for item in sites_in_hub)
        sites = prepare_string_for_sql(sites)

        # ------------------------------------------------------------------------------------------
        # Add water event via SQL
        # ------------------------------------------------------------------------------------------
        sql_camtrees_add_care_action('rain', 'water', '001', 'ZZZ-9999', row.rainDate, row.created_by, sites, row.Note)
    return


if __name__ == "__main__":
    run_epicollect_import(
        config=IMPORT_CONFIG,
        process_dataframe=epicollect_process_data,
        testing=KR_TESTING,
    )
