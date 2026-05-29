---
title: ChangeLog
nav_order: 99
---

# {{ page.title }}
_Version: 29.1_

<!-- This content will not appear in the rendered Markdown 
Headers we may use in this ChangeLog page...
## YYYY-MM-DD
##### CAMTREES Database Website
##### EpiCollect Updates
##### Python EpiCollect Import Code
##### Python EpiCollect Image Downloader Code
##### SQL Access
##### SQL Functions
##### SQL Hosting
##### SQL Tables
##### SQL Views
##### GitHub
##### GitHub Actions
##### GitHub Images
-->


## 2026-05-25
##### SQL Views
- Moved the 'gis_map_view' column in the 'cam_sites' and 'cam_trees' SQL views to the
  first column so as to make it easier to select Sites or Trees for viewing on a map

##### CAMTREES Database Website
- Created favicon's for both browsers and Apple specific devices
- Moved the images directory inside the assets directory
- Numbered items in our ToDo list for easier viewing especially on phones


## 2026-05-24
##### CAMTREES Database Website
- Moved the content of Kenster's offline ToDo List into the website's ToDo List page
- Added initial content to the "Epicollect5 for Users" web page
- Added initial content to the "DBeaver Access to SQL" web page


## 2026-05-23
##### CAMTREES Database Website
- Now using [Jekyll](https://jekyllrb.com) to author pages
- Now using [Just the Docs](https://just-the-docs.com) Jekyll template for all pages
- Created empty skeleton pages for the website
- Added a version number to this page so we can detect if GitHub has rebuilt the site


## 2026-05-22
##### SQL Tables
- Site table now has GPS coordinates which allows us to view a Site Map using DBeaver
  and the 'cam_sites_map' view
	- Site's GPS coordinates are obtained from the lowest tree number at the site
- Site table now has two new columns: 'tree_primary_caretaker' and 'tree_secondary_caretaker'
	- These values will be used to replace NULL values for the 'primary_caretaker'
	  or the 'secondary_caretaker' of a tree in the 'cam_trees' view.

## 2026-05-21
- Changed the 'cam_count_next_tree_number_for_planting' view to show all CAM Orgs. If CAM Org doesn't yet have trees, the next tree num will be 1.

## 2026-05-20
##### SQL Views
- cam_sites view will now contain a gis_map_view column which will show the map position of the lowest tree number at the site.

## 2026-05-20
##### SQL Tables
- Add primary_caretaker_id and secondary_caretaker_id to the site table'; remove all primary caretakers from all trees; we will use the site value unless specified for a single tree

## 2026-05-20
##### CAMTREES Database Website
- Created this GitHub Pages repository to house the CAMTREES Database Website

## 2026-04-19
##### SQL Tables
- Update 'tree' table with four new Access_ columns. Update cam_trees view and all other views depending upon cam_trees view

## 2026-04-16
##### SQL Tables
- Deleted 'Waldoboro' Hub

## 2026-04-16
##### GitHub
- Create GitHub account for camorgdatabase@gmail.com

## 2026-04-16
##### GitHub Actions
- Create a GitHub Action to copy the Neon camtrees database from ken.rosenberry@gmail.com's project space into cam.org.database@gmail.com Neon project space

## 2026-04-15
##### SQL Tables
- Added two new 2026 sites with all ancillary info (volunteers, etc)

## 2026/03/27
##### SQL Tables
- Add two New Hampshire Hubs

## 2026-03-19
##### SQL Views
- Created 'missing_data_' views

## 2026-03-19
##### SQL Tables
- Changed 'Augusta' hub to 'Winthrop' and added 'Danforth' hub

## 2026-03-11
##### SQL Tables
- Added Eva Butler's tree, site, and volunteer data

## 2026-02-23
##### SQL Functions
- Create function to process EpiCollect ALL Record_Type data

## 2026-02-23
##### SQL Tables
- Add date_created and date_updated columns to most tables; set values to '2026-02-01' for all existing records

## 2026-02-22
##### SQL Functions
- Add camtrees_manage_dates function so some tables can have date_created and date_updated fields

## 2026/02/18
##### SQL Tables
- Added Mark McCollough tree data

## 2025/11/15
##### SQL Tables
- Add Volunteers Interests Worksheet and Table.

## 2025/11/11
##### EpiCollect Updates
- Allow volunteer to enter Rain Event data by Hub as well as by Site

## 2025/11/06
##### EpiCollect Updates
- Updates for using new EpiCollect "Cam Org - Site" question (includes major VBA code changes as well)

## 2025-11-01
##### SQL Tables
- Begin conversion of MS Excel database to PostgreSQL

## 2025/10/12
##### EpiCollect Updates
- Changes so EpiCollect Record Type GPS will only prompt for Tree Number, GPS Location, and Notes - required a 3rd EpiCollect Tree Number and GPS Location screensof course, changes to the Excel VBA Import Code

## 2025/10/04
##### SQL Tables
- Updates to allow for WildCAM trees

## 2025/10/04
##### SQL Tables
- Add Lea's data for 2025 plantings

## 2025/09/06
##### SQL Tables
- Add Watering data from Maggie Lynn's Excel table
