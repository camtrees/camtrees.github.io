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

### SQL Table Descriptions by table type

The color of the SQL table headers indicates the type and purpose of the tables.

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
