---
title: DBeaver Access to SQL
layout: default
parent: Info for Database Users 
---

# {{ page.title }}

DBeaver is the recommended desktop GUI Database Administrator Tool for both Mac and
Windows users. The Community version is free and totally functional. This page will guide
the Database Administrator when she is helping CAM Staff to install, configure, and 
navigate the DBeaver application.

#### Topics to Demonstrate When Introducing DBeaver

1. Download the
<a href="https://dbeaver.io/download/" target="_blank">DBeaver Community Edition</a>.

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
