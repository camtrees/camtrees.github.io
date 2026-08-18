(() => {
  'use strict';

  const normalise = (value) => String(value ?? '').trim().toLocaleLowerCase();
  const rawValue = (row, key) => String(row[key] ?? '').trim();
  const yesNoValue = (value) => ['true', 't', 'yes', 'y', '1'].includes(normalise(value)) ? 'Yes' : ['false', 'f', 'no', 'n', '0'].includes(normalise(value)) ? 'No' : '';

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

  function initialise(root) {
    const configElement = root.querySelector('[data-cam-table-config]');
    let config;
    try { config = JSON.parse(configElement.textContent); }
    catch (_) { root.textContent = 'This table configuration could not be loaded.'; return; }

    const { columns, pageSize = 100 } = config;
    const table = root.querySelector('[data-cam-table-table]');
    const head = table.tHead; const body = table.tBodies[0];
    const search = root.querySelector('[data-cam-table-search]');
    const summary = root.querySelector('[data-cam-table-summary]');
    const pagination = root.querySelector('[data-cam-table-pagination]');
    const filters = new Map();
    let rows = []; let currentPage = 1; let sortKey = columns[0].key; let sortDirection = 'asc';

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

    function render() {
      const sorted = filteredRows();
      const sortColumn = columns.find((column) => column.key === sortKey);
      sorted.sort((a, b) => (sortDirection === 'asc' ? 1 : -1) * compareRows(a, b, sortColumn));
      const pages = Math.max(1, Math.ceil(sorted.length / pageSize));
      currentPage = Math.min(currentPage, pages);
      const first = (currentPage - 1) * pageSize;
      const shown = sorted.slice(first, first + pageSize);

      body.replaceChildren();
      if (!shown.length) {
        const cell = document.createElement('td'); cell.colSpan = columns.length; cell.className = 'cam-table__empty'; cell.textContent = 'No records match the current filters.';
        const row = document.createElement('tr'); row.append(cell); body.append(row);
      } else {
        shown.forEach((item) => {
          const row = document.createElement('tr');
          columns.forEach((column) => { const cell = document.createElement('td'); cell.textContent = displayValue(item, column) || '—'; row.append(cell); });
          body.append(row);
        });
      }
      summary.textContent = sorted.length ? `Showing ${first + 1}–${Math.min(first + pageSize, sorted.length)} of ${sorted.length} records` : '0 records';
      head.querySelectorAll('button[data-sort-key]').forEach((button) => button.setAttribute('aria-sort', button.dataset.sortKey === sortKey ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'));
      pagination.replaceChildren();
      if (pages > 1) {
        const previous = document.createElement('button'); previous.type = 'button'; previous.textContent = 'Previous'; previous.disabled = currentPage === 1; previous.addEventListener('click', () => { currentPage -= 1; render(); });
        const label = document.createElement('p'); label.textContent = `Page ${currentPage} of ${pages}`;
        const next = document.createElement('button'); next.type = 'button'; next.textContent = 'Next'; next.disabled = currentPage === pages; next.addEventListener('click', () => { currentPage += 1; render(); });
        pagination.append(previous, label, next);
      }
    }

    function refreshFromFirstPage() { currentPage = 1; render(); }
    const headerRow = document.createElement('tr');
    columns.forEach((column) => {
      const cell = document.createElement('th'); cell.scope = 'col';
      const button = document.createElement('button'); button.type = 'button'; button.textContent = column.label; button.dataset.sortKey = column.key;
      button.addEventListener('click', () => { sortDirection = sortKey === column.key && sortDirection === 'asc' ? 'desc' : 'asc'; sortKey = column.key; refreshFromFirstPage(); });
      const filter = createFilter(column, refreshFromFirstPage); filters.set(column.key, filter); cell.append(button, filter); headerRow.append(cell);
    });
    head.append(headerRow); search.addEventListener('input', refreshFromFirstPage);

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
