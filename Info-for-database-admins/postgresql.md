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

- **tree** — All the CAM planted trees or Wild trees under observation
- **tree_photo_** — Photos of the trees. The actual photos are stored in EpiCollect. We compute the URL necessary to view the tree. NOTE: You MUST BE LOGGED INTO EpiCOllect to view the photos.
- **tree_care_action** — Care actions performed on trees
- **tree_health_assessment** — Tree measurements and observations to access the health of the tree
</details>

<details>
<summary><strong>Cyan Tables — Organizational tables</strong></summary>

- **hub** — Hub regions as defined by Eva Butler
- **organization** — Cam Organizations
- **site** — Sites where trees are planted
- **volunteer** — Volunteers. All persons referenced in any table will appear in this table.
</details>

<details>
<summary><strong>Yellow Tables — SQL join tables</strong></summary>

- **site_hub** — Sites contained in each hub
- **volunteer_interest** — Volunteer's interests. Like watering trees or being available for special events.
- **volunteer_phone** — Phone numbers at which volunteers can be reached

</details>

<details>
<summary><strong>Purple Tables — Lookup tables that link to a other tables via a foreign key relationship</strong></summary>

- **epicollect_record_type** — EpiCollect record types (path the volunteer takes trhough the iPhone app)
- **phone_type** — Phone Type (home, cell, work, etc)
- **state** — State codes plus Washing D.C.
- **town** — All towns in Maine with a few towns from other states
- **tree_access_level_type** — Ease of access for trees
- **tree_access_method_type** — Access method to pollinate or harves trees
- **tree_access_path_type** — Access path to a tree
- **tree_care_action_type** — Care actions (water, weed, fertilize, prune)
- **tree_form_type** — Tree shape (straight, bushy)
- **tree_health_nuts_type** — Nut quantity produced by the tree
- **tree_health_type** — Tree health (good, poor, dead)
- **tree_parent_type** — Mother and Father Trees
- **tree_planting_method_type** — Tube (if any) used to plant the tree
- **volunteer_interest_type** — Volunteer interests
- **volunteer_status_type** — Volunteer status (active, inactive, etc)
</details>

<details>
<summary><strong>Orange Tables — Independent tables not linked to any other tables</strong></summary>

- **docs_web_link** — Helpful web links
- **epicollect_import_date** — Epicollect Import Dates from running Python programs
- **spatial_ref_sys** — A PostGIS table used for plotting trees on a map
- **z_test_url** — Test table for Kenster to experiment with URL's and their clickability
</details>
