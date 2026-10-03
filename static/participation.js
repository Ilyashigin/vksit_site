const USER_TYPE = window.USER_TYPE || 'teacher';
const API_BASE = window.API_BASE || '/api/participation/teachers';
const TEACHER_API = '/api/participation/teachers';

function parseToIsoDate(str) {
    if (!str) return '';
    const value = String(str).trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value;

    const dmY = value.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
    if (dmY) {
        return `${dmY[3]}-${dmY[2].padStart(2, '0')}-${dmY[1].padStart(2, '0')}`;
    }
    return '';
}

function formatIsoToDdMmYyyy(iso) {
    if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return '';
    const [y, m, d] = iso.split('-');
    return `${d}.${m}.${y}`;
}

function formatDisplayDate(str) {
    if (!str) return '';
    const value = String(str).trim();

    const rangeMatch = value.match(/^(\d{1,2}\.\d{1,2}\.\d{4})-(\d{1,2}\.\d{1,2}\.\d{4})$/);
    if (rangeMatch) return value;

    const iso = parseToIsoDate(value);
    if (iso) return formatIsoToDdMmYyyy(iso);

    return value;
}

function parseEventPeriod(str) {
    if (!str) return { start: '', end: '' };
    const value = String(str).trim();

    const rangeMatch = value.match(/^(\d{1,2}\.\d{1,2}\.\d{4})-(\d{1,2}\.\d{1,2}\.\d{4})$/);
    if (rangeMatch) {
        return {
            start: parseToIsoDate(rangeMatch[1]),
            end: parseToIsoDate(rangeMatch[2]),
        };
    }

    return { start: parseToIsoDate(value), end: '' };
}

function formatDateObjToDdMmYyyy(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    return `${day}.${month}.${date.getFullYear()}`;
}

