---
title: DBeaver Access to SQL
parent: Info for CAM Staff
---

# {{ page.title }}

There are many Database Management Tools which could be used to access the CAMTREES
PostgreSQL Database:
- DBeaver
- pgAdmin
- Postico
- TablePlus

Kenster's preferred program is DBeaver because...
- There is a full functioning FREE Community version of DBeaver.
- DBeaver can be set to show either a Simple or Advanced view of the database.
  Most often the Simple view is desirable as it removes much of the complexity inherent
  to SQL databases.
- Using GPS Coordinates translated into PostGIS data, DBeaver can display Tree
  and Site locations on a Map. Individual items on the map can have whatever labels
  the user wishes to see. Clicking on map items (like a tree) will show all the data
  associated with either the tree or the site clicked upon.

####Things to demo when showing CAM Folks how to use DBeaver
- Download the [DBeaver Community version](https://dbeaver.io/download/)
- We need to create a 'connection' to connect to the CAMTREES Database. We need to specify
  the following fields all of which need to be kept private so they are NOT listed here.
	```
		PGHOST     : [private]
		PGDATABASE : [private]
		PGUSER     : [private]
		PGPASSWORD : [private]
	```

- DBeaver Walkthrough
	- Using the ER diagram to see what's in each table and the relationship between tables
	- Difference between Tables and Views
	- Explaining the 'v_pg...' views (most are only interesting to a Database Admin)
	- Viewing records
	- Filtering rows by column values
	- Rearranging, showing, hiding, and sorting columns
	- Viewing a single record with the TAB key
	- How to view Trees and Sites (with labels) on a map
		- Perhaps particularly nice to show latest health as a label?
	- Dragging columns into the 'Groups' panel for FREQ and CROSSTAB tables
	- Helping to fill in missing data using the 'missing_data' views

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 





