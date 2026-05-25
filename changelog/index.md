---
title: ChangeLog
nav_order: 99
---

# {{ page.title }}
_Version: 25.5_

{% comment %}
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
{% endcomment %}

## 2026-05-25
##### CAMTREES Database Website
- Create favicon.ico file
- Move images directory inside the assets directory
- Number items in our ToDo list for easier viewing especially on phones
- Moved the 'gis_map_view' columns in the 'cam_sites' and 'cam_trees' SQL views to the
  first column to ease selection of sites or trees for map viewing

## 2026-05-24
##### CAMTREES Database Website
- Kenster moved the content of his offline ToDo List into the website ToDo list 
- Added initial content to the "Epicollect5 for Users" web page
- Added initial content to the "DBeaver Access to SQL" web page

## 2026-05-23
##### CAMTREES Database Website
- Using [Jekyll](https://jekyllrb.com) to author pages
- Using [Just the Docs](https://just-the-docs.com) Jekyll template for all pages
- Created empty skeleton pages for the website
- Added a version number to this page so we can detect if GitHub has rebuilt the site

## 2026-05-22
##### SQL Tables
- Site table now has GPS coordinates which allows us to view a Site Map using DBeaver
  and the 'cam_sites_map' view
	- Site's GPS coordinates are obtained from the lowest tree number at the site
- Site table has two new columns: 'tree_primary_caretaker' and 'tree_secondary_caretaker'.
	- These values will be used to replace NULL values for the 'primary_caretaker'
	  or the 'secondary_caretaker' of a tree in the 'cam_trees' view.

## 2026-05-20
##### CAMTREES Database Website
- Create GitHub Pages repository to house this CAMTREES Database Website