function dateObjToIso(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function buildPeriodFromPicker(picker) {
    if (!picker || !picker.selectedDates.length) return '';

    const dates = picker.selectedDates;
    const startFmt = formatDateObjToDdMmYyyy(dates[0]);
    if (dates.length === 1) return startFmt;

    const endFmt = formatDateObjToDdMmYyyy(dates[1]);
    if (startFmt === endFmt) return startFmt;
    return `${startFmt}-${endFmt}`;
}

function buildEventPeriod() {
    return buildPeriodFromPicker(eventDatePicker);
}

function buildMentorEventPeriod() {
    return buildPeriodFromPicker(mentorDatePicker);
}

function computeAcademicYear(isoDate) {
    if (!isoDate || !/^\d{4}-\d{2}-\d{2}$/.test(isoDate)) return '';
    const [year, month] = isoDate.split('-').map(Number);
    const year1 = month >= 9 ? year : year - 1;
    return `${year1}-${year1 + 1}`;
}

function updateYearFromDate() {
    let startIso = '';
    if (eventDatePicker && eventDatePicker.selectedDates.length) {
        startIso = dateObjToIso(eventDatePicker.selectedDates[0]);
    }

    const year = computeAcademicYear(startIso);
    document.getElementById('m_year').value = year;

    const hint = document.getElementById('m_year_hint');
    if (hint) {
        hint.textContent = year ? `Учебный период: ${year}` : '';
    }
}

function setPickerDate(picker, value) {
    if (!picker) return;

    const period = parseEventPeriod(value);
    if (period.start && period.end) {
        picker.setDate([period.start, period.end], false);
    } else if (period.start) {
        picker.setDate([period.start], false);
    } else {
        picker.clear(false);
    }
}

function setEventDate(value) {
    setPickerDate(eventDatePicker, value);
    updateYearFromDate();
}

function setMentorEventDate(value) {
    setPickerDate(mentorDatePicker, value);
}

function clearEventDate() {
    if (eventDatePicker) eventDatePicker.clear(false);
    document.getElementById('m_year').value = '';
    const hint = document.getElementById('m_year_hint');
    if (hint) hint.textContent = '';
}

let eventDatePicker = null;
let mentorDatePicker = null;

function initEventDatePicker() {
    const input = document.getElementById('m_date');
    if (!input || eventDatePicker || typeof flatpickr === 'undefined') return;

    eventDatePicker = flatpickr(input, {
        mode: 'range',
        locale: 'ru',
        dateFormat: 'd.m.Y',
        rangeSeparator: ' — ',
        allowInput: false,
        onChange: updateYearFromDate,
        onClose: updateYearFromDate,
    });
}

function initMentorDatePicker() {
    const input = document.getElementById('mentor_date');
    if (!input || mentorDatePicker || typeof flatpickr === 'undefined') return;

    mentorDatePicker = flatpickr(input, {
        mode: 'range',
        locale: 'ru',
        dateFormat: 'd.m.Y',
        rangeSeparator: ' — ',
        allowInput: false,
    });
}

let optionsData = {
    users: [],
    events: [],
    levels: [],
    years: []
};

document.addEventListener('DOMContentLoaded', async () => {
    initEventDatePicker();
    initMentorDatePicker();
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
    return ['full_name', 'fio', 'level', 'event', 'mentor', 'group', 'year'].some(k => params.get(k));
}

function fillSearchFromUrl(params) {
    const set = (id, key) => {
        const el = document.getElementById(id);
        if (el && params.get(key)) el.value = params.get(key);
    };
    set('searchFullName', 'full_name');
    if (!params.get('full_name') && params.get('fio')) {
        set('searchFullName', 'fio');
    }
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
            <td>${item.level_name}</td>
            <td>${formatDisplayDate(item.event_date)}</td>
            <td>${item.participant_name} | ${item.results}</td>
        `;
        if (USER_TYPE === 'student') {
            row += `<td>${item.group || '-'}</td><td>${item.mentor || '-'}</td>`;
        }
        row += `
            <td class="table__actions">
                <button class="btn btn--sm btn--warning" onclick="openEditModal(${item.id})">Ред.</button>
                <button class="btn btn--sm btn--danger" onclick="deleteParticipation(${item.id})">Уд.</button>
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
    const fullName = document.getElementById('searchFullName').value.trim();

    if (year) params.set('year', year);
    if (level) params.set('level', level);
    if (event) params.set('event', event);
    if (fullName) params.set('full_name', fullName);

    if (USER_TYPE === 'student') {
        const mentor = document.getElementById('searchMentor').value.trim();
        const group = document.getElementById('searchGroup').value.trim();
        if (mentor) params.set('mentor', mentor);
        if (group) params.set('group', group);
    }

    return `/api/filter?${params.toString()}`;
}

function applyFilter() {
    const params = new URLSearchParams(buildFilterUrl().split('?')[1]);
    const hasFilter = ['year', 'level', 'event', 'full_name', 'mentor', 'group'].some(k => params.get(k));

    if (!hasFilter) {
        alert('Заполните хотя бы одно поле для поиска');
        return;
    }

    fetchFiltered(buildFilterUrl());
}

function resetSearch() {
    ['searchLevel', 'searchEvent', 'searchFullName', 'searchMentor', 'searchGroup'].forEach(id => {
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
        populatePeriodSelects(years);

        const teachers = optionsData.users.filter(u => !u.group || u.group.trim() === '');
        const students = optionsData.users.filter(u => u.group && u.group.trim() !== '');

        if (USER_TYPE === 'student') {
            fillDatalist('dl_users', students.map(u => u.full_name));
            fillDatalist('dl_mentors', teachers.map(u => u.full_name));
            fillDatalist('dl_search_users', students.map(u => u.full_name));
            fillDatalist('dl_search_mentors', teachers.map(u => u.full_name));
            if (optionsData.groups) {
                fillDatalist('dl_groups', optionsData.groups.map(g => g.name));
                fillDatalist('dl_search_groups', optionsData.groups.map(g => g.name));
            }
        } else {
            fillDatalist('dl_users', teachers.map(u => u.full_name));
            fillDatalist('dl_search_users', teachers.map(u => u.full_name));
        }

        populateReportUsers();
    } catch (err) {
        console.error(err);
    }
}

function getReportUsersList() {
    const type = document.getElementById('repType')?.value || 'all';
    if (type === 'teacher') {
        return optionsData.users.filter(u => !u.group || u.group.trim() === '');
    }
    if (type === 'student') {
        return optionsData.users.filter(u => u.group && u.group.trim() !== '');
    }
    return optionsData.users;
}

function userDisplayLabel(user) {
    if (user.group && user.group.trim()) {
        return `${user.full_name} (${user.group})`;
    }
    return user.full_name;
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
    const found = list.find(u => userDisplayLabel(u) === input || u.full_name === input);
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
            document.getElementById('m_level').value = ev.level_name;
            document.getElementById('m_description').value = ev.description || '';
            setEventDate(ev.date);
        }
    });

    const fullNameInput = document.getElementById('m_full_name');
    fullNameInput.addEventListener('change', function () {
        const user = optionsData.users.find(u => u.full_name === this.value);
        if (user && USER_TYPE === 'student') {
            document.getElementById('m_group').value = user.group || '';
        }
    });
}

function openAddModal() {
    document.getElementById('editId').value = '';
    document.getElementById('modalTitle').innerText = 'Добавить мероприятие';
    document.getElementById('eventForm').reset();
    clearEventDate();
    loadOptions().then(() => setupAutoFill());
    openModal('eventModal');
}

