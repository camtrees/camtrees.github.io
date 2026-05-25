---
title: ChangeLog
nav_order: 99
---

# {{ page.title }}
_Version: 25.9_

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


## 2026-05-20
##### CAMTREES Database Website
- Created this GitHub Pages repository to house the CAMTREES Database Website
