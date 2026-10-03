document.addEventListener('DOMContentLoaded', async () => {
    initEventDatePicker();
    await loadOptions();
    loadEvents();
});

const API_URL = '/api/events';
let currentEventData = [];
let eventDatePicker = null;

const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('eventForm');
const datalistLevels = document.getElementById('dl_levels');

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

function formatDateObjToDdMmYyyy(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    return `${day}.${month}.${date.getFullYear()}`;
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

function buildEventPeriod() {
    if (!eventDatePicker || !eventDatePicker.selectedDates.length) return '';

    const dates = eventDatePicker.selectedDates;
    const startFmt = formatDateObjToDdMmYyyy(dates[0]);
    if (dates.length === 1) return startFmt;

    const endFmt = formatDateObjToDdMmYyyy(dates[1]);
    if (startFmt === endFmt) return startFmt;
    return `${startFmt}-${endFmt}`;
}

function setEventDate(value) {
    if (!eventDatePicker) return;

    const period = parseEventPeriod(value);
    if (period.start && period.end) {
        eventDatePicker.setDate([period.start, period.end], false);
    } else if (period.start) {
        eventDatePicker.setDate([period.start], false);
    } else {
        eventDatePicker.clear(false);
    }
}

function clearEventDate() {
    if (eventDatePicker) eventDatePicker.clear(false);
}

function initEventDatePicker() {
    const input = document.getElementById('m_date');
    if (!input || eventDatePicker || typeof flatpickr === 'undefined') return;

    eventDatePicker = flatpickr(input, {
        mode: 'range',
        locale: 'ru',
        dateFormat: 'd.m.Y',
        rangeSeparator: ' — ',
        allowInput: false,
    });
}

async function loadOptions() {
    try {
        const res = await fetch('/api/options');
        if (!res.ok) throw new Error('Ошибка загрузки списков');
        const data = await res.json();

        if (datalistLevels && data.levels) {
            datalistLevels.innerHTML = data.levels
                .map(level => `<option value="${level.name || level}">`)
                .join('');
        }
    } catch (err) {
        console.warn('Не удалось загрузить подсказки для уровней:', err);
    }
}

async function loadEvents() {
    const tableBody = document.getElementById('event-body');
    const loading = document.getElementById('loading-events');
    const table = document.getElementById('event-table');

    loading.style.display = 'block';
    table.style.display = 'none';
    tableBody.innerHTML = '';

    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error('Ошибка загрузки мероприятий');
        currentEventData = await res.json();

        currentEventData.forEach(event => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${event.id}</td>
                <td>${event.name}</td>
                <td>${event.description || '-'}</td>
                <td>${event.level_name || '-'}</td>
                <td>${event.date}</td>
                <td class="table__actions">
                    <button class="btn btn--sm btn--warning" onclick="openEventModal('edit', ${event.id})">Ред.</button>
                    <button class="btn btn--sm btn--danger" onclick="deleteEvent(${event.id})">Уд.</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="6" class="text-danger text-center">${err.message}</td></tr>`;
    } finally {
        loading.style.display = 'none';
        table.style.display = 'table';
    }
}

function openEventModal(type, id = null) {
    form.reset();
    clearEventDate();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const event = currentEventData.find(e => e.id === id);
        if (event) {
            modalTitle.innerText = 'Редактировать мероприятие';
            document.getElementById('editId').value = event.id;
            document.getElementById('m_name').value = event.name;
            document.getElementById('m_description').value = event.description || '';
            setEventDate(event.date);
            document.getElementById('m_level').value = event.level_name || '';
        }
    } else {
        modalTitle.innerText = 'Добавить мероприятие';
    }

    openModal('eventModal');
}

async function saveEvent() {
    const id = document.getElementById('editId').value;
    const eventName = document.getElementById('m_name').value.trim();
    const eventDate = buildEventPeriod();
    const levelName = document.getElementById('m_level').value.trim();

    if (!eventName) { alert('Поле Название обязательно к заполнению'); return; }
    if (!eventDate) { alert('Укажите дату или период проведения'); return; }
    if (!levelName) { alert('Поле Уровень обязательно к заполнению'); return; }

    const payload = {
        name: eventName,
        date: eventDate,
        description: document.getElementById('m_description').value.trim(),
        level_name: levelName
    };

    const url = id ? `${API_URL}/${id}` : API_URL;
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
        loadEvents();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteEvent(id) {
    if (!confirm('Вы уверены, что хотите удалить мероприятие?')) return;

    try {
        const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadEvents();
        } else {
            const data = await res.json();
            alert(data.error || 'Ошибка при удалении');
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
    }
}
