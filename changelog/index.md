---
title: CAMTREES Database Changelog
layout: default
nav_order: 98
---

<img src="../assets/images/website/changelog.png" alt="CAMTREE Volunteer consulting a day planner showing the ChangeLog" height="512" width="828">

# {{ page.title }}
_Version: July 13 edit # 2_

<!-- This content will not appear in the rendered Markdown 
<details markdown="1">
<summary markdown="span"><strong>YYYY Month</strong></summary>

### Area (EpiCollect / GitHub / Python / SQL / Website)
### EpiCollect
### GitHub
### Google Map
### Python
### SQL
### SQL Functions
### SQL Hosting
### SQL Tables
### SQL Views
### Website Content
### Website Infrastructure

* Change/Impact/Notes

Note:

* All timestamps use ISO format (`YYYY-MM-DD`) for consistency.
* Each entry should be mostly immutable once published.
* New entries should be appended at the top of each section.
* Keep descriptions short, factual, and action-oriented.

</details>
-->

This changelog documents updates to the CAMTREES Database, and its supporting systems:
EpiCollect, GitHub, Google, Python, SQL, and this website.
Each entry is grouped by month. Within each month, changes are organized by area.

---

## Changelog Entries

---

<details markdown="1">
<summary markdown="span"><strong>2026 July</strong></summary>

### EpiCollect
* Created HKR Tree TAG test project for possible use by Tree-Managers

### GitHub
* Created new camtrees/codebase to house SQL and Python source code
* Add Python PyCharm Project to camtrees.github.io repository

### Google Map
* Added each trees height in inches and in human readable form (ft and inches)

### Python
* Using .env file to keep SQL and EpiCollect Connection Parameters and Access Tokens secret

### SQL Views
* Created cam_tree_latest_height view

### Website Content
* Created content for the GitHub page under the Info for Database Admins hierarchy

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 June</strong></summary>

### EpiCollect

* Add "Collect LIVE Data? Just TESTING?" question for WildCAM and WildTACF trees
* Edit CLEW - Franklin Park tree numbers 100 and 200 to be 006 and 005

### Python
* Call sql_add_tree_initial_health function to set health of newly planted tree to 'good'
* Changes necessitated by removal of location_note from SQL tables_
* Allow for specification of EpiCollect MAP_INDEX when retrieving data

### SQL Hosting
* Master CAMTREES Database is now under the CamOrgDatabase@gmail.com Neon User

### SQL Functions
* Coded sql_add_tree_initial_health function to allow setting of newly planted tree

### SQL Tables
* Remove location_note column; move existing data into access_note column
* Worked with Marc to get MAFP - Field NE of Building Site data imported from EpiCollect

### SQL Views
* Renamed many "cam_..." views to be "data_..."
* Added cam_export_tree_parent_type_for_epicollect
* Added cam_export_volunteer_email_for_epicollect

### Website Content
* Created content for the "Google Services" page
* Created content for the "Info for Database Admins" page
* Created the Using ChatGPT to Create WebSite Illustrations web page

### Website Infrastructure
* Added Info for Database Users section
* Added more ChatGPT Illustrations and resized all for consistency
* Project Roadmap now listed with Major Headers as Timeline and Sub Headers as Task Category
* Added ChatGPT generated website illustrations
* Added Database Admin skeleton pages for EpiCollect, GitHub, PostgreSQL, Python, etc

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 May</strong></summary>

### SQL Tables

* Added site-level caretaker IDs
* Removed tree-level primary caretakers in favor of site-level defaults
* Added GPS coordinates to Site table for mapping support
* Introduced `tree_primary_caretaker` and `tree_secondary_caretaker` fields
* Enabled fallback caretaker logic in `cam_trees` view

### SQL Views

* Added `gis_map_view` column to `cam_sites`
* Updated `cam_count_next_tree_number_for_planting` to include all CAM orgs
* Default tree numbering now starts at 1 for new orgs
* Moved `gis_map_view` to the first column in `cam_sites` and `cam_trees` views to simplify map selection

### Website Content

* Added an image to the Epicollect5 for Users page
* Migrated Kenster’s offline To-Do list into the website
* Added initial content for “EpiCollect5 for Users”
* Added initial content for “DBeaver Access to SQL”
* Added changelog entries previously stored in Excel and early SQL systems

### Website Infrastructure

* Renamed To-Do Task List page to Project Roadmap
* Created GitHub Pages repository for CAMTREES Database site
* Adopted <a href="https://jekyllrb.com" target="_blank">Jekyll</a> for site generation
* Adopted the <a href="https://just-the-docs.com" target="_blank">Just the Docs</a> theme
* Created initial skeleton pages
* Added version tracking to detect rebuilds
* Created favicons for browser and Apple devices
* Moved images directory into the assets folder
* Improved To-Do list formatting for mobile readability
* Improved To-Do Task List readability using collapsible sections, removing the need for numbering

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 April</strong></summary>

### GitHub

* Created GitHub account (camorgdatabase@gmail.com)
* Added workflow to sync CAMTREES Neon database between accounts

### SQL Tables

* Added two new 2026 sites with associated data
* Removed Waldoboro hub
* Added four `access_` columns to `tree`; updated `cam_trees` and dependent views

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 March</strong></summary>

### SQL Tables

* Added two New Hampshire hubs
* Renamed Augusta hub to Winthrop; added Danforth hub
* Added Eva Butler’s tree, site, and volunteer data

### SQL Views

* Created `missing_data_` views

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 February</strong></summary>

### SQL

* Settled upon using Neon.com to host the CAMTREES Database (PostGreSQL)
* Added Mark McCollough tree data
* Added `camtress_manage_dates` for automated timestamp handling
* Created function for EpiCollect ALL records
* Added `date_created` and `date_updated` fields (initialized to 2026-02-01)

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2026 January</strong></summary>

### SQL

* Settled upon using PostGreSQL as the RDBMS
* Investigate PostGreSQL host platforms

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2025 December</strong></summary>

### SQL

* Research various SQL Relational DataBase Management Systems (RDBMS)
* Brainstormed how to convert Excel system into SQL

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2025 November</strong></summary>

### EpiCollect

* Enabled Rain Event entry by Hub or Site
* Updated “Cam Org – Site” question format

### SQL Tables

* Began migration from Excel to PostgreSQL
* Added Volunteer Interests table

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2025 October</strong></summary>

### EpiCollect

* Simplified GPS record fields
* Added additional GPS/tree-number screens

### Excel

* Enabled WildCAM trees
* Added Lea’s 2025 planting data

</details>

---

<details markdown="1">
<summary markdown="span"><strong>2025 September</strong></summary>

### Excel

* Added watering data from Maggie Lynn's spreadsheet

</details>

---

