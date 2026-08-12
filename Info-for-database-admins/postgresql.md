---
title: PostgreSQL
layout: default
parent: Info for Database Admins
---

<center>
<table border="0" cellpadding="10">
  <tr>
    <td valign="top">
		<img src="../assets/images/website/puzzle-piece-postgresql.png" alt="A PostgreSQL jigsaw puzzle piece" height="418">
    </td>
    <td valign="center">
      <center><h2>CAMTREES<br>Database<br>and<br>PostgreSQL</h2></center>
    </td>
  </tr>
</table>
</center>


# {{ page.title }}

We store the CAMTREES Database in **PostgreSQL**, a powerful, open-source (free)
relational database management system (RDBMS). PostgreSQL is well known for its
reliability, standards compliance, and extensibility, making it an excellent choice for
applications that require accurate, long-term data management.

Although PostgreSQL itself is free to use, the database must be hosted on a server that is
accessible over the Internet. Because Chestnuts Across Maine (CAM) is a nonprofit
organization with limited financial resources, we wanted a hosting solution that was
either free or very affordable.

## Neon.com

The CAMTREES Database is hosted by <a href="https://neon.com" target="_blank">Neon</a>, a
cloud-based PostgreSQL hosting service.

Neon uses a usage-based pricing model with no monthly minimum charge and offers a generous
Free Tier. The Free Tier is currently more than sufficient for the size and activity level
of the CAMTREES Database.

If our storage or usage requirements increase in the future, upgrading to a paid plan is
straightforward, with expected hosting costs remaining relatively low – likely in the range
of $5 to $10 per month.

## CAMTREES Database Schema

### Entity Relationship Diagram

<a href="../assets/images/website/entity-relationship-diagram.png" target="_blank"><img src="../assets/images/website/entity-relationship-diagram.png" alt="CAMTREES SQL Entity Relationship Diagram"></a>

*Click the image to view the full-size version in a new browser tab.*

### SQL Tables

The color of the SQL tables' headers in the ER Diagram indicates the type and purpose of the tables.

<details>
<summary><strong>Green Tables — The four main tables containing tree related data</strong></summary>

<ul>
	<li><strong>tree</strong> — All the CAM planted trees or Wild trees under observation</li>
	<li><strong>tree_photo</strong> — Photos of the trees. The actual photos are stored in EpiCollect. We compute the URL necessary to view the tree. NOTE: You MUST BE LOGGED INTO EpiCOllect to view the photos.</li>
	<li><strong>tree_care_action</strong> — Care actions performed on trees</li>
	<li><strong>tree_health_assessment</strong> — Tree measurements and observations to access the health of the tree</li>
</ul>

</details>


<details>
<summary><strong>Cyan Tables — Organizational tables</strong></summary>

These tables are also Lookup Tables

<ul>
	<li><strong>hub</strong> — Hub regions as defined by Eva Butler</li>
	<li><strong>organization</strong> — Cam Organizations</li>
	<li><strong>site</strong> — Sites where trees are planted</li>
	<li><strong>volunteer</strong> — Volunteers. All persons referenced in any table will appear in this table.</li>
</ul>

</details>


<details>
<summary><strong>Yellow Tables — SQL join tables</strong></summary>

<ul>
	<li><strong>site_hub</strong> — Sites contained in each hub</li>
	<li><strong>volunteer_interest</strong> — Volunteer's interests. Like watering trees or being available for special events.</li>
	<li><strong>volunteer_phone</strong> — Phone numbers at which volunteers can be reached</li>
</ul>

</details>


<details>
<summary><strong>Purple Tables — Lookup tables that link to a other tables via a foreign key relationship</strong></summary>

