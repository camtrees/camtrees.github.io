###############################################################################
## Program  : epicollect_import_runner.py
##
## Purpose  : Shared orchestration and DataFrame preparation for the nightly
##            EpiCollect import programs.
###############################################################################

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Sequence

import pandas as pd
from tabulate import tabulate

from camtrees_sql import prepare_string_for_sql, sql_get_epicollect_last_import_date
from epicollect_api import (
    epicollect_get_access_token,
    epicollect_get_project_data,
    zulu_to_eastern,
)
from execute_query import execute_query
from print_functions import LINE_SEP


@dataclass(frozen=True)
class EpicollectImportConfig:
    """Values that differ between EpiCollect projects."""

    project_key: str
    client_id: str
    client_secret: str | None
    project_name: str
    project_slug: str
    token_file: str
    map_index: int
    string_columns: tuple[str, ...] = ()
    filter_by: str = "uploaded_at"


def build_epicollect_attributes(
    config: EpicollectImportConfig,
    filter_from: date,
    filter_to: date,
) -> dict:
    """Build the attribute dictionary expected by epicollect_api.py."""
    attributes = {
        "CLIENT_ID": config.client_id,
        "CLIENT_SECRET": config.client_secret,
        "PROJECT_NAME": config.project_name,
        "PROJECT_SLUG": config.project_slug,
        "FILTER_BY": config.filter_by,
        "FILTER_FROM": filter_from,
        "FILTER_TO": filter_to,
        "MAP_INDEX": config.map_index,
        "TOKEN_FILE": config.token_file,
    }

    print(
        f"\nFILTER_BY   : {attributes['FILTER_BY']}"
        f"\nFILTER_FROM : {attributes['FILTER_FROM']}"
        f"\nFILTER_TO   : {attributes['FILTER_TO']}"
    )
    return attributes


def prepare_epicollect_dataframe(
    data: Sequence[dict],
    string_columns: Sequence[str],
    testing: bool,
) -> pd.DataFrame:
    """Apply the preparation steps shared by all EpiCollect imports."""
    dataframe = pd.DataFrame(data)

    print("\nThe DataFrame as received from EpiCollect...")
    print(tabulate(dataframe, headers="keys", tablefmt="psql"))

    if testing:
        print("\nKenster is TESTING. The DataFrame with only Kenster data...")
        dataframe.drop(
            dataframe[dataframe["created_by"] != "ken.rosenberry@gmail.com"].index,
            inplace=True,
        )
        print(tabulate(dataframe, headers="keys", tablefmt="psql"))

    # Sort before created_at is converted from a timestamp to an Eastern date.
    dataframe.sort_values(by="created_at", ascending=True, inplace=True)
    print("\nThe DataFrame sorted by the 'created_at' column...")
    print(tabulate(dataframe, headers="keys", tablefmt="psql"))

    dataframe = zulu_to_eastern(dataframe)
    for column in string_columns:
        dataframe[column] = prepare_string_for_sql(dataframe[column])

    print("\nThe DataFrame NOW READY to be processed...")
    print(tabulate(dataframe, headers="keys", tablefmt="psql"))
    return dataframe


def run_epicollect_import(
    config: EpicollectImportConfig,
    process_dataframe: Callable[[pd.DataFrame], None],
    testing: bool = False,
) -> None:
    """Download, prepare, process, and checkpoint one EpiCollect project."""
    pd.set_option("display.max_columns", None)

    if testing:
        filter_from = date.today()
        filter_to = date.today() + timedelta(days=1)
    else:
        filter_from = sql_get_epicollect_last_import_date(config.project_key)
        filter_to = date.today() - timedelta(days=1)

    attributes = build_epicollect_attributes(config, filter_from, filter_to)
    access_token = epicollect_get_access_token(attributes)
    data = epicollect_get_project_data(attributes, access_token)

    if not data:
        print("***** No data to process")
    else:
        dataframe = prepare_epicollect_dataframe(
            data,
            string_columns=config.string_columns,
            testing=testing,
        )
        process_dataframe(dataframe)

    # Preserve the existing behavior: test runs never advance the checkpoint,
    # while successful production runs advance it even when no rows were found.
    if not testing:
        filter_to_as_str = filter_to.strftime("%Y-%m-%d")
        updated_rows = execute_query(
            "UPDATE epicollect_import_date "
            f"SET date = '{filter_to_as_str}' "
            f"WHERE epicollect_project = '{config.project_key}';"
        )
        print(f"\n{LINE_SEP}")
        print(
            f"***** Updated {updated_rows} row(s) in the "
            "epicollect_import_date table."
        )
