---
title: Database Admin Access
layout: default
nav_order: 7
---

<img src="../assets/images/website/staff-meeting.png" alt="CAM Staff Meeting" height="512" width="828">

# {{ page.title }}

There are many database management tools that can be used to access the CAMTREES
PostgreSQL database.

These tools, often called **SQL GUI clients**, provide a graphical interface for viewing
data, running SQL commands, and managing database objects. Similar to email clients,
different users may prefer different tools based on their experience and workflow.

The CAMTREES Database is hosted in the cloud, so these tools connect remotely to the
database rather than storing a copy of the database on the user's computer.

The CAMTREES Database does not require all admins to use the same SQL GUI client. Admins
may choose the tool that best fits their needs.

---

## Desktop Tools

Several SQL GUI clients are available for desktop computers:

- <a href="https://dbeaver.io/download/" target="_blank">DBeaver Community Edition</a>
- <a href="https://www.pgadmin.org" target="_blank">pgAdmin</a>
- <a href="https://tableplus.com/" target="_blank">TablePlus</a>

DBeaver Community Edition is currently the recommended SQL GUI client for CAMTREES for
several reasons:

- It is fully functional and available at no cost.
- It can display the database using either a **Simple** view or an **Advanced** view.
  - The Simple view hides much of the complexity of a PostgreSQL database and is generally
  easier to navigate.
  - The Advanced view provides access to the full database structure.
- It supports PostGIS geographic data, allowing tree and site locations to be displayed on
maps.
- Map features can be labeled using available database fields.
- Selecting a tree or site on the map displays the associated database records.

---

## iPhone and iPad Tools

<a href="https://apps.apple.com/us/app/postgresql-client/id1233662353" target="_blank">DB Compass for PostgreSQL</a>
is available for iPhone and iPad.

DB Compass is a full-featured PostgreSQL management application. It requires a one-time
purchase ($9.99) which can be used on both iPhone and iPad devices. The iPad version
provides an improved experience because of the larger screen size, making database
browsing and record review easier.

---

## Android Phones and Tablets

CAM Database Admins do not currently have experience with Android phones and thus cannot
recommend a specific tool.
