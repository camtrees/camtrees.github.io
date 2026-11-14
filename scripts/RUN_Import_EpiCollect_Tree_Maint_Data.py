###############################################################################
## Program  : RUN_Import_EpiCollect_Tree_Maint_Data.py
##
## Purpose  : Get EpiCollect Tree Maintenance data not yet processed
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
## Revised  : 2026-04-22 <hkr> Initial Version
##            2026-05-07 <hkr> Change from CAMWILD to WildCAM
##            2026-05-07 <hkr> Change from DENTATA to WildTACF
##            2026-05-07 <hkr> Change EpiCollect 'Notes' field to 'Note'
##            2026-05-16 <hkr> Changes required to process WildTACF trees
##            2026-06-06 <hkr> Allow for EpiCollect MAP_INDEX
##            2026-07-11 Use .env file to load EpiCollect access tokens
##            2026-07-22 Changes for using config.py file
##            2026-10-19 New LIVE or TEST EpiCollect question
##            2026-10-19 Remove WILD TACF and WILD CAM pathways
##            2026-11-14 Use the shared EpiCollect import runner
###############################################################################

# load globals from config.py file
from config import *

# Kenster libraries
from camtrees_sql import *
from epicollect_import_runner import EpicollectImportConfig, run_epicollect_import
from print_functions import *

# import sys
# sys.exit()

IMPORT_CONFIG = EpicollectImportConfig(
    project_key="maint",
    client_id=MAINT_CLIENT_ID,
    client_secret=MAINT_CLIENT_SECRET,
    project_name=MAINT_PROJECT_NAME,
    project_slug=MAINT_PROJECT_SLUG,
    token_file="epicollect_cam_tree_maintenance_access_token",
    map_index=1,
    string_columns=(
        "Access_Note_PLANT",
        "Tree_Form",
        "Access_Method_ONE",
        "Tree_Photo",
        "Tree_Photo2",
        "Note",
    ),
)


def epicollect_process_data(df):
    """
    Process the prepared EpiCollect Tree Maintenance DataFrame.
    """
    #------------------------------------------------------------------------------------------
    # Iterate through the EpiCollect records using itertuples()
    #------------------------------------------------------------------------------------------
    for row in df.itertuples():
        # ------------------------------------------------------------------------------------------
        # Split the CAM_Org_Site into cam_org and site
        # ------------------------------------------------------------------------------------------
        cam_org, site = row.CAM_Org_Site.split(' - ', 1)
        site = prepare_string_for_sql(site)

        # ------------------------------------------------------------------------------------------
        # Skip EpiCollect TEST records
        # ------------------------------------------------------------------------------------------
        if row.LIVE_or_TEST == 'TEST':
            print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{row.Record_Type}', cam_org = '{cam_org}', site = '{site}' ")
            print(f"\t ***** NOTE *****: Skipping EpiCollect TEST entry.")
            continue # Skip to next record

        # ------------------------------------------------------------------------------------------
        # Process the ALL, GPS, ONE, or PLANT EpiCollect record
        # ------------------------------------------------------------------------------------------
        match (cam_org, row.Record_Type):
            case (any_value, 'ALL'):
                process_epicollect_all(row, site)
            case (any_value, 'GPS'):
                process_epicollect_gps(row, site)
            case (any_value, 'ONE'):
                process_epicollect_one(row, site)
            case (any_value, 'PLANT'):
                process_epicollect_plant(row, site)
            case _, _:
                print_with_separator_line(f"***** Skipping UNKNOWN EpiCollect record for cam_org = '{cam_org}' record_type = '{row.Record_Type}'")

    return ## END FUNCTION: epicollect_process_data


def process_epicollect_all(row, site):
    record_type = 'ALL'
    tree_number = 'NULL' # We don't use a tree_number when processing an EpiCollect ALL record.

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}'")

    check_for_care_actions(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_all


def process_epicollect_gps(row, site):
    record_type = 'GPS'
    tree_number = prepare_string_for_sql(row.Tree_Number_GPS)
    longitude = prepare_string_for_sql(str(row.Tree_Location_GPS["longitude"]))
    latitude = prepare_string_for_sql(str(row.Tree_Location_GPS["latitude"]))

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', tree_number = '{tree_number}', longitude = '{longitude}', latitude = '{latitude}'  ")

    if longitude == 'NULL' or latitude == 'NULL':
        print(f"\t ***** ERROR *****: Missing GPS data for tree number = '{tree_number}'.")
        return ## EARLY EXIT

    if not sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' DOES NOT exist.")
        return ## EARLY EXIT

    if sql_gps_locked(site, tree_number):
        print(f"\t ***** ERROR *****: GPS is 'locked' for tree number = '{tree_number}'.")
        return ## EARLY EXIT

    sql_update_gps(site, tree_number, longitude, latitude, row.Note)

    return ## END FUNCTION: process_epicollect_gps


def process_epicollect_one(row, site):
    record_type = 'ONE'
    tree_number = prepare_string_for_sql(row.Tree_Number_ONE)

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}' tree_number = '{tree_number}'")

    if not sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' DOES NOT exist.")
        return ## EARLY EXIT

    if row.Tree_Form != 'NULL':
        sql_update_tree_form(site, tree_number, row.Tree_Form)
    else:
        print(f"\t***** Ignoring a NULL tree_form for tree number = '{tree_number}'.")

    if row.Access_Method_ONE != 'NULL':
        sql_update_access_method(site, tree_number, row.Access_Method_ONE)
    else:
        print(f"\t***** Ignoring a NULL access_method for tree number = '{tree_number}'.")

    sql_camtrees_add_health_assessment(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_one


def process_epicollect_plant(row, site):
    record_type = 'PLANT'
    tree_number = prepare_string_for_sql(row.Tree_Number_PLANT)

    longitude = prepare_string_for_sql(str(row.Tree_Location_PLANT["longitude"]))
    latitude = prepare_string_for_sql(str(row.Tree_Location_PLANT["latitude"]))

    print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. record_type = '{record_type}', site = '{site}', tree_number = '{tree_number}', longitude = '{longitude}', latitude = '{latitude}'")

    if sql_tree_exists(site, tree_number):
        print(f"\t ***** ERROR *****: Tree number = '{tree_number}' at Site = '{site}' ALREADY exists.")
        return ## EARLY EXIT

    if not sql_tree_tag_exists(tree_number):
        print(f"\t ***** ERROR *****: Tree TAG = '{tree_number}' does NOT exist.")
        return ## EARLY EXIT

    sql_camtrees_add_tree(row, record_type, site, tree_number)

    sql_camtrees_add_tree_initial_health(row, record_type, site, tree_number)

    check_for_care_actions(row, record_type, site, tree_number)

    check_for_tree_photos(row, record_type, site, tree_number)

    return ## END FUNCTION: process_epicollect_plant


if __name__ == "__main__":
    run_epicollect_import(
        config=IMPORT_CONFIG,
        process_dataframe=epicollect_process_data,
        testing=KR_TESTING,
    )
