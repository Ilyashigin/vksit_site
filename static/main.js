const USER_TYPE = window.USER_TYPE || 'ped';
const API_BASE = window.API_BASE || '/api/uchastiya/ped';

let optionsData = {
    users: [],
    events: [],
    levels: [],
    years: []
};

document.addEventListener('DOMContentLoaded', async () => {
    await loadOptions();
    initReportUserPicker();

    const urlParams = new URLSearchParams(location.search);
    if (hasUrlFilters(urlParams)) {
        fillSearchFromUrl(urlParams);
        applyFilter();
    } else {
        loadTable();
    }
});

function hasUrlFilters(params) {
    return ['fio', 'level', 'event', 'mentor', 'group', 'year'].some(k => params.get(k));
}

function fillSearchFromUrl(params) {
    const set = (id, key) => {
        const el = document.getElementById(id);
        if (el && params.get(key)) el.value = params.get(key);
    };
    set('searchFio', 'fio');
    set('searchLevel', 'level');
    set('searchEvent', 'event');
    set('searchMentor', 'mentor');
    set('searchGroup', 'group');
    set('filterYear', 'year');
}

function populatePeriodSelects(years) {
    const filter = document.getElementById('filterYear');
    const rep = document.getElementById('repYear');
    if (!filter || !rep) return;

    const currentFilter = filter.value;
    filter.innerHTML = '<option value="">Все периоды</option>' +
        years.map(y => `<option value="${y}">${y}</option>`).join('');
    if (currentFilter) filter.value = currentFilter;

    rep.innerHTML = years.length
        ? years.map(y => `<option value="${y}">${y}</option>`).join('')
        : '<option value="">Нет периодов в БД</option>';
}

function fillDatalist(id, values) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = values.map(v => `<option value="${v}">`).join('');
}

function renderTable(data) {
    const tbody = document.getElementById('table-body');
    const table = document.getElementById('main-table');
    tbody.innerHTML = '';

    data.forEach(item => {
        let row = `
            <td>${item.id}</td>
            <td>${item.event_name}</td>
            <td>${item.event_level}</td>
            <td>${item.event_date}</td>
            <td>${item.user_name} | ${item.rezults}</td>
        `;
        if (USER_TYPE === 'stud') {
            row += `<td>${item.group || '-'}</td><td>${item.mentor || '-'}</td>`;
        }
        row += `
            <td class="table__actions">
                <button class="btn btn--sm btn--warning" onclick="openEditModal(${item.id})">Ред.</button>
                <button class="btn btn--sm btn--danger" onclick="deleteEvent(${item.id})">Уд.</button>
            </td>
        `;
        const tr = document.createElement('tr');
        tr.innerHTML = row;
        tbody.appendChild(tr);
    });
    table.style.display = 'table';
}

async function loadTable() {
    const tbody = document.getElementById('table-body');
    const spinner = document.getElementById('loading');
    const table = document.getElementById('main-table');

    spinner.style.display = 'block';
    table.style.display = 'none';
    tbody.innerHTML = '';

    try {
        const res = await fetch(API_BASE);
        if (!res.ok) throw new Error('Ошибка загрузки данных');
        renderTable(await res.json());
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-danger text-center">${err.message}</td></tr>`;
        table.style.display = 'table';
    } finally {
        spinner.style.display = 'none';
    }
}

async function fetchFiltered(url) {
    const tbody = document.getElementById('table-body');
    const spinner = document.getElementById('loading');
    const table = document.getElementById('main-table');

    spinner.style.display = 'block';
    table.style.display = 'none';
    tbody.innerHTML = '';

    try {
        const res = await fetch(url);
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData[0]?.error || errData.error || 'Ничего не найдено');
        }
        renderTable(await res.json());
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-warning text-center">${err.message}</td></tr>`;
        table.style.display = 'table';
    } finally {
        spinner.style.display = 'none';
    }
}