<ul>
	<li><strong>epicollect_record_type</strong> — EpiCollect record types (path the volunteer takes trhough the iPhone app)</li>
	<li><strong>phone_type</strong> — Phone Type (home, cell, work, etc)</li>
	<li><strong>state</strong> — State codes plus Washing D.C.</li>
	<li><strong>town</strong> — All towns in Maine with a few towns from other states</li>
	<li><strong>tree_access_level_type</strong> — Ease of access for trees</li>
	<li><strong>tree_access_method_type</strong> — Access method to pollinate or harves trees</li>
	<li><strong>tree_access_path_type</strong> — Access path to a tree</li>
	<li><strong>tree_care_action_type</strong> — Care actions (water, weed, fertilize, prune)</li>
	<li><strong>tree_form_type</strong> — Tree shape (straight, bushy)</li>
	<li><strong>tree_health_nuts_type</strong> — Nut quantity produced by the tree</li>
	<li><strong>tree_health_type</strong> — Tree health (good, poor, dead)</li>
	<li><strong>tree_parent_type</strong> — Mother and Father Trees</li>
	<li><strong>tree_planting_method_type</strong> — Tube (if any) used to plant the tree</li>
	<li><strong>volunteer_interest_type</strong> — Volunteer interests</li>
	<li><strong>volunteer_status_type</strong> — Volunteer status (active, inactive, etc)</li>
</ul>

</details>


<details>
<summary><strong>Orange Tables — Independent tables not linked to any other tables</strong></summary>

<ul>
	<li><strong>docs_web_link</strong> — Helpful web links</li>
	<li><strong>epicollect_import_date</strong> — Epicollect Import Dates from running Python programs</li>
	<li><strong>spatial_ref_sys</strong> — A PostGIS table used for plotting trees on a map</li>
	<li><strong>z_test_url</strong> — Test table for Kenster to experiment with URL's and their clickability</li>
</ul>

</details>


### SQL Views

<details>
<summary><strong>'Earliest' and 'Latest' Views</strong></summary>

<ul>
	<li><strong>cam_tree_latest_health</strong> - Show latest tree_health</li>
	<li><strong>cam_tree_latest_height</strong> - Show latest tree_height</li>
	<li><strong>cam_tree_latest_water</strong> - Show most recent date trees have been watered</li>
	<li><strong>cam_tree_photos_earliest_photos</strong> - Show all photos from the first date on which a tree had any photos taken</li>
	<li><strong>cam_tree_photos_latest_photos</strong> - Show all photos from the latest date on which a tree had any photos taken</li>
</ul>

</details>


<details>
<summary><strong>'CAM' Views - Views for which CAM Staff will be most interested</strong></summary>

<ul>
	<li><strong>cam_hubs</strong> - Hub regions as defined by Eva Butler</li>
	<li><strong>cam_organizations</strong> - Cam Organizations</li>
	<li><strong>cam_sites</strong> - Sites where trees are planted</li>
	<li><strong>cam_sites_hubs</strong> - Sites contained in each hub</li>
	<li><strong>cam_towns_with_state_name</strong> - All towns in Maine with a few towns from other states</li>
	<li><strong>cam_tree_care_action</strong> - Care actions performed on trees</li>
	<li><strong>cam_tree_health_assessment</strong> - Tree size and health measurements</li>
	<li><strong>cam_tree_photos</strong> - Photos of the trees. The actual photos are stored in EpiCollect. We compute the URL necessary to view the tree. NOTE: You MUST BE LOGGED INTO EpiCOllect to view the photos.</li>
	<li><strong>cam_tree_photos_with_tags</strong> - Tree photos showing a closeup of the tree's tag</li>
	<li><strong>cam_tree_photos_without_tags</strong> - Tree photos excluding photos of the tree's tags</li>
	<li><strong>cam_trees</strong> - CAM planted trees or Wild trees under observation</li>
	<li><strong>cam_volunteer_interests</strong> - Volunteer's interests. Like watering trees or being available for special events.</li>
	<li><strong>cam_volunteer_phone_numbers</strong> - Phone numbers at which volunteers can be reached</li>
	<li><strong>cam_volunteers</strong> - Volunteers. All persons referenced in any table must appear in this table.</li>
</ul>

</details>


<details>
<summary><strong>'Count' Views - Frequency counts of various values</strong></summary>

