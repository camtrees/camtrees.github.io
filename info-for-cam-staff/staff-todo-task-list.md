---
title: ToDo Task List
parent: Info for CAM Staff
---

# {{ page.title }}

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

## EpiCollect 7

#### Later (Perhaps a good or next Winter project)
<details markdown="1">
<summary markdown="span">1. Use GitHub as a long term photo repository instead of EpiCollect</summary>

	- Why do this? Because now, a user must be signed into EpiCollect to see
	  the photos. Furthermore, since the EpiCollect project isn't public, access to
	  the photos outside of a browser won't work.
	- This will require a Python program to download ALL existing photos and thumbnails.
	- This will also require a mod to our Python Import code so that photos are
	  downloaded each time Tree Maintenance data is imported
	- Python code rewrites will be tricky if the Python code is stored as a GitHub action.
	  This is due to GitHub Actions not having direct write access into a repository.
</details>

<p></p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

## SQL

#### In Progress
<details>
<summary>1. Add additional 'missing_data' views</summary>

	- missing_data_trees_with_no_mother_or_father
</details>

<details>
<summary>1. Work with CAM Staff to complete as much of the 'missing data' as possible.</summary>

	- Go through all the 'missing_data' views in SQL and try to fill in as much
	  of the missing data as possible.
</details>

#### Soon
<details>
<summary>1. Allow CAMOrgs, and Sites to have multiple (as many as desired) contact persons.</summary>

	- Do we need (I think we do) to have a 'contact_comment' field for each CAMorg and
	  Site contact? For example:
		- Say Mark McCollough is the contact for the Fort Point State Park. But he is
		  away for some time.
		- The comment might say: Mark is in Antarctica for the next 3 years so, until
		  May of 2029, we should reach out to other Fort Point State Park contacts.
	- Once that capability, here is some data that needs to be added...
	- An additional contact for the 'Meddybemps Lake Land Trust' is:
		- Brittany Mauricette
	- Additional contacts for the 'Maine Coast Heritage Trust' may be:
		- Andrew Deci
		- Emily Marshall
	- Should verify these (and every other contact) with Eva
</details>

1. Show CAM folks how to access CAMTREES SQL Database using DBeaver
	- Document details in a separate website page

1. Document how to add...
<details>
<summary>1. A new CAMorg</summary>

</details>

		- Code: The CAMorg abbeviation
		- Name: The CAMorg name
		- Contact Partner Person(s): The Volunteer Name
<details>
<summary>XXXXX</summary>

</details>
	1. A new Site
		- Name: The Site name
		- Camorg: The CAMorg that the Site is associated with
		- Town: The town in which the Site is located
		- Location: The street address of the Site (if any)
		- Contact Person(s): The Volunteer Name
		- URL: The site URL
		- Primary_Caretaker: The primary caretaker for ALL the trees at the Site
		- Secondary_Caretaker: The secondary caretaker for ALL the trees at the Site
		- Hub: In what Hub is the Site contained
<details>
<summary>XXXXX</summary>

</details>
	1. A new 'CAMorg - Site' pair to EpiCollect
<details>
<summary>XXXXX</summary>

</details>
	1. A new Hub
		- Name: The Hub name
		- Captain: The Hub captain
		- Lieutenant: The Hub lieutenant
		- Site Name: Name of a site that is contained within the Hub
<details>
<summary>XXXXX</summary>

</details>
	1. A new Volunteer
		- first_name: first name
		- last_name: last name
		- email: email address
		- title: job title
		- hometown: home Town
		- phone numbers: cell, home, work, any and all
		- Add volunteer's email address to Epicollect
			- Add all volunteers to the CAM Tree Maintenance project even recognizing
			  some of them may never use EpiCollect.
			- Add Hub Captains, Lieutenants, and select other volunteers to the
			  CAM Tree Rain Event project
<p></p>

#### Later
5. Create a view that shows the tree photos from the first and last visit each year
	- Perhaps use some SQL code something like:
		- EXTRACT(YEAR FROM CURRENT_DATE) and EXTRACT(YEAR FROM tree_photo.date table)
<p></p>

6. Create a view that shows how close dead/poor trees are to each other?
	- Perhaps 3 views: 1) dead trees; 2) poor trees; 3) dead and poor trees combined
<p></p>



#### Long Term Desires
7. Some CAM Staff should have write access to the SQL tables
	- Would be most helpful to do this through a web browser versus DBeaver or any other
	  Database Management Tool.
	  	- CAM folks will not need to have DELETE capabilities. But they will need UPDATE
	  	  and possibly INSERT.
			- For example, marking a volunteer as 'inactive'
			- Changing (and removing) volunteers from the list of Hub Captains
			- Adding a volunteer
			- Adding a 'Site' (would need a function)
			- Adding a 'Hub' (perhaps via a function as well)
		- This would likely require changing from using 'ken.rosenberry@gmail.com' Neon
		  as the master to using the camorgdatabase@gmail.com as the master
		  	- We could than twin the database from camorgdatabase to ken.rosenberry
		  	  instead of our current method
<p></p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

## Web Access to the CAMTREES SQL Database

#### Hopefully Someday - but probably not soon unless we find $$$
1. Need live online access to the Neon CAMTREES Database
	- Use softr.io? (NOT FREE)
		- Has really nice Mapping capabilities (but might cost more $ for Google maps!)
		- Has nice filtering capabilities of tables (dropdown menus or text filtering)
		- Quite easy to create a website in no time
	- Given $$ contraints, research these
		- [6 Best No-Code Tools for PostgreSQL](https://www.nocobase.com/en/blog/6-no-code-tools-supporting-postgresql)
		- [Appsmith](https://www.appsmith.com)
		- [Teable](https://teable.ai)
		- [UI Bakery](https://www.youtube.com/watch?v=wE_Oafo1bx0_)

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

## CAMTREES Database Website

#### In Progress
1. Move Kenster ToDo list from external document into this list
2. Create additional empty skeleton pages for more topics
3. Add content into empty skeleton pages


#### Later
4. Get input on website from Kim, Eva, and Mark once website is a bit more developed

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 

## Python Programming

#### Soon
1. Need cloud solution (GitHub Actions?) to run Python scripts
	- Could create a schedule for running programs automatically but maybe it would be
	  better to have a human run the programs on demand.
	- An undesirable fallback option to a cloud solution would be for a user to run
	  the programs using PyCharm (or a similar environment) on his/her personal computer. 

#### Ongoing
2. After any Python Import code testing, delete ken.rosenberry@gmail.com records in tables:
	- tree
	- tree_photo
	- tree_care_action
	- tree_health_assessment

