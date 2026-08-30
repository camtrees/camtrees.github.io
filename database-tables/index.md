---
title: Database Tables
layout: default
nav_order: 3
---

# {{ page.title }}

The database tables in this section are currently under development. All data shown
reflects a snapshot taken on August 30, 2026. These tables will transition to live
production status once nightly data refreshes are implemented. (Coming soon!)

Within each table, you can:

- Use the **"Search all ..."** box to filter records across all fields.
- Use the **"Filter ..."** box under each column heading to further narrow results.
- Click a **Column Heading** to sort it in ascending order; click it again to sort in descending order.
- **Refresh the webpage** to clear all filters and search terms.

You can also:
- Click the **"Print filtered ..."** button to print the table records. Most tables will print
best using landscape mode.
- Click the **"Export as CSV"** button to export the table as a CSV file. Once downloaded you
can import the CSV file into MS Excel to create professional looking charts. Or you might
import the CSV file into the R application to perform statistical analysis.
- Click the **"Map filtered ..."** button on the CAM Hubs, CAM Sites, and CAM Trees tables
to open a pop-up window showing records on a street, satellite, or topographic map. Click
the map controls on each map and you should be able to easily discern what each one does.

Tables will show 1000 records per page. All tables currently have fewer than 500 records;
so only one page for now.


{: .note }
For security, this website will never connect directly to the CAMTREES Database. Rather, a
secure Python script will (soon!) regenerate the necessary tables each night.