<ul>
	<li><strong>data_count_next_tree_number_for_planting</strong> - Show the NEXT CamOrg tree number to be used when planting new trees</li>
	<li><strong>data_count_tree_care_action_by_volunteer</strong> - Frequency count of how many times volunteers have attended to trees by type of care_action</li>
	<li><strong>data_count_trees_by_health</strong> - Frequency count of trees by the tree health</li>
	<li><strong>data_count_trees_by_primary_caretaker</strong> - Frequency count of how many trees each primary caretaker is responsible for</li>
	<li><strong>data_count_trees_by_site</strong> - Frequency count of how many trees are at each site</li>
</ul>

</details>


<details>
<summary><strong>'Crosstab' Views - Statistical tables that display the relationship between two or more categorical variable</strong></summary>

<ul>
	<li><strong>data_crosstab_care_action_by_record_type</strong> - Crosstab of Tree Care Action BY EpiCollect Record Type</li>
	<li><strong>data_crosstab_site_by_hub</strong> - Crosstab of Site BY hub</li>
	<li><strong>data_crosstab_tree_planting_method_by_wire_fence</strong> - Crosstab of Tree Planting Method BY Wire Fence</li>
</ul>

</details>


<details>
<summary><strong>'Distance' Views - Shows the distance between trees</strong></summary>

<ul>
	<li><strong>data_distance_between_all_trees</strong> - Show tree to tree distance (in meters and miles) for all trees</li>
	<li><strong>data_distance_between_trees_at_same_site</strong> - Show tree to tree distance (in meters and feet) but only for trees at the same site</li>
	<li><strong>data_distance_trees_within_15_meters_of_each_other</strong> - Show tree to tree distance (in meters and feet) for all trees within 15 meters of each other</li>
</ul>

</details>


<details>
<summary><strong>'Duplicate' Views - Duplicate records in tables</strong></summary>

<ul>
	<li><strong>data_duplicate_tree_care_actions</strong> - Duplicate tree_care_action records (if any)</li>
	<li><strong>data_duplicate_tree_health_assessments</strong> - Duplicate tree_health_assessments records (if any)</li>
</ul>

</details>


<details>
<summary><strong>'Error' Views - Tables with missing data</strong></summary>

<ul>
	<li><strong>data_error_hubs_with_no_captain</strong> - Hubs with no captain (If any)</li>
	<li><strong>data_error_hubs_with_no_sites</strong> - Hubs not linked to any sites</li>
	<li><strong>data_error_sites_in_multiple_hubs</strong> - Sites in more than one hub</li>
	<li><strong>data_error_sites_not_in_any_hub</strong> - Sites not linked to any hubs</li>
	<li><strong>data_error_sites_with_no_contact</strong> - Sites with no contact person</li>
	<li><strong>data_error_sites_with_no_primary_caretaker</strong> - Sites with no primary caretaker</li>
	<li><strong>data_error_sites_with_no_site_url</strong> - Sites with no URL</li>
	<li><strong>data_error_sites_with_no_trees</strong> - Sites with no trees</li>
	<li><strong>data_error_trees_with_gps_approximated</strong> - Trees with estimated longitude and latitude data</li>
	<li><strong>data_error_trees_with_no_elevation</strong> - Trees with missing elevation</li>
	<li><strong>data_error_trees_with_no_gps</strong> - Trees with missing longitude and latitude data</li>
	<li><strong>data_error_trees_with_no_mother_or_father</strong> - Trees with missing parents</li>
	<li><strong>data_error_trees_with_no_primary_caretaker</strong> - Trees with no primary caretaker</li>
	<li><strong>data_error_trees_with_no_tag_info</strong> - Trees with no tag_info</li>
	<li><strong>data_error_trees_with_no_tag_photo</strong> - Trees with missing tag photo</li>
	<li><strong>data_error_trees_with_planting_method_unknown</strong> - Trees with unknown planting method</li>
	<li><strong>data_error_volunteers_with_no_email</strong> - Volunteers with temporary (non-valid) email addresses</li>
	<li><strong>data_error_volunteers_with_no_hometown</strong> - Volunteers with no home town</li>
	<li><strong>data_error_volunteers_with_no_phone</strong> - Volunteers with no known phone number</li>
