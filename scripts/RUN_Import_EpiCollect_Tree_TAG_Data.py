###############################################################################
## Program  : RUN_Import_EpiCollect_Tree_TAG_Data.py
##
## Purpose  : Get data from EpiCollect CAM TREE TAG project
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
## Revised  : 2026-11-13 <hkr> Initial Version
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
    project_key="tag",
    client_id=TAG_CLIENT_ID,
    client_secret=TAG_CLIENT_SECRET,
    project_name=TAG_PROJECT_NAME,
    project_slug=TAG_PROJECT_SLUG,
    token_file="epicollect_cam_tree_tag_access_token",
    map_index=1,
    string_columns=(
        "mother_tree_other",
        "father_tree_other",
        "parent_tree_note",
    ),
)


def epicollect_process_data(df):
    """
    Process the prepared EpiCollect Tree TAG DataFrame.
    """
    #------------------------------------------------------------------------------------------
    # Iterate through the EpiCollect records using itertuples()
    #------------------------------------------------------------------------------------------
    for row in df.itertuples():
        # ------------------------------------------------------------------------------------------
        # Split the Tree Manager into initials and name
        # ------------------------------------------------------------------------------------------
        tree_manager_initials, tree_manager_name = row.tree_manager.split(' - ', 1)
        tag_id = f"{tree_manager_initials} - {row.tag_number}"
        print_with_separator_line(f"***** Processing EpiCollect Record {row.Index}. Tree TAG = {tag_id}")

        # ------------------------------------------------------------------------------------------
        # Skip EpiCollect TEST records
        # ------------------------------------------------------------------------------------------
        if tree_manager_initials == 'TST':
            print(f"\t ***** NOTE *****: Skipping EpiCollect TST entry.")
            continue # Skip to next record

        # ------------------------------------------------------------------------------------------
        # Verify tree_manager_initials and tree_manager_email is a valid combination
        # ------------------------------------------------------------------------------------------
        valid_combinations = {
            ("ENE", "ericevans45@gmail.com"),
            ("ESB", "eva.maineacf@gmail.com"),
            ("HKR", "ken.rosenberry@gmail.com"),
            ("KLC", "kimcolson.sebago@gmail.com"),
            ("KLS", "k.lea.sewell@gmail.com"),
            ("MAM", "markmccollough25@gmail.com")
        }
        # Verify membership
        if (tree_manager_initials, row.created_by) not in valid_combinations:
            print(
                f"\t ***** ERROR *****: Invalid Tree Manager Initials and Email combination. Initials={tree_manager_initials} Email = {row.created_by}")
            continue # Skip to next record

        # ------------------------------------------------------------------------------------------
        # Skip TAGs that already exist. Perhaps user entered the incorrect tag number?
        # ------------------------------------------------------------------------------------------
        if sql_tree_tag_exists(tag_id):
            print(f"\t ***** ERROR *****: Tree TAG = '{tag_id}' ALREADY EXISTS.")
            continue # Skip to next record

        sql_camtrees_add_tree_tag(row, tree_manager_initials)

    return ## END FUNCTION: epicollect_process_data


if __name__ == "__main__":
    run_epicollect_import(
        config=IMPORT_CONFIG,
        process_dataframe=epicollect_process_data,
        testing=KR_TESTING,
    )
