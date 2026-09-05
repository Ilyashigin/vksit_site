document.addEventListener('DOMContentLoaded', async () => {
    // Сначала грузим подсказки, потом таблицу мероприятий
    await loadOptions();
    loadEvents();
});

const API_URL = '/api/mer';
let currentEventData = [];

// DOM-элементы
const modalEl = document.getElementById('eventModal');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('eventForm');
const datalistLevels = document.getElementById('dl_levels');

// ======================================
// 1. ЗАГРУЗКА СПИСКОВ (УРОВНИ) ДЛЯ DATALIST
// ======================================
async function loadOptions() {
    try {
        const res = await fetch('/api/options'); // Тот же эндпоинт, что в main.js
        if (!res.ok) throw new Error('Ошибка загрузки списков');

        const data = await res.json();

        // Заполняем <datalist id="dl_levels">
        if (datalistLevels && data.levels && Array.isArray(data.levels)) {
            datalistLevels.innerHTML = '';
            data.levels.forEach(l => {
                const option = document.createElement('option');
                option.value = l.name || l; // Поддержка разных форматов ответа
                datalistLevels.appendChild(option);
            });
        }
    } catch (err) {
        console.warn('Не удалось загрузить подсказки для уровней:', err);
        // Fallback: если API недоступен, можно добавить статичные варианты
        // ['Муниципальный', 'Региональный', 'Всероссийский', 'Международный'].forEach(val => {
        //     const opt = document.createElement('option');
        //     opt.value = val; datalistLevels.appendChild(opt);
        // });
    }
}

// ======================================
// 2. ЗАГРУЗКА МЕРОПРИЯТИЙ
// ======================================
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
                <td class="text-end">
                    <button class="btn btn-sm btn-warning"
                            onclick="openModal('edit', ${event.id})">
                        ✏️
                    </button>
                    <button class="btn btn-sm btn-danger"
                            onclick="deleteEvent(${event.id})">
                        ️🗑️
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-danger text-center">
                    ${err.message}
                </td>
            </tr>
        `;
    } finally {
        loading.style.display = 'none';
        table.style.display = 'table';
    }
}

// ======================================
// 3. МОДАЛЬНОЕ ОКНО
// ======================================
function openModal(type, id = null) {
    form.reset();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const event = currentEventData.find(e => e.id === id);
        if (event) {
            modalTitle.innerText = 'Редактировать мероприятие';
            document.getElementById('editId').value = event.id;
            document.getElementById('m_name').value = event.event_name;
            document.getElementById('m_date').value = event.event_date;
            // Уровень подставится автоматически, если он есть в datalist
            document.getElementById('m_level').value = event.event_level || '';
        }
    } else {
        modalTitle.innerText = 'Добавить мероприятие';
        document.getElementById('m_level').value = ''; // Сброс при добавлении
    }

    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modalEl).show();
    } else {
        modalEl.style.display = 'block';
        modalEl.classList.add('show');
    }
}

// ======================================
// 4. СОХРАНЕНИЕ (POST / PUT)
// ======================================
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
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ошибка сохранения');

        hideModal();
        loadEvents();
    } catch (err) {
        alert(err.message);
    }
}

// ======================================
// 5. УДАЛЕНИЕ
// ======================================
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

// ======================================
// 6. СКРЫТИЕ МОДАЛКИ
// ======================================
function hideModal() {
    if (typeof bootstrap !== 'undefined') {
        const instance = bootstrap.Modal.getInstance(modalEl);
        if (instance) instance.hide();
    } else {
        modalEl.style.display = 'none';
        modalEl.classList.remove('show');
    }
}