function buildFilterUrl() {
    const params = new URLSearchParams();
    params.set('user_type', USER_TYPE);

    const year = document.getElementById('filterYear').value;
    const level = document.getElementById('searchLevel').value.trim();
    const event = document.getElementById('searchEvent').value.trim();
    const fio = document.getElementById('searchFio').value.trim();

    if (year) params.set('year', year);
    if (level) params.set('level', level);
    if (event) params.set('event', event);
    if (fio) params.set('fio', fio);

    if (USER_TYPE === 'stud') {
        const mentor = document.getElementById('searchMentor').value.trim();
        const group = document.getElementById('searchGroup').value.trim();
        if (mentor) params.set('mentor', mentor);
        if (group) params.set('group', group);
    }

    return `/api/filter?${params.toString()}`;
}

function applyFilter() {
    const params = new URLSearchParams(buildFilterUrl().split('?')[1]);
    const hasFilter = ['year', 'level', 'event', 'fio', 'mentor', 'group'].some(k => params.get(k));

    if (!hasFilter) {
        alert('Заполните хотя бы одно поле для поиска');
        return;
    }

    fetchFiltered(buildFilterUrl());
}

function resetSearch() {
    ['searchLevel', 'searchEvent', 'searchFio', 'searchMentor', 'searchGroup'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    document.getElementById('filterYear').value = '';
    history.replaceState({}, '', location.pathname);
    loadTable();
}

async function loadOptions() {
    try {
        const res = await fetch('/api/options');
        if (!res.ok) throw new Error('Ошибка загрузки списков');
        optionsData = await res.json();

        fillDatalist('dl_events', optionsData.events.map(e => e.name));
        fillDatalist('dl_levels', optionsData.levels.map(l => l.name));
        fillDatalist('dl_search_events', optionsData.events.map(e => e.name));
        fillDatalist('dl_search_levels', optionsData.levels.map(l => l.name));

        const years = optionsData.years || [];
        fillDatalist('dl_years', years);
        populatePeriodSelects(years);

        const teachers = optionsData.users.filter(u => !u.group || u.group.trim() === '');
        const students = optionsData.users.filter(u => u.group && u.group.trim() !== '');

        if (USER_TYPE === 'stud') {
            fillDatalist('dl_users', students.map(u => u.fio));
            fillDatalist('dl_mentors', teachers.map(u => u.fio));
            fillDatalist('dl_search_users', students.map(u => u.fio));
            fillDatalist('dl_search_mentors', teachers.map(u => u.fio));
            if (optionsData.groups) {
                fillDatalist('dl_groups', optionsData.groups.map(g => g.name));
                fillDatalist('dl_search_groups', optionsData.groups.map(g => g.name));
            }
        } else {
            fillDatalist('dl_users', teachers.map(u => u.fio));
            fillDatalist('dl_search_users', teachers.map(u => u.fio));
        }

        populateReportUsers();
    } catch (err) {
        console.error(err);
    }
}

function getReportUsersList() {
    const type = document.getElementById('repType')?.value || 'all';
    if (type === 'ped') {
        return optionsData.users.filter(u => !u.group || u.group.trim() === '');
    }
    if (type === 'stud') {
        return optionsData.users.filter(u => u.group && u.group.trim() !== '');
    }
    return optionsData.users;
}

function userDisplayLabel(u) {
    if (u.group && u.group.trim()) {
        return `${u.fio} (${u.group})`;
    }
    return u.fio;
}

function populateReportUsers() {
    const list = getReportUsersList();
    fillDatalist('dl_report_users', list.map(userDisplayLabel));
}

function resolveReportUserId() {
    const input = document.getElementById('repUser').value.trim();
    document.getElementById('repUserId').value = '';
    if (!input) return '';

    const list = getReportUsersList();
    const found = list.find(u => userDisplayLabel(u) === input || u.fio === input);
    if (found) {
        document.getElementById('repUserId').value = found.id;
        return found.id;
    }
    return '';
}

function initReportUserPicker() {
    const repType = document.getElementById('repType');
    const repUser = document.getElementById('repUser');
    if (repType) {
        repType.addEventListener('change', () => {
            repUser.value = '';
            document.getElementById('repUserId').value = '';
            populateReportUsers();
        });
    }
    if (repUser) {
        repUser.addEventListener('change', resolveReportUserId);
        repUser.addEventListener('blur', resolveReportUserId);
    }
}

function setupAutoFill() {
    document.getElementById('m_name').addEventListener('change', function () {
        const ev = optionsData.events.find(e => e.name === this.value);
        if (ev) {
            document.getElementById('m_level').value = ev.level;
            document.getElementById('m_date').value = ev.date;
        }
    });

    const fioInput = document.getElementById('m_fio');
    fioInput.addEventListener('change', function () {
        const usr = optionsData.users.find(u => u.fio === this.value);
        if (usr && USER_TYPE === 'stud') {
            document.getElementById('m_group').value = usr.group || '';
        }
    });
}

function openAddModal() {
    document.getElementById('editId').value = '';
    document.getElementById('modalTitle').innerText = 'Добавить мероприятие';
    document.getElementById('eventForm').reset();
    loadOptions().then(() => setupAutoFill());
    openModal('eventModal');
}

async function openEditModal(id) {
    document.getElementById('editId').value = id;
    document.getElementById('modalTitle').innerText = 'Редактировать мероприятие';
    document.getElementById('eventForm').reset();
    openModal('eventModal');

    try {
        const res = await fetch(`${API_BASE}/${id}`);
        if (!res.ok) throw new Error('Ошибка загрузки');
        const item = await res.json();

        document.getElementById('m_name').value = item.event_name || '';
        document.getElementById('m_level').value = item.event_level || '';
        document.getElementById('m_date').value = item.event_date || '';
        document.getElementById('m_fio').value = item.user_name || '';
        document.getElementById('m_year').value = item.year || '';

        const parts = (item.rezults || '').split(',').map(s => s.trim());
        document.getElementById('m_result').value = parts[0] || '';
        document.getElementById('m_diploms').value = parts[1] || '';
        document.getElementById('m_awards').value = parts[2] || '';

        if (USER_TYPE === 'stud') {
            document.getElementById('m_group').value = item.group || '';
            document.getElementById('m_mentor').value = item.mentor || '';
        }

        await loadOptions();
        setupAutoFill();
    } catch (err) {
        alert(err.message);
    }
}

async function saveEvent() {
    const payload = {
        event_name: document.getElementById('m_name').value,
        event_level: document.getElementById('m_level').value,
        event_date: document.getElementById('m_date').value,
        fio: document.getElementById('m_fio').value,
        rezultat: document.getElementById('m_result').value,
        diplomi: document.getElementById('m_diploms').value,
        nagradi: document.getElementById('m_awards').value,
        year: document.getElementById('m_year').value
    };

    if (USER_TYPE === 'stud') {
        payload.group = document.getElementById('m_group').value;
        payload.mentor = document.getElementById('m_mentor').value;
    }

    const id = document.getElementById('editId').value;
    const url = id ? `${API_BASE}/${id}` : API_BASE;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ошибка сохранения');

        closeModal('eventModal');
        loadTable();
        loadOptions();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteEvent(id) {
    if (!confirm('Удалить запись?')) return;
    try {
        const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
        if (res.ok) loadTable();
        else alert('Ошибка удаления');
    } catch {
        alert('Ошибка сети');
    }
}

async function startDownload() {
    const year = document.getElementById('repYear').value;
    const type = document.getElementById('repType').value;
    const sort = document.getElementById('repSort').value;
    const userId = resolveReportUserId();

    if (!year) {
        alert('Нет доступных учебных периодов в базе данных');
        return;
    }

    let url = `/api/report/download?year=${encodeURIComponent(year)}&type=${type}&sort=${sort}`;
    if (userId) url += `&user_id=${userId}`;

    try {
        const res = await fetch(url);
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || 'Ошибка формирования отчета');
        }

        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `otchet_${year}_${type}.docx`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(link.href);

        closeModal('reportModal');
    } catch (err) {
        alert(err.message);
    }
}