</ul>

</details>


<details>
<summary><strong>'Export' Views - For exporting data to EpiCollect or Google Maps</strong></summary>

<ul>
	<li><strong>data_export_epicollect_tree_parent_type</strong> - Export tree_parent_type as CSV file to load into EpiCollect CAM Tree Maintenance form</li>
	<li><strong>data_export_epicollect_volunteer_email</strong> - Export volunteer_email as CSV file to load into EpiCollect CAM Tree Maintenance form</li>
	<li><strong>data_export_google_map_data</strong> - Export Google Map Data as CSV file and load into Google Maps</li>
</ul>

</details>


<details>
<summary><strong>'Site Visit' Views - Useful for printing prior to a Site visit</strong></summary>

<ul>
	<li><strong>data_site_visit</strong> - Show data useful to have printed for when a volunteer performs a site visit</li>
</ul>

</details>


<details>
<summary><strong>'Kenster' Views - Database Admin views</strong></summary>

<ul>
	<li><strong>user_hkr_tree_photos_for_tag_info_editing</strong> - Tree photos with our EpiCollect link and tag_info for easy Kenster editing</li>
</ul>

</details>


### SQL Functions

<details>
<summary><strong>'Add' Functions - Called from Python to insert data into SQL tables</strong></summary>

<ul>
	<li><strong>camtrees_add_care_action</strong> - Add a tree_care_action from an EpiCollect 'ONE', 'ALL', or 'RAIN' record</li>
	<li><strong>camtrees_add_health_assessment</strong> - Add a new tree_health_assessment from an EpiCollect ONE record</li>
	<li><strong>camtrees_add_tree_initial_health</strong> - Add a new initial tree_health_assessment from EpiCollect 'PLANT' record</li>
	<li><strong>camtrees_add_tree_photo</strong> - Add a new tree photo</li>
	<li><strong>camtrees_add_tree</strong> - Add a new tree</li>
</ul>

</details>


<details>
<summary><strong>'Count' Functions - Used by Views to count records in Tables and Views</strong></summary>

<ul>
	<li><strong>camtrees_count_table_rows</strong> - Assists with counting rows in Tables</li>
	<li><strong>camtrees_count_view_rows</strong> - Assists with counting rows in Views</li>
</ul>

</details>


<details>
<summary><strong>'Distance' Functions - Used by views to calculate tree distances</strong></summary>

<ul>
	<li><strong>camtrees_get_distance_to_closest_wildcam_tree</strong> - Get the distance (in meters) to the closest WildCAM tree</li>
</ul>

</details>


<details>
<summary><strong>'Date' Functions - Add date_created and date_updated values to tables</strong></summary>

<ul>
	<li><strong>camtrees_manage_dates</strong> - Add a date_created on INSERT and date_updated on UPDATE</li>
</ul>

</details>


<details>
<summary><strong>'Interrogate' Functions - Called from Python to test certain conditions</strong></summary>

<ul>
	<li><strong>camtrees_tree_exists</strong> - Determine if a tree already exists in the 'tree' table</li>
	<li><strong>camtrees_tree_gps_locked</strong> - Get tree's gps_locked value</li>
</ul>

</details>


<details>
<summary><strong>'Update' Functions - Called from Python to Update tree column values</strong></summary>

<ul>
	<li><strong>camtrees_update_access_method</strong> - Update a tree's access_method</li>
	<li><strong>camtrees_update_tree_form</strong> - Update a tree's form</li>
	<li><strong>camtrees_update_tree_gps</strong> - Update a tree's GPS data. Append new access_note data to existing access_note</li>
</ul>

</details>


<details>
<summary><strong>Testing</strong></summary>

* camtrees_update_access_method - Update a tree's access_method
* camtrees_update_tree_form - Update a tree's form
* camtrees_update_tree_gps - Update a tree's GPS data. Append new access_note data to existing access_note

</details>