# CAMTREES data-request handler

This folder contains the Google Apps Script source used to receive public forms
from the CAMTREES GitHub Pages site and email them to the Database Administrator.
It is separate from `scripts/` because those files are Python programs executed
by GitHub Actions, while this code is deployed and executed by Google.

## Initial deployment

1. Sign into Google Apps Script as `camorg.database@gmail.com` and create a new
   standalone project.
2. Copy `Code.gs` into the project. In **Project Settings**, enable display of
   the manifest file and replace it with `appsscript.json` from this folder.
3. Add these **Script properties** in Project Settings:
   - `DATABASE_ADMINISTRATOR_EMAIL`: destination address for requests.
   - `CAMTREES_RETURN_URL`: optional page to open after submission. The CAMTREES
     home page is used when this property is omitted.
4. Deploy the project as a **Web app**, execute it as the project owner, and
   permit the audience that should be able to submit public requests.
5. Authorize the mail permission when Google requests it.
6. Copy the deployed `/exec` URL into `google_apps_script_web_app_url` in the
   website's `_config.yml`, then rebuild the GitHub Pages site.

Do not use the test `/dev` URL in `_config.yml`; it is intended only for script
editors and is not the public deployment.

## Adding another request type

Adding a form requires changes in both locations:

1. Define its presentation fields in the site's `_data/request_forms.yml`.
2. Add the same request type and an explicit field allow-list to
   `REQUEST_DEFINITIONS` in `Code.gs`.

Forms that set `include_requested_by: true` automatically append the common
section from `_data/request_form_sections.yml`. In `Code.gs`, append the matching
`REQUESTOR_FIELDS` array and use `requestor_email` as `replyToField`.

The duplication is deliberate. The YAML controls what the browser displays,
while `Code.gs` independently controls what the server accepts and emails.
Never trust additional field names submitted by a browser.

After changing `Code.gs`, create a new Apps Script deployment version (or edit
the existing deployment to use the new version). Merely saving source changes
does not update an existing public deployment.
