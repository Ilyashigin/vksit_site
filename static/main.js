document.addEventListener('DOMContentLoaded', loadTable);

const USER_TYPE = window.USER_TYPE || 'ped';
const API_BASE = window.API_BASE || '/api/uchastiya/ped';
let optionsData = { users: [], events: [], levels: [] };

// Загрузка таблицы (без изменений)
async function loadTable() {
    const tbody = document.getElementById('table-body');
    const spinner = document.getElementById('loading');
    const table = document.getElementById('main-table');
    spinner.style.display = 'block'; table.style.display = 'none'; tbody.innerHTML = '';

    try {
        const res = await fetch(API_BASE);
        if (!res.ok) throw new Error('Ошибка сети');
        const data = await res.json();
        data.forEach(item => {
            if (USER_TYPE === 'stud' && !item.group) return;
            let row = `<td>${item.id}</td><td>${item.event_name}</td><td>${item.event_level}</td>
                       <td>${item.event_date}</td><td>${item.user_name} | ${item.rezults}</td>`;
            if (USER_TYPE === 'stud') row += `<td>${item.group || '-'}</td>`;
            row += `<td><button class="btn btn-sm btn-warning mx-1" onclick="openEditModal(${item.id})">Ред.</button>
                    <button class="btn btn-sm btn-danger mx-1" onclick="deleteEvent(${item.id})">Уд.</button></td>`;
            const tr = document.createElement('tr'); tr.innerHTML = row; tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-danger">Ошибка: ${err.message}</td></tr>`;
    } finally {
        spinner.style.display = 'none'; table.style.display = 'table';
    }
}

// Загрузка вариантов для datalist
async function loadOptions() {
    try {
        const res = await fetch('/api/options');
        optionsData = await res.json();

        document.getElementById('dl_events').innerHTML = optionsData.events.map(e => `<option value="${e.name}">`).join('');
        document.getElementById('dl_users').innerHTML = optionsData.users.map(u => `<option value="${u.fio}">`).join('');
        document.getElementById('dl_levels').innerHTML = optionsData.levels.map(l => `<option value="${l.name}">`).join('');


        if (optionsData.groups) {
            document.getElementById('dl_groups').innerHTML = optionsData.groups.map(g => `<option value="${g.name}">`).join('');
        }
    } catch (err) { console.error('Не удалось загрузить списки:', err); }
}

// Автозаполнение зависимых полей
function setupAutoFill() {
    document.getElementById('m_name').addEventListener('change', function() {
        const ev = optionsData.events.find(e => e.name === this.value);
        if (ev) {
            document.getElementById('m_level').value = ev.level;
            document.getElementById('m_date').value = ev.date;
        }
    });

    document.getElementById('m_fio').addEventListener('change', function() {
        const usr = optionsData.users.find(u => u.fio === this.value);
        if (usr && USER_TYPE === 'stud') {
            document.getElementById('m_group').value = usr.group || '';
        }
    });
}

// Открытие модалки (Добавление)
function openAddModal() {
    document.getElementById('editId').value = '';
    document.getElementById('modalTitle').innerText = 'Добавить мероприятие';
    document.getElementById('eventForm').reset();
    loadOptions().then(setupAutoFill); // Загружаем списки и вешаем обработчики
    showModal();
}

// Открытие модалки (Редактирование)
async function openEditModal(id) {
    document.getElementById('editId').value = id;
    document.getElementById('modalTitle').innerText = 'Редактировать мероприятие';
    document.getElementById('eventForm').reset();
    showModal();

    try {
        const res = await fetch(`${API_BASE}/${id}`);
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
        }

        // Загружаем опции для редактирования (чтобы можно было сменить на другое существующее)
        await loadOptions();
        setupAutoFill();
    } catch (err) { alert('Ошибка загрузки данных'); }
}

// Сохранение (POST / PUT)
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
    if (USER_TYPE === 'stud') payload.group = document.getElementById('m_group').value;

    const id = document.getElementById('editId').value;
    const url = id ? `${API_BASE}/${id}` : API_BASE;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ошибка сохранения');
        hideModal(); loadTable();
    } catch (err) { alert(err.message); }
}

// Удаление
async function deleteEvent(id) {
    if (!confirm('Удалить запись?')) return;
    try {
        const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
        if (res.ok) loadTable(); else alert('Ошибка удаления');
    } catch { alert('Ошибка сети'); }
}

// Управление модалкой (Bootstrap 5)
function showModal() {
    if (typeof bootstrap !== 'undefined') new bootstrap.Modal(document.getElementById('eventModal')).show();
    else { document.getElementById('eventModal').style.display = 'block'; }
}
function hideModal() {
    if (typeof bootstrap !== 'undefined') {
        const m = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
        if (m) m.hide();
    } else { document.getElementById('eventModal').style.display = 'none'; }
}