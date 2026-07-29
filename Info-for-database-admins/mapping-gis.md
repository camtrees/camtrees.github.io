---
title: Mapping / GIS
layout: default
parent: Info for Database Admins
---

<center>
<table border="0" cellpadding="10">
  <tr>
    <td valign="top">
		<img src="../assets/images/website/puzzle-piece-mapping-gis.png" alt="A Mapping / GIS jigsaw puzzle piece" height="418">
    </td>
    <td valign="center">
      <center><h2>CAMTREES<br>Database<br>and<br>Mapping/GIS</h2></center>
    </td>
  </tr>
</table>
</center>


# {{ page.title }}

## Viewing Tree Locations on a Map

We currently have two methods to view tree locations on a map:

* Using a custom Google My Maps - Viewable by anyone

* Using DBeaver (our recommended desktop GUI Database Tool) - Viewable by a limited
number of CAM Staff and Volunteers

### Using a Custom Google My Maps

1. First we create an SQL View that has each tree's Longitude and Latitude. Google will use
those data to place each tree's pin on the map. When a user clicks a tree's pin an info
card opens. This card displays the custom title, description, and any additional info (SQL
table fields) added by the map creator.

1. Next, we export the data from the view to a local CSV file on our personal computer.

1. Finally, we import the local CSV file into our custom Google map, replacing all the
existing data for our map.

You can view the
<a href="https://www.google.com/maps/d/edit?mid=1BnudQOUMWyFeMCpp1HV90hQPCFrWSx0&ll=44.44387186421211%2C-70.31670421000621&z=9" target="_blank">CAM Tree Locations</a>
Google Map page. It shows the locations of all CAM Chestnut Trees planted to date.


### Using DBeaver

1. First we install the PostGIS PostgreSQL extension into the CAMTREES database. This
extension adds new data types to our database. One of which allows us to plot trees on a
map.

1. Then, for each tree, we calculate a geography point. That is a point representing the
tree's position on the earth's surface.

1. Finally, from within an SQL View of trees, we select one or more geography points. That
will plot the selected points (trees) on a map shown in DBeaver's 'Value' panel.

### Here is a DBeaver Screenshot Showing a Map of Two Tree Locations

There are two 'POINT's (rows 95 and 100) selected, thus the map will show only those two
trees. Click the map image to see the full sized image in a new browser tab.

<a href="../assets/images/website/dbeaver_tree_map.png" target="_blank"><img src="../assets/images/website/dbeaver_tree_map.png" alt="DBeaver map showing two trees"></a>

### The SQL Code Which Creates a Geography Point for Each Tree

Each tree's geography point is calculated using the tree's longitude and latitude at the
time a tree is added to the 'tree' table.

Here is an incomplete portion of the SQL code that creates the 'tree' table:

```
1 CREATE TABLE tree (
2     id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
3     longitude float8,
4     latitude  float8,
5     geog      geography(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography) STORED,
6     . etc
7     . etc
8     . etc
9     );
```

### Key Parts of the SQL code (line 5) that creates the geography point

**geog:** is the name of the column in the 'tree' table. Just as 'id', 'longitude' and
'latitude' are also names of other columns.

**geography(Point, 4326):** Specifies a spherical coordinate data type for a point using
GPS coordinates (WGS 84, SRID 4326).

**GENERATED ALWAYS AS (...) STORED:** Tells PostgreSQL to compute the value automatically
and save it on disk whenever longitude or latitude change.

**ST_SetSRID(ST_MakePoint(longitude, latitude), 4326):** Creates a raw point from the
coordinate columns (longitude and latitude) and tags it with the correct GPS system ID
(4326).

**::geography:** Casts that raw point into the geography type so distances are measured in
real-world meters instead of flat grid units.

### Breakdown of Components

**geography vs geometry:** The geography type calculates distances over a 3D sphere (the
Earth), which gives true measurements in meters. The geometry type (which we are not
using) treats coordinates like a flat piece of paper.

**4326 (SRID):** The standard ID for WGS 84 GPS coordinates, where coordinates are
recorded in degrees of longitude and latitude.

**STORED:** Means the database actually writes and keeps this point saved on disk. This
takes a tiny bit of extra disk space, but makes searches and maps run much faster because
it does not need to re-calculate the point every time you look at it.

