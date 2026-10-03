document.addEventListener('DOMContentLoaded', async () => {
    await loadOptions();
    loadEvents();
});

const API_URL = '/api/mer';
let currentEventData = [];

const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('eventForm');
const datalistLevels = document.getElementById('dl_levels');

async function loadOptions() {
    try {
        const res = await fetch('/api/options');
        if (!res.ok) throw new Error('Ошибка загрузки списков');
        const data = await res.json();

        if (datalistLevels && data.levels) {
            datalistLevels.innerHTML = data.levels
                .map(l => `<option value="${l.name || l}">`)
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
                <td>${event.event_name}</td>
                <td>${event.event_level || '-'}</td>
                <td>${event.event_date}</td>
                <td class="table__actions">
                    <button class="btn btn--sm btn--warning" onclick="openEventModal('edit', ${event.id})">Ред.</button>
                    <button class="btn btn--sm btn--danger" onclick="deleteEvent(${event.id})">Уд.</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-danger text-center">${err.message}</td></tr>`;
    } finally {
        loading.style.display = 'none';
        table.style.display = 'table';
    }
}

function openEventModal(type, id = null) {
    form.reset();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const event = currentEventData.find(e => e.id === id);
        if (event) {
            modalTitle.innerText = 'Редактировать мероприятие';
            document.getElementById('editId').value = event.id;
            document.getElementById('m_name').value = event.event_name;
            document.getElementById('m_date').value = event.event_date;
            document.getElementById('m_level').value = event.event_level || '';
        }
    } else {
        modalTitle.innerText = 'Добавить мероприятие';
    }

    openModal('eventModal');
}

async function saveEvent() {
    const id = document.getElementById('editId').value;
    const eventName = document.getElementById('m_name').value.trim();
    const eventDate = document.getElementById('m_date').value;
    const eventLevel = document.getElementById('m_level').value.trim();

    if (!eventName) { alert('Поле Название обязательно к заполнению'); return; }
    if (!eventDate) { alert('Поле Дата обязательно к заполнению'); return; }
    if (!eventLevel) { alert('Поле Уровень обязательно к заполнению'); return; }

    const payload = {
        event_name: eventName,
        event_date: eventDate,
        event_level: eventLevel
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