async function openEditModal(id) {
    document.getElementById('editId').value = id;
    document.getElementById('modalTitle').innerText = 'Редактировать мероприятие';
    document.getElementById('eventForm').reset();
    clearEventDate();
    openModal('eventModal');

    try {
        const res = await fetch(`${API_BASE}/${id}`);
        if (!res.ok) throw new Error('Ошибка загрузки');
        const item = await res.json();

        document.getElementById('m_name').value = item.event_name || '';
        document.getElementById('m_description').value = item.description || '';
        document.getElementById('m_level').value = item.level_name || '';
        setEventDate(item.event_date || '');
        document.getElementById('m_full_name').value = item.participant_name || '';

        const parts = (item.results || '').split(',').map(s => s.trim());
        document.getElementById('m_result').value = parts[0] || '';
        document.getElementById('m_diplomas').value = parts[1] || '';
        document.getElementById('m_awards').value = parts[2] || '';

        if (USER_TYPE === 'student') {
            document.getElementById('m_group').value = item.group || '';
            document.getElementById('m_mentor').value = item.mentor || '';
        }

        await loadOptions();
        setupAutoFill();
    } catch (err) {
        alert(err.message);
    }
}

async function checkMentorDuplicate(data) {
    try {
        const res = await fetch(TEACHER_API);
        if (!res.ok) return false;
        const teachers = await res.json();
        return teachers.some(item =>
            item.participant_name === data.mentor &&
            item.event_name === data.event_name &&
            item.event_date === data.event_date &&
            item.level_name === data.level_name
        );
    } catch {
        return false;
    }
}

async function openMentorFollowUpModal(data) {
    if (!data.mentor || !String(data.mentor).trim()) return;

    document.getElementById('mentor_name').value = data.event_name || '';
    document.getElementById('mentor_description').value = data.description || '';
    document.getElementById('mentor_level').value = data.level_name || '';
    setMentorEventDate(data.event_date || '');
    document.getElementById('mentor_full_name').value = data.mentor || '';
    document.getElementById('mentor_result').value = data.result || '';
    document.getElementById('mentor_diplomas').value = '';
    document.getElementById('mentor_awards').value = '';

    const warning = document.getElementById('mentorDuplicateWarning');
    if (warning) {
        const isDuplicate = await checkMentorDuplicate(data);
        warning.style.display = isDuplicate ? 'block' : 'none';
    }

    openModal('mentorModal');
}

function skipMentorParticipation() {
    closeModal('mentorModal');
    const warning = document.getElementById('mentorDuplicateWarning');
    if (warning) warning.style.display = 'none';
}

async function saveMentorParticipation() {
    const eventDate = buildMentorEventPeriod();
    if (!eventDate) {
        alert('Укажите дату или период проведения');
        return;
    }

    const payload = {
        event_name: document.getElementById('mentor_name').value,
        description: document.getElementById('mentor_description').value.trim(),
        level_name: document.getElementById('mentor_level').value,
        event_date: eventDate,
        full_name: document.getElementById('mentor_full_name').value,
        result: document.getElementById('mentor_result').value,
        diplomas: document.getElementById('mentor_diplomas').value,
        awards: document.getElementById('mentor_awards').value,
    };

    try {
        const res = await fetch(TEACHER_API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ошибка сохранения');

        skipMentorParticipation();
        alert('Участие наставника добавлено');
    } catch (err) {
        alert(err.message);
    }
}

async function saveParticipation() {
    updateYearFromDate();

    const eventDate = buildEventPeriod();
    const academicYear = document.getElementById('m_year').value;

    if (!eventDate) {
        alert('Укажите дату или период проведения');
        return;
    }

    const payload = {
        event_name: document.getElementById('m_name').value,
        description: document.getElementById('m_description').value.trim(),
        level_name: document.getElementById('m_level').value,
        event_date: eventDate,
        full_name: document.getElementById('m_full_name').value,
        result: document.getElementById('m_result').value,
        diplomas: document.getElementById('m_diplomas').value,
        awards: document.getElementById('m_awards').value,
        year: academicYear
    };

    if (USER_TYPE === 'student') {
        payload.group = document.getElementById('m_group').value;
        payload.mentor = document.getElementById('m_mentor').value;
    }

    const id = document.getElementById('editId').value;
    const url = id ? `${API_BASE}/${id}` : API_BASE;
    const method = id ? 'PUT' : 'POST';
    const isNewStudent = USER_TYPE === 'student' && !id;
    const mentorSnapshot = isNewStudent ? { ...payload } : null;

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

        if (mentorSnapshot) {
            await openMentorFollowUpModal(mentorSnapshot);
        }
    } catch (err) {
        alert(err.message);
    }
}

async function deleteParticipation(id) {
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
        link.download = `report_${year}_${type}.docx`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(link.href);

        closeModal('reportModal');
    } catch (err) {
        alert(err.message);
    }
}
