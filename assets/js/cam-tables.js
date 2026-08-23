(() => {
  'use strict';

  const normalise = (value) => String(value ?? '').trim().toLocaleLowerCase();
  const rawValue = (row, key) => String(row[key] ?? '').trim();
  const yesNoValue = (value) => ['true', 't', 'yes', 'y', '1'].includes(normalise(value)) ? 'Yes' : ['false', 'f', 'no', 'n', '0'].includes(normalise(value)) ? 'No' : '';
  let dialogNumber = 0;

  function showDialog(dialog) {
    if (typeof dialog.showModal === 'function' && !dialog.open) dialog.showModal();
    else dialog.setAttribute('open', '');
  }

  function displayValue(row, column) {
    const value = rawValue(row, column.key);
    return column.type === 'boolean' ? yesNoValue(value) : value;
  }

  function compareRows(left, right, column) {
    const a = rawValue(left, column.key);
    const b = rawValue(right, column.key);
    if (!a || !b) return a ? -1 : b ? 1 : 0;
    if (column.type === 'number') return Number(a) - Number(b);
    if (column.type === 'date') return Date.parse(a) - Date.parse(b);
    // Tree ID is explicitly text, so numeric collation is intentionally disabled.
    return a.localeCompare(b, undefined, { numeric: false, sensitivity: 'base' });
  }

  function createFilter(column, refresh) {
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
        const value = document.createElement('dd'); value.textContent = displayValue(record, column) || '—';
        details.append(label, value);
      });
      showDialog(dialog);
    };
  }

  function createMapDialog() {
    const dialog = document.createElement('dialog');
    dialog.className = 'cam-map-dialog';
    const title = document.createElement('h2'); title.textContent = 'Map View';
    const close = document.createElement('button'); close.type = 'button'; close.className = 'cam-map-dialog__close'; close.textContent = 'Close';
    const header = document.createElement('div'); header.className = 'cam-map-dialog__header'; header.append(title, close);
    const status = document.createElement('p'); status.className = 'cam-map-dialog__status'; status.setAttribute('aria-live', 'polite');
    const canvas = document.createElement('div'); canvas.className = 'cam-map-dialog__map'; canvas.setAttribute('aria-label', 'Map of filtered trees');
    dialog.append(header, status, canvas); document.body.append(dialog);

    const closeDialog = () => {
      if (typeof dialog.close === 'function') dialog.close();
      else dialog.removeAttribute('open');
    };
    close.addEventListener('click', closeDialog);
    dialog.addEventListener('click', (event) => { if (event.target === dialog) closeDialog(); });

    let map; let markers;
    return (records) => {
      if (!window.L) {
        status.textContent = 'The map library could not be loaded. Check that your browser can load unpkg.com.';
        showDialog(dialog);
        return;
      }
      try {
        if (!map) {
          map = window.L.map(canvas);
          window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          }).addTo(map);
          markers = window.L.layerGroup().addTo(map);
        }
      } catch (_) {
        status.textContent = 'The map could not be initialized.';
        showDialog(dialog);
        return;
      }
      markers.clearLayers();
      const points = records.map((record) => {
        const latitudeValue = rawValue(record, 'latitude');
        const longitudeValue = rawValue(record, 'longitude');
        return { record, latitudeValue, longitudeValue, latitude: Number(latitudeValue), longitude: Number(longitudeValue) };
      }).filter((point) => point.latitudeValue && point.longitudeValue && Number.isFinite(point.latitude) && Number.isFinite(point.longitude) && Math.abs(point.latitude) <= 90 && Math.abs(point.longitude) <= 180);
      points.forEach((point) => {
        const popup = document.createElement('div');
        const site = document.createElement('strong'); site.textContent = rawValue(point.record, 'site') || 'Unknown site';
        popup.append(site, document.createElement('br'), document.createTextNode(`Tree ID: ${rawValue(point.record, 'tree_id') || '—'}`));
        window.L.circleMarker([point.latitude, point.longitude], { radius: 7, color: '#2f6b3a', fillColor: '#5eaa6c', fillOpacity: .9, weight: 1.5 })
          .bindPopup(popup).addTo(markers);
      });
      status.textContent = `${points.length} of ${records.length} filtered tree${records.length === 1 ? '' : 's'} mapped.`;
      showDialog(dialog);
      requestAnimationFrame(() => requestAnimationFrame(() => {
        map.invalidateSize({ animate: false, pan: false });
        if (points.length === 1) map.setView([points[0].latitude, points[0].longitude], 17, { animate: false });
        else if (points.length > 1) map.fitBounds(points.map((point) => [point.latitude, point.longitude]), { padding: [24, 24], maxZoom: 17, animate: false });
        else map.setView([45.25, -69.45], 6, { animate: false });
        // Safari can finish sizing a dialog after the first two paint frames.
        window.setTimeout(() => map.invalidateSize({ animate: false, pan: false }), 150);
      }));
    };
  }

  function initialise(root) {
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
    const mapButton = root.querySelector('[data-cam-table-map]');
    const filters = new Map();
    const openRecordDialog = createRecordDialog(columns);
    const openMapDialog = mapButton ? createMapDialog() : null;
    let rows = []; let currentPage = 1; let sortKey = columns[0].key; let sortDirection = 'asc'; let printing = false;

    function filteredRows() {
      const globalTerm = normalise(search.value);
      return rows.filter((row) => {
        if (globalTerm && !columns.some((column) => normalise(displayValue(row, column)).includes(globalTerm))) return false;
        return [...filters].every(([key, filter]) => {
          const column = columns.find((item) => item.key === key);
          const filterValue = normalise(filter.value);
          return !filterValue || normalise(displayValue(row, column)).includes(filterValue);
        });
      });
    }

    function sortedRows() {
      const sorted = filteredRows();
      const sortColumn = columns.find((column) => column.key === sortKey);
      return sorted.sort((a, b) => (sortDirection === 'asc' ? 1 : -1) * compareRows(a, b, sortColumn));
    }

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
          columns.forEach((column) => { const cell = document.createElement('td'); cell.textContent = displayValue(item, column) || '—'; row.append(cell); });
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

    function refreshFromFirstPage() { currentPage = 1; render(); }
    const headerRow = document.createElement('tr');
    const actionHeader = document.createElement('th'); actionHeader.scope = 'col'; actionHeader.textContent = 'View Record'; headerRow.append(actionHeader);
    columns.forEach((column) => {
      const cell = document.createElement('th'); cell.scope = 'col';
      const button = document.createElement('button'); button.type = 'button'; button.textContent = column.label; button.dataset.sortKey = column.key;
      button.addEventListener('click', () => { sortDirection = sortKey === column.key && sortDirection === 'asc' ? 'desc' : 'asc'; sortKey = column.key; refreshFromFirstPage(); });
      const filter = createFilter(column, refreshFromFirstPage); filters.set(column.key, filter); cell.append(button, filter); headerRow.append(cell);
    });
    head.append(headerRow); search.addEventListener('input', refreshFromFirstPage);
    if (mapButton) mapButton.addEventListener('click', () => openMapDialog(filteredRows()));
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

    fetch(root.dataset.source, { credentials: 'same-origin' })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then((payload) => {
        const records = Array.isArray(payload) ? payload : payload.records;
        rows = Array.isArray(records) ? records : [];
        render();
      })
      .catch(() => { summary.textContent = 'The table data is temporarily unavailable.'; });
  }

  document.querySelectorAll('[data-cam-table]').forEach(initialise);
})();
