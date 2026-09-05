---
title: Database Tables
layout: default
nav_order: 3
---

# {{ page.title }}

The database tables in this section are now in *live production* mode. Tables are
refreshed each morning, usually between the hours of 3 and 6am. 

### Available Tables

- **CAM Hubs** – Hubs with their Captain and Lieutenant
- **CAM Orgs** – CAM Organizations with the Contact person for each
- **CAM Sites** – Site info where trees have been planted
- **CAM Trees** – Master list of all trees planted by CAM
- **Parent Trees** – Trees used as Mother and Father trees 
- **Site Visit** – A subset of the columns in the CAM Trees table useful to print and
carry with you on a site visit
- **Sites in Hubs** – To which Hub each of the Sites 'belongs'

Within each table, you can:

- Use the **"Search all ..."** box to filter records across all fields.
- Use the **"Filter ..."** box under each column heading to further narrow results.
- Click a **Column Heading** to sort the table in ascending order by the values in that
column; click the column heading again to sort in descending order.
- **Refresh the webpage** to clear all filters and search terms.

You can also:
- Click the **"Print filtered ..."** button to print the table records. Most tables will print
best using landscape mode.
- Click the **"Export as CSV"** button to export the table as a CSV file. Once downloaded you
can import the CSV file into MS Excel to create professional looking charts. Or you might
import the CSV file into the R application to perform statistical analysis.
- Click the **"Map filtered ..."** button on the CAM Hubs, CAM Sites, and CAM Trees tables
to open a pop-up window showing records on a street, satellite, or topographic map.
Each map has clickable controls:
	- The "plus and minus icons" in the upper left will zoom the map in and out.
	- The "target" control, also in the upper left, will center the map on your location.
	  Make sure you "allow" the web page access to your location when asked.
	- The "layers" icon in the upper right will allow you to select the type of map: Street,
	  Satellite, Topographic, or Satellite + Labels.
	- The "Hub Areas" checkbox within the "layers" icon will toggle on/off the hub boundaries.
	- Only on the CAM Trees Map there is a "Color pins by" control in the lower left of
	  the map. You can select to either color pins by the "Tree Health" or by the "Nuts
	  Present" column for each tree. Selecting either option will zoom in the map as
	  far as possible to show all the appropriate trees based upon the selection.
	  Selecting "Nuts Present" will hide all trees except those that have either "some"
	  or "many" nuts.
	- Note: The CAM Trees Map has what looks like a control in the lower right of map.
	  This is **not a control!** Rather, it is a legend showing what the pin colors on the
	  map represent.
	- You can click each pin on the map and a small popup window will appear showing just
	  a couple of identifying columns for the pin. Within that small popup will be a "View
	  full record" button. Clicking that will bring up another popup window within the map
	  showing all the columns for that particular pin clicked. It will make immediate
	  sense once you give it a try.
	- To pan the map North, South, East, or West, click-and-drag the map.

Tables will show 1000 records per page. All tables currently have fewer than 500 records;
so only one page for now.


{: .note }
For security, this website will never connect directly to the CAMTREES Database. Rather, a
secure Python script will (soon!) regenerate the necessary tables each night.