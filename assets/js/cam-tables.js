(() => {
  'use strict';

  // Convert database values into consistent strings for searching and display.
  const normalise = (value) => String(value ?? '').trim().toLocaleLowerCase();
  const rawValue = (row, key) => String(row[key] ?? '').trim();
  const yesNoValue = (value) => ['true', 't', 'yes', 'y', '1'].includes(normalise(value)) ? 'Yes' : ['false', 'f', 'no', 'n', '0'].includes(normalise(value)) ? 'No' : '';
  let dialogNumber = 0;

  // Open an HTML dialog, with a fallback for browsers lacking showModal().
  function showDialog(dialog) {
    if (typeof dialog.showModal === 'function' && !dialog.open) dialog.showModal();
    else dialog.setAttribute('open', '');
  }

  function displayValue(row, column) {
    const value = rawValue(row, column.key);
    return column.type === 'boolean' ? yesNoValue(value) : value;
  }

  // Permit only normal web addresses before turning database text into a link.
  function safeWebUrl(value) {
    try {
      const url = new URL(value);
      return ['https:', 'http:'].includes(url.protocol) ? url.href : '';
    } catch (_) {
      return '';
    }
  }

  // Add either plain text or a safe new-tab website link to a table cell.
  function appendValue(container, row, column) {
    const value = displayValue(row, column);
    const url = column.type === 'url' ? safeWebUrl(value) : '';
    if (url) {
      const link = document.createElement('a');
      link.className = 'cam-table__url';
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = column.linkLabel || value;
      link.setAttribute('aria-label', `${column.linkLabel || column.label} (opens in a new tab)`);
      container.append(link);
    } else {
      container.textContent = value || '—';
    }
  }

  // Compare two records using the data type declared in the table configuration.
  function compareRows(left, right, column) {
    const a = rawValue(left, column.key);
    const b = rawValue(right, column.key);
    if (!a || !b) return a ? -1 : b ? 1 : 0;
    if (column.type === 'number') return Number(a) - Number(b);
    if (column.type === 'date') return Date.parse(a) - Date.parse(b);
    // Tree ID is explicitly text, so numeric collation is intentionally disabled.
    return a.localeCompare(b, undefined, { numeric: false, sensitivity: 'base' });
  }

  // Quote a value according to CSV rules, including embedded quotation marks.
  function csvCell(value) {
    return `"${String(value ?? '').replace(/"/g, '""')}"`;
  }

  // Build a UTF-8 CSV file in the browser and start the user's download.
  function downloadCsv(records, columns, filename) {
    const lines = [
      columns.map((column) => csvCell(column.label)).join(','),
      ...records.map((record) => columns.map((column) => csvCell(displayValue(record, column))).join(','))
    ];
    const blob = new Blob([`\uFEFF${lines.join('\r\n')}\r\n`], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  // Build a checkbox menu whose choices are populated from the downloaded JSON.
  function createMultiFilter(column, refresh) {
    const filter = document.createElement('details');
    filter.className = 'cam-table__multi-filter';
    const summary = document.createElement('summary');
    const options = document.createElement('div');
    options.className = 'cam-table__multi-filter-options';
    const choices = document.createElement('div');
    const clear = document.createElement('button');
    clear.type = 'button'; clear.textContent = 'Clear selections';
    options.append(choices, clear); filter.append(summary, options);
    const selectedValues = new Set();

    // An empty selection means All; otherwise values use exact OR matching.
    const updateSummary = () => {
      const text = selectedValues.size ? `${selectedValues.size} selected` : 'All';
      summary.textContent = text;
      summary.setAttribute('aria-label', `Filter ${column.label}: ${text}`);
    };
    filter.matchesValue = (value) => !selectedValues.size || selectedValues.has(normalise(value));
    filter.populateOptions = (records) => {
      const uniqueValues = new Map();
      records.forEach((record) => {
        const value = displayValue(record, column);
        if (value && !uniqueValues.has(normalise(value))) uniqueValues.set(normalise(value), value);
      });
      choices.replaceChildren();
      [...uniqueValues].sort((left, right) => left[1].localeCompare(right[1], undefined, { sensitivity: 'base' })).forEach(([value, labelText]) => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox'; checkbox.value = value;
        checkbox.addEventListener('change', () => {
          if (checkbox.checked) selectedValues.add(value);
          else selectedValues.delete(value);
          updateSummary();
          refresh();
        });
        label.append(checkbox, document.createTextNode(labelText));
        choices.append(label);
      });
    };
    clear.addEventListener('click', () => {
      selectedValues.clear();
      choices.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => { checkbox.checked = false; });
      updateSummary();
      refresh();
    });
    updateSummary();
    return filter;
  }

  // Boolean fields use All/Yes/No, configured multi-filters use checkboxes,
  // and all remaining columns use a normal search box.
  function createFilter(column, refresh) {
    if (column.filter === 'multi') return createMultiFilter(column, refresh);
    if (column.type === 'boolean') {
      const filter = document.createElement('select');
      filter.setAttribute('aria-label', `Filter ${column.label}`);
      [['', 'All'], ['Yes', 'Yes'], ['No', 'No']].forEach(([value, label]) => {
        const option = new Option(label, value); filter.add(option);
      });
      filter.addEventListener('change', refresh);
      return filter;
    }
    const filter = document.createElement('input');
    filter.type = 'search'; filter.placeholder = `Filter ${column.label}`;
    filter.setAttribute('aria-label', `Filter ${column.label}`);
    filter.addEventListener('input', refresh);
    return filter;
  }

  // Create one reusable dialog that displays a selected row vertically.
  function createRecordDialog(columns) {
    dialogNumber += 1;
    const dialog = document.createElement('dialog');
    dialog.className = 'cam-record-dialog';
    const title = document.createElement('h2');
    title.id = `cam-record-dialog-title-${dialogNumber}`;
    title.textContent = 'Record details';
    const close = document.createElement('button');
    close.type = 'button'; close.className = 'cam-record-dialog__close'; close.textContent = 'Close';
    const header = document.createElement('div');
    header.className = 'cam-record-dialog__header'; header.append(title, close);
    const details = document.createElement('dl');
    details.className = 'cam-record-dialog__details';
    dialog.setAttribute('aria-labelledby', title.id); dialog.append(header, details); document.body.append(dialog);

    const closeDialog = () => {
      if (typeof dialog.close === 'function') dialog.close();
      else dialog.removeAttribute('open');
    };
    close.addEventListener('click', closeDialog);
    dialog.addEventListener('click', (event) => { if (event.target === dialog) closeDialog(); });

    return (record) => {
      details.replaceChildren();
      columns.forEach((column) => {
        const label = document.createElement('dt'); label.textContent = column.label;
        const value = document.createElement('dd'); appendValue(value, record, column);
        details.append(label, value);
      });
      showDialog(dialog);
    };
  }

  // Create the Leaflet dialog used by any table with map configuration.
  function createMapDialog(openRecordDialog, mapConfig = {}) {
    // General table and popup settings are shared by every map theme.
    const singular = mapConfig.singular || 'tree';
    const plural = mapConfig.plural || `${singular}s`;
    const overlayConfigs = Array.isArray(mapConfig.overlays) ? mapConfig.overlays : [];
    const popupTitleKey = mapConfig.popupTitleKey || 'site';
    const popupFields = mapConfig.popupFields || [
      { key: 'tree_id', label: 'Tree ID' },
      { key: 'latest_health', label: 'Health' }
    ];

    // Older single-theme configurations still work for tables such as CAM Sites.
    const legacyTheme = {
      label: mapConfig.legendTitle || 'Legend',
      markerStyleKey: mapConfig.markerStyleKey || '',
      markerStyles: mapConfig.markerStyles || {},
      defaultMarkerStyle: mapConfig.defaultMarkerStyle || { order: -1, color: '#2f6b3a', fillColor: '#5eaa6c' }
    };
    const themes = mapConfig.themes || { default: legacyTheme };
    const themeKeys = Object.keys(themes);
    const defaultThemeKey = themes[mapConfig.defaultTheme] ? mapConfig.defaultTheme : themeKeys[0];
    const hasThemeSelector = themeKeys.length > 1;
    const hasLegend = themeKeys.some((key) => {
      const theme = themes[key];
      return Object.values(theme.markerStyles || {}).some((style) => style.label) || theme.defaultMarkerStyle?.label;
    });

    // Build the dialog once; its markers and status are refreshed each time it opens.
    dialogNumber += 1;
    const themeControlName = `cam-map-theme-${dialogNumber}`;
    const dialog = document.createElement('dialog');
    dialog.className = 'cam-map-dialog';
    const title = document.createElement('h2'); title.textContent = 'Map View';
    const close = document.createElement('button'); close.type = 'button'; close.className = 'cam-map-dialog__close'; close.textContent = 'Close';
    const header = document.createElement('div'); header.className = 'cam-map-dialog__header'; header.append(title, close);
    const status = document.createElement('p'); status.className = 'cam-map-dialog__status'; status.setAttribute('aria-live', 'polite');
    const canvas = document.createElement('div'); canvas.className = 'cam-map-dialog__map'; canvas.setAttribute('aria-label', `Map of filtered ${plural}`);
    dialog.append(header, status, canvas); document.body.append(dialog);

    const closeDialog = () => {
      if (typeof dialog.close === 'function') dialog.close();
      else dialog.removeAttribute('open');
    };
    close.addEventListener('click', closeDialog);
    dialog.addEventListener('click', (event) => { if (event.target === dialog) closeDialog(); });

    let map; let markers; let legendContainer; let legendHeading; let legendList;
    let activeThemeKey = defaultThemeKey;
    let currentRecords = [];
    const themeInputs = new Map();
    const defaultOverlayLayers = [];

    // Refresh the legend whenever the user changes the marker-color theme.
    function updateLegend(theme, points) {
      if (!legendHeading || !legendList) return;
      const defaultStyle = theme.defaultMarkerStyle || legacyTheme.defaultMarkerStyle;
      const plottedStyles = new Set(points.map((point) => point.markerStyle));
      const entries = Object.values(theme.markerStyles || {})
        .concat(defaultStyle.label ? [defaultStyle] : [])
        // Only explain colors that are actually visible in the current map.
        .filter((style) => style.label && plottedStyles.has(style))
        .sort((left, right) => (left.legendOrder ?? left.order) - (right.legendOrder ?? right.order));
      legendHeading.textContent = theme.legendTitle || theme.label || 'Legend';
      legendContainer.hidden = !entries.length;
      legendList.replaceChildren();
      entries.forEach((style) => {
        const item = document.createElement('li');
        const swatch = document.createElement('span');
        swatch.className = 'cam-map-legend__swatch';
        swatch.style.backgroundColor = style.fillColor;
        swatch.style.borderColor = style.color;
        swatch.setAttribute('aria-hidden', 'true');
        item.append(swatch, document.createTextNode(style.label));
        legendList.append(item);
      });
    }

    // Redraw the same table-filtered records using the selected map theme.
    function drawMap(records) {
      const theme = themes[activeThemeKey];
      const markerStyleKey = theme.markerStyleKey || '';
      const markerStyles = theme.markerStyles || {};
      const defaultMarkerStyle = theme.defaultMarkerStyle || legacyTheme.defaultMarkerStyle;
      const includeValues = (theme.includeValues || []).map(normalise);
      markers.clearLayers();
      map.closePopup();

      // Discard invalid coordinates and, when configured, unwanted theme values.
      const points = records.map((record, sourceIndex) => {
        const latitudeValue = rawValue(record, 'latitude');
        const longitudeValue = rawValue(record, 'longitude');
        const styleName = markerStyleKey ? normalise(rawValue(record, markerStyleKey)) : '';
        const markerStyle = markerStyles[styleName] || defaultMarkerStyle;
        return { record, sourceIndex, styleName, markerStyle, latitudeValue, longitudeValue, latitude: Number(latitudeValue), longitude: Number(longitudeValue) };
      }).filter((point) => (!includeValues.length || includeValues.includes(point.styleName)) && point.latitudeValue && point.longitudeValue && Number.isFinite(point.latitude) && Number.isFinite(point.longitude) && Math.abs(point.latitude) <= 90 && Math.abs(point.longitude) <= 180)
        // Later groups are drawn last so their overlapping pins stay visible.
        .sort((left, right) => (left.markerStyle.order - right.markerStyle.order) || (left.sourceIndex - right.sourceIndex));

      // The legend describes only marker categories present after filtering.
      updateLegend(theme, points);

      // Create each marker popup without inserting untrusted database HTML.
      points.forEach((point) => {
        const popup = document.createElement('div');
        const popupTitle = document.createElement('strong'); popupTitle.textContent = rawValue(point.record, popupTitleKey) || `Unknown ${singular}`;
        const detailButton = document.createElement('button');
        detailButton.type = 'button'; detailButton.className = 'cam-map-dialog__record-button'; detailButton.textContent = 'View full record';
        detailButton.addEventListener('click', () => {
          map.closePopup();
          openRecordDialog(point.record);
        });
        popup.append(popupTitle);
        popupFields.forEach((field) => {
          popup.append(
            document.createElement('br'),
            document.createTextNode(`${field.label}: ${rawValue(point.record, field.key) || '—'}`)
          );
        });
        popup.append(document.createElement('br'), detailButton);
        window.L.circleMarker([point.latitude, point.longitude], {
          radius: 7,
          color: point.markerStyle.color,
          fillColor: point.markerStyle.fillColor,
          fillOpacity: .9,
          weight: 1.5
        }).bindPopup(popup).addTo(markers);
      });

      const noun = records.length === 1 ? singular : plural;
      status.textContent = `${points.length} of ${records.length} filtered ${noun} ${theme.statusSuffix || 'mapped.'}`;

      // Wait for the dialog to receive its final size before fitting the map.
      requestAnimationFrame(() => requestAnimationFrame(() => {
        map.invalidateSize({ animate: false, pan: false });
        if (points.length === 1) map.setView([points[0].latitude, points[0].longitude], 17, { animate: false });
        else if (points.length > 1) map.fitBounds(points.map((point) => [point.latitude, point.longitude]), { padding: [24, 24], maxZoom: 17, animate: false });
        else map.setView([45.25, -69.45], 6, { animate: false });
        // Safari can finish sizing a dialog after the first two paint frames.
        window.setTimeout(() => map.invalidateSize({ animate: false, pan: false }), 150);
      }));
    }

    return (records) => {
      if (!window.L) {
        status.textContent = 'The map library could not be loaded. Check that your browser can load unpkg.com.';
        showDialog(dialog);
        return;
      }
      try {
        if (!map) {
          // Initialize Leaflet only on the first click and offer four base maps.
          map = window.L.map(canvas);
          const streetLayer = window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          });
          const satelliteLayer = window.L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}', {
            maxNativeZoom: 16,
            maxZoom: 19,
            attribution: 'USGS The National Map'
          });
          const topoLayer = window.L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}', {
            maxNativeZoom: 16,
            maxZoom: 19,
            attribution: 'USGS The National Map'
          });
          const imageryTopoLayer = window.L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}', {
            maxNativeZoom: 15,
            maxZoom: 19,
            attribution: 'USGS The National Map'
          });
          streetLayer.addTo(map);
          const layerControl = window.L.control.layers({
            Street: streetLayer,
            Satellite: satelliteLayer,
            Topographic: topoLayer,
            'Satellite + Labels': imageryTopoLayer
          }, null, { collapsed: true, position: 'topright' }).addTo(map);

          // Load optional same-site GeoJSON overlays into a pane below the
          // table record markers. Each table decides whether an overlay is
          // initially checked through its showByDefault configuration.
          if (overlayConfigs.length) {
            map.createPane('camReferenceOverlay');
            map.getPane('camReferenceOverlay').style.zIndex = 350;
            overlayConfigs.forEach((overlayConfig) => {
              const overlayLayer = window.L.geoJSON(null, {
                pane: 'camReferenceOverlay',
                style: { color: '#356b44', weight: 2.5, opacity: .85 },
                // Hub centers use noninteractive black triangles with their
                // names directly below; record markers retain all popups.
                pointToLayer: (feature, latlng) => {
                  const content = document.createElement('div');
                  content.className = 'cam-hub-center-marker';
                  const triangle = document.createElement('span');
                  triangle.className = 'cam-hub-center-marker__triangle';
                  triangle.setAttribute('aria-hidden', 'true');
                  const label = document.createElement('span');
                  label.className = 'cam-hub-center-marker__label';
                  label.textContent = feature.properties?.Name || 'Hub';
                  content.append(triangle, label);
                  return window.L.marker(latlng, {
                    pane: 'camReferenceOverlay',
                    interactive: false,
                    icon: window.L.divIcon({
                      className: 'cam-hub-center-icon',
                      html: content,
                      iconSize: [160, 32],
                      iconAnchor: [80, 5]
                    })
                  });
                }
              });
              fetch(overlayConfig.url, { credentials: 'same-origin' })
                .then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
                .then((geoJson) => {
                  overlayLayer.addData(geoJson);
                  layerControl.addOverlay(overlayLayer, overlayConfig.label);
                  if (overlayConfig.showByDefault) {
                    defaultOverlayLayers.push(overlayLayer);
                    overlayLayer.addTo(map);
                  }
                })
                // A failed optional overlay must not prevent the record map.
                .catch(() => { console.warn(`Map overlay could not be loaded: ${overlayConfig.label}`); });
            });
          }

          // Let users switch thematic coloring without opening another map.
          if (hasThemeSelector) {
            const themeControl = window.L.control({ position: 'bottomleft' });
            themeControl.onAdd = () => {
              const container = document.createElement('div');
              container.className = 'cam-map-theme';
              container.setAttribute('role', 'radiogroup');
              container.setAttribute('aria-label', 'Color pins by');
              // A normal heading stays inside the panel; fieldset legends can
              // straddle the border differently across Safari and Chrome.
              const heading = document.createElement('strong');
              heading.textContent = 'Color pins by';
              container.append(heading);
              themeKeys.forEach((key) => {
                const label = document.createElement('label');
                const input = document.createElement('input');
                input.type = 'radio'; input.name = themeControlName; input.value = key;
                input.addEventListener('change', () => {
                  if (!input.checked) return;
                  activeThemeKey = key;
                  drawMap(currentRecords);
                });
                themeInputs.set(key, input);
                label.append(input, document.createTextNode(themes[key].label || key));
                container.append(label);
              });
              window.L.DomEvent.disableClickPropagation(container);
              return container;
            };
            themeControl.addTo(map);
          }

          // The legend contents change to match the active marker-color theme.
          if (hasLegend) {
            const legend = window.L.control({ position: 'bottomright' });
            legend.onAdd = () => {
              legendContainer = document.createElement('div');
              legendContainer.className = 'cam-map-legend';
              legendContainer.setAttribute('role', 'group');
              legendContainer.setAttribute('aria-label', 'Map legend');
              legendHeading = document.createElement('strong');
              legendList = document.createElement('ul');
              legendContainer.append(legendHeading, legendList);
              return legendContainer;
            };
            legend.addTo(map);
          }
          markers = window.L.layerGroup().addTo(map);
        }
      } catch (_) {
        status.textContent = 'The map could not be initialized.';
        showDialog(dialog);
        return;
      }

      // Every opening starts from the configured default (Tree Health for CAM Trees).
      currentRecords = records;
      activeThemeKey = defaultThemeKey;
      themeInputs.forEach((input, key) => { input.checked = key === activeThemeKey; });
      // Restore table-specific default overlays whenever a map is reopened.
      defaultOverlayLayers.forEach((overlayLayer) => overlayLayer.addTo(map));
      showDialog(dialog);
      drawMap(currentRecords);
    };
  }

  // Turn one data-cam-table section and its JSON configuration into a table.
  function initialise(root) {
    // Read the table-specific columns, filenames, and optional map settings.
    const configElement = root.querySelector('[data-cam-table-config]');
    let config;
    try { config = JSON.parse(configElement.textContent); }
    catch (_) { root.textContent = 'This table configuration could not be loaded.'; return; }

    const { columns, pageSize = 1000 } = config;
    const table = root.querySelector('[data-cam-table-table]');
    const head = table.tHead; const body = table.tBodies[0];
    const search = root.querySelector('[data-cam-table-search]');
    const summary = root.querySelector('[data-cam-table-summary]');
    const pagination = root.querySelector('[data-cam-table-pagination]');
    const printButton = root.querySelector('[data-cam-table-print]');
    const csvButton = root.querySelector('[data-cam-table-csv]');
    const mapButton = root.querySelector('[data-cam-table-map]');
    const filters = new Map();
    const openRecordDialog = createRecordDialog(columns);
    const openMapDialog = mapButton ? createMapDialog(openRecordDialog, config.map) : null;
    let rows = []; let currentPage = 1; let sortKey = columns[0].key; let sortDirection = 'asc'; let printing = false;

    // Apply the global search and every active column filter simultaneously.
    function filteredRows() {
      const globalTerm = normalise(search.value);
      return rows.filter((row) => {
        if (globalTerm && !columns.some((column) => normalise(displayValue(row, column)).includes(globalTerm))) return false;
        return [...filters].every(([key, filter]) => {
          const column = columns.find((item) => item.key === key);
          if (filter.matchesValue) return filter.matchesValue(displayValue(row, column));
          const filterValue = normalise(filter.value);
          return !filterValue || normalise(displayValue(row, column)).includes(filterValue);
        });
      });
    }

    // Sort a fresh filtered array without changing the original JSON records.
    function sortedRows() {
      const sorted = filteredRows();
      const sortColumn = columns.find((column) => column.key === sortKey);
      return sorted.sort((a, b) => (sortDirection === 'asc' ? 1 : -1) * compareRows(a, b, sortColumn));
    }

    // Redraw the visible page, record count, sort indicators, and pagination.
    function render() {
      const sorted = sortedRows();
      const pages = Math.max(1, Math.ceil(sorted.length / pageSize));
      currentPage = Math.min(currentPage, pages);
      const first = (currentPage - 1) * pageSize;
      const shown = printing ? sorted : sorted.slice(first, first + pageSize);

      body.replaceChildren();
      if (!shown.length) {
        const cell = document.createElement('td'); cell.colSpan = columns.length + 1; cell.className = 'cam-table__empty'; cell.textContent = 'No records match the current filters.';
        const row = document.createElement('tr'); row.append(cell); body.append(row);
      } else {
        shown.forEach((item) => {
          const row = document.createElement('tr');
          const actionCell = document.createElement('td');
          const viewButton = document.createElement('button');
          viewButton.type = 'button'; viewButton.className = 'cam-table__view-record'; viewButton.title = 'View record'; viewButton.setAttribute('aria-label', 'View record details');
          const icon = document.createElement('span'); icon.setAttribute('aria-hidden', 'true'); icon.textContent = '👁';
          const label = document.createElement('span'); label.className = 'cam-table__view-label'; label.textContent = 'View record';
          viewButton.append(icon, label); viewButton.addEventListener('click', () => openRecordDialog(item)); actionCell.append(viewButton); row.append(actionCell);
          columns.forEach((column) => { const cell = document.createElement('td'); appendValue(cell, item, column); row.append(cell); });
          body.append(row);
        });
      }
      summary.textContent = sorted.length ? `Showing ${first + 1}–${Math.min(first + pageSize, sorted.length)} of ${sorted.length} records` : '0 records';
      head.querySelectorAll('button[data-sort-key]').forEach((button) => button.setAttribute('aria-sort', button.dataset.sortKey === sortKey ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'));
      pagination.replaceChildren();
      if (!printing && pages > 1) {
        const previous = document.createElement('button'); previous.type = 'button'; previous.textContent = 'Previous'; previous.disabled = currentPage === 1; previous.addEventListener('click', () => { currentPage -= 1; render(); });
        const label = document.createElement('p'); label.textContent = `Page ${currentPage} of ${pages}`;
        const next = document.createElement('button'); next.type = 'button'; next.textContent = 'Next'; next.disabled = currentPage === pages; next.addEventListener('click', () => { currentPage += 1; render(); });
        pagination.append(previous, label, next);
      }
    }

    // Changing a search, filter, or sort always returns the user to page one.
    function refreshFromFirstPage() { currentPage = 1; render(); }

    // Build the sortable heading row and one filter control per data column.
    const headerRow = document.createElement('tr');
    const actionHeader = document.createElement('th'); actionHeader.scope = 'col'; actionHeader.textContent = 'View Record'; headerRow.append(actionHeader);
    columns.forEach((column) => {
      const cell = document.createElement('th'); cell.scope = 'col';
      const button = document.createElement('button'); button.type = 'button'; button.textContent = column.label; button.dataset.sortKey = column.key;
      button.addEventListener('click', () => { sortDirection = sortKey === column.key && sortDirection === 'asc' ? 'desc' : 'asc'; sortKey = column.key; refreshFromFirstPage(); });
      const filter = createFilter(column, refreshFromFirstPage); filters.set(column.key, filter); cell.append(button, filter); headerRow.append(cell);
    });
    head.append(headerRow); search.addEventListener('input', refreshFromFirstPage);

    // Map, CSV, and print actions all operate on the current filtered records.
    if (mapButton) mapButton.addEventListener('click', () => openMapDialog(filteredRows()));
    if (csvButton) csvButton.addEventListener('click', () => downloadCsv(sortedRows(), columns, config.csvFilename || 'table.csv'));
    if (printButton) {
      printButton.addEventListener('click', () => {
        printing = true;
        render();
        // Keep this synchronous with the click: some browsers block print
        // dialogs that are opened after an animation frame or timeout.
        window.print();
      });
      window.addEventListener('afterprint', () => {
        if (printing) { printing = false; render(); }
      });
    }

    // Fetch only the public static JSON file; the browser never contacts Neon.
    fetch(root.dataset.source, { credentials: 'same-origin' })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then((payload) => {
        const records = Array.isArray(payload) ? payload : payload.records;
        rows = Array.isArray(records) ? records : [];
        // Multi-select options come from the complete JSON dataset.
        filters.forEach((filter) => { if (filter.populateOptions) filter.populateOptions(rows); });
        render();
      })
      .catch(() => { summary.textContent = 'The table data is temporarily unavailable.'; });
  }

  // A page may contain one or more independently configured public tables.
  document.querySelectorAll('[data-cam-table]').forEach(initialise);
})();
