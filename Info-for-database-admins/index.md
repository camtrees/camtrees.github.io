---
title: Info for Database Admins
layout: default
nav_order: 6
---

<img src="../assets/images/website/jigsaw-puzzle.png" alt="Jigsaw puzzle showing cloud services used in the support of the CAMTREES Database Project" height="512" width="828">

# {{ page.title }}

As pictured in the jigsaw puzle above, many cloud services come together to form the
CAMTREES Database technology ecosystem.

* EpiCollect5
	* Used by volunteers to collect tree data while in the field
	* Also used by Hub Captains to record rain events
* GitHub
	* GitHub Actions allows for the automation of a nightly backup of the CAMTREES Database
	* GitHub Pages hosts the CAMTREES Database website (the one your currently viewing)
* PostgreSQL
	* Neon.com hosts the CAMTREES (PostgreSQL) Database
* Python
	* PyCharm IDE allows us to run programs to import EpiCollect data into our CAMTREES Database
* Web Server
	* GitHub Pages hosts the CAMTREES Database website (the one your currently viewing)
* Google Services
	* Gmail provides the shared email address used to log into all the other cloud services listed here
	* Google Groups allows for collaboration through a single shared email address
	* Google My Maps allows us to create a custom map showing CAM Tree Locations across Maine
* Mapping / GIS
	* PostGIS extends PostgreSQL by adding support for showing data on maps, as well as 
	  querying geospatial data
	* Google My Maps allows us to create a publicly available map showing CAM Tree Locations across Maine
	* DBeaver allows viewing selected tree locations on a map within an SQL GUI client

More detailed information on each of these cloud services is provided in the pages under
the "Info for Database Admins" hierarchy.

