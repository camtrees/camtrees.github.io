# GitHub Pages

This repository holds files required to build this CAMTREES Database Website.

All pages use Jekyll and the 'Just the Docs' Jekyll template except for the Database
Tables pages. Those use a 'nil' layout so the html table is as large as possible.

# CAMTREES public data pipeline

The public table pages fetch only static JSON files in `data/`. Those files are
refreshed nightly by GitHub Actions from the PostgreSQL views
`public_cam_trees`, `public_cam_sites`, `public_cam_orgs`, and
`public_cam_hubs`, `public_site_visit`, and `public_sites_hubs`; browsers never
connect to Neon and never receive the database URL. `public_parent_trees` is
exported through the same pipeline.

## Setup

1. In the repository’s GitHub Actions secrets, create `CAMTREES_READ_URL` with
   the read-replica Neon PostgreSQL connection URL and `CAMTREES_WRITE_URL`
   with the writable Neon connection URL. Also create `MAINT_CLIENT_SECRET`
   and `RAIN_CLIENT_SECRET` with the two EpiCollect API client secrets. Do not
   add any of these values to site files or Jekyll configuration.
2. Ensure the database views exist with the columns expected by the export
   allow-list. The CAM Trees view begins with `site`, `tree_id`, `town`, `hub`,
   and `cam_org` in that order.
3. Enable GitHub Actions write permissions for the repository if they are not
   already allowed. Run **Export public CAMTREES data** once from the Actions
   tab to create the first populated JSON export.
4. Add the appropriate table include to a normal Just the Docs page, or use
   the included `cam-trees.md`, `cam-sites.md`, `cam-orgs.md`, or
   `cam-hubs.md`, or `site-visit.md` page. Each include loads data with
   Jekyll’s `relative_url` filter, so it supports a project-site base path.
   `parent-trees.md` is available for the Parent Trees table, and
   `sites-in-hubs.md` is available for Sites in Hubs.

The exporter has a small allow-list in `scripts/export_public_data.py`. Add a
new entry there for each future public view so additional datasets follow the
same private-export/public-JSON pattern.

The nightly export workflow also builds and deploys the Jekyll site in the same
workflow: GitHub does not start a second workflow from the data commit created
with its built-in `GITHUB_TOKEN`. The build installs the repository's Gemfile
dependencies so the Just the Docs theme is available. For a minimal repository
without a Gemfile, it installs pinned Jekyll and Just the Docs versions directly.
The Pages build runs even when no exported data changes, allowing a manual run
to repair or repeat a previous failed deployment. Its GitHub-maintained action
versions target the current Node.js 24 Actions runtime.

Before exporting public data, the nightly workflow imports EpiCollect rain-event
data, imports EpiCollect tree-maintenance data, and fills missing tree elevations,
in that order. It explicitly selects the writable CAMTREES database for these
three programs. EpiCollect tokens are requested only when the runner has no valid
cached token; their temporary cache is never committed or copied into the site.

Each maintenance program writes a timestamped log. Because those logs can include
private EpiCollect record details, the workflow stores them as a downloadable
GitHub Actions artifact for 30 days instead of committing them to the public
repository. Logs are uploaded even when a maintenance step fails.

The CAM Trees export includes the site's `town` plus `longitude` and `latitude`
from `public_cam_trees`. The Map filtered trees control uses those static JSON
coordinates in the browser; it does not connect to Neon. Its layer selector
offers OpenStreetMap Street and the USGS Satellite, Topographic, and Satellite
+ Labels base maps.

The CAM Sites export includes `town`, `hub`, `longitude`, and `latitude` from
`public_cam_sites`. Its displayed columns follow the view order beginning with
Site, Town, Hub, Organization Code, and Organization. The Map filtered sites
control uses the same map component and base-map choices, while displaying
the Site name, Town, Hub, Organization code, and Organization in each marker
popup.

The CAM Sites table renders `site_url` as a Visit Website link that opens in a
new tab. Only `http:` and `https:` addresses are made clickable.

CAM Trees map markers are color-coded by `latest_health`: Good is green,
Dormant is blue, Poor is yellow, and Dead is red. Unrecognized health values
are gray. Markers are drawn in that order so Dead markers remain above the
other overlapping markers. The map displays a Tree Health legend generated
from the same marker configuration.

Every public table can download all currently filtered records as a UTF-8 CSV
file in the table's current sort order. CSV exports contain the configured data
columns but not the View Record action column.

The CAM Trees map opens with Tree Health coloring. Its in-map Color pins by
control can switch to Nuts Present coloring; that theme maps only trees whose
`nuts_present` value is `some` or `many`. Switching themes does not change the
table's active searches or column filters.

The CAM Trees Latest Health column uses a checkbox multi-filter populated from
the unique values in the downloaded JSON. Selected values use OR logic within
that column and remain combined with all other filters. Map legends show only
the marker categories actually plotted after filtering and coordinate checks.

The CAM Trees and CAM Sites maps load `data/hub-areas.geojson` as an optional
Hub Areas overlay in the Leaflet layer control. It is off by default and is
drawn beneath the record markers without tooltips or popups. Its center points
are interior polygon centers shown as small black triangles with permanent
Hub-name labels. The overlay contains 19 adjoining, non-overlapping Hub
boundaries with one merged Warren area; the Coastal Downeast no-grow zone is
intentionally excluded.

CAM Sites records are shown with square map pins filled with `#f000e0`. This
table-specific marker setting does not affect CAM Trees or CAM Hubs markers.

Every interactive map includes a location button beneath the zoom controls.
It requests browser location permission when clicked, centers the map on the
reported position, and draws a blue location marker with an accuracy circle.

The CAM Hubs export includes `longitude` and `latitude`. Its Map filtered hubs
control always shows filtered Hubs as clickable black triangles with permanent
Hub-name labels and Captain and Lieutenant details. The Hub Areas checkbox
controls only the green boundary outlines and starts enabled. The Trees and
Sites maps continue to open with their complete Hub Areas overlay disabled.
