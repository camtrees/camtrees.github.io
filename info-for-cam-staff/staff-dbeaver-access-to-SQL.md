---
title: DBeaver Access to SQL
layout: default
parent: Information for CAM 
---

# {{ page.title }}

There are many database management tools that can be used to access the CAMTREES PostgreSQL database, including:

* DBeaver
* pgAdmin
* Postico
* TablePlus

DBeaver is currently the preferred database management tool for the CAMTREES project for several reasons:

* A fully functional and free Community Edition is available.
* DBeaver can be configured to display either a Simple or Advanced view of the database.
  In most cases, the Simple view is preferable because it hides much of the complexity
  inherent in SQL databases.
* Using GPS coordinates stored as PostGIS data, DBeaver can display tree and site
  locations on a map. Individual map features can be labeled with any available data.
  Selecting a tree or site on the map displays the associated database records.

#### Topics to Demonstrate When Introducing DBeaver

1. Download the [DBeaver Community Edition](https://dbeaver.io/download/).

2. Create a database connection to the CAMTREES database. The following connection parameters are required and should be kept private:

   ```text
   PGHOST     : [private]
   PGDATABASE : [private]
   PGUSER     : [private]
   PGPASSWORD : [private]
   ```

3. DBeaver walkthrough:
	* Using the Entity Relationship (ER) diagram to understand the database structure and relationships between tables.
	* Understanding the difference between tables and views.
	* Explaining the `v_pg...` views (most are primarily of interest to database administrators).
	* Viewing records.
	* Filtering rows based on column values.
	* Rearranging, showing, hiding, and sorting columns.
	* Viewing a single record using the Tab key.
	* Displaying trees and sites on a map, including custom labels.
		* Consider using the latest health status as a map label.
	* Creating frequency and cross-tabulation summaries by dragging columns into the **Groups** panel.
	* Using the `missing_data` views to identify and help fill gaps in the dataset.
