document.addEventListener('DOMContentLoaded', loadTable);

const USER_TYPE = window.USER_TYPE || 'ped';
const API_BASE = window.API_BASE || '/api/uchastiya/ped';

let optionsData = {
    users: [],
    events: [],
    levels: []
};

// ======================================
// ЗАГРУЗКА ТАБЛИЦЫ
// ======================================
async function loadTable() {

    const tbody = document.getElementById('table-body');
    const spinner = document.getElementById('loading');
    const table = document.getElementById('main-table');

    spinner.style.display = 'block';
    table.style.display = 'none';
    tbody.innerHTML = '';

    try {

        const res = await fetch(API_BASE);

        if (!res.ok) {
            throw new Error('Ошибка загрузки данных');
        }

        const data = await res.json();

        data.forEach(item => {

            let row = `
                <td>${item.id}</td>
                <td>${item.event_name}</td>
                <td>${item.event_level}</td>
                <td>${item.event_date}</td>
                <td>${item.user_name} | ${item.rezults}</td>
            `;

            // ДЛЯ СТУДЕНТОВ
            if (USER_TYPE === 'stud') {

                row += `
                    <td>${item.group || '-'}</td>
                    <td>${item.mentor || '-'}</td>
                `;
            }

            row += `
                <td>
                    <button class="btn btn-sm btn-warning mx-1"
                            onclick="openEditModal(${item.id})">
                        Ред.
                    </button>

                    <button class="btn btn-sm btn-danger mx-1"
                            onclick="deleteEvent(${item.id})">
                        Уд.
                    </button>
                </td>
            `;

            const tr = document.createElement('tr');
            tr.innerHTML = row;

            tbody.appendChild(tr);
        });

    } catch (err) {

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-danger text-center">
                    ${err.message}
                </td>
            </tr>
        `;

    } finally {

        spinner.style.display = 'none';
        table.style.display = 'table';
    }
}

// ======================================
// ЗАГРУЗКА ДАННЫХ ДЛЯ DATALIST
// ======================================
async function loadOptions() {

    try {

        const res = await fetch('/api/options');

        if (!res.ok) {
            throw new Error('Ошибка загрузки списков');
        }

        optionsData = await res.json();

        // МЕРОПРИЯТИЯ
        document.getElementById('dl_events').innerHTML =
            optionsData.events
                .map(e => `<option value="${e.name}">`)
                .join('');

        // УРОВНИ
        document.getElementById('dl_levels').innerHTML =
            optionsData.levels
                .map(l => `<option value="${l.name}">`)
                .join('');

        // ======================================
        // ПОЛЬЗОВАТЕЛИ
        // ======================================

        // ПЕДАГОГИ
        const teachers = optionsData.users.filter(
            u => !u.group || u.group.trim() === ''
        );

        // СТУДЕНТЫ
        const students = optionsData.users.filter(
            u => u.group && u.group.trim() !== ''
        );

        // ЕСЛИ СТРАНИЦА СТУДЕНТОВ
        if (USER_TYPE === 'stud') {

            // ФИО = только студенты
            document.getElementById('dl_users').innerHTML =
                students
                    .map(u => `<option value="${u.fio}">`)
                    .join('');

            // Наставники = только преподаватели
            document.getElementById('dl_mentors').innerHTML =
                teachers
                    .map(u => `<option value="${u.fio}">`)
                    .join('');

            // Группы
            if (optionsData.groups) {

                document.getElementById('dl_groups').innerHTML =
                    optionsData.groups
                        .map(g => `<option value="${g.name}">`)
                        .join('');
            }

        } else {

            // НА СТРАНИЦЕ ПЕДАГОГОВ
            // ФИО = только преподаватели
            document.getElementById('dl_users').innerHTML =
                teachers
                    .map(u => `<option value="${u.fio}">`)
                    .join('');
        }

    } catch (err) {

        console.error(err);
    }
}

// ======================================
// АВТОЗАПОЛНЕНИЕ
// ======================================
function setupAutoFill() {

    // АВТОЗАПОЛНЕНИЕ МЕРОПРИЯТИЯ
    document.getElementById('m_name').addEventListener('change', function () {

        const ev = optionsData.events.find(
            e => e.name === this.value
        );

        if (ev) {

            document.getElementById('m_level').value = ev.level;
            document.getElementById('m_date').value = ev.date;
        }
    });

    // АВТОГРУППА СТУДЕНТА
    const fioInput = document.getElementById('m_fio');

    fioInput.addEventListener('change', function () {

        const usr = optionsData.users.find(
            u => u.fio === this.value
        );

        if (usr && USER_TYPE === 'stud') {

            document.getElementById('m_group').value =
                usr.group || '';
        }
    });
}

// ======================================
// ДОБАВЛЕНИЕ
// ======================================
function openAddModal() {

    document.getElementById('editId').value = '';

    document.getElementById('modalTitle').innerText =
        'Добавить мероприятие';

    document.getElementById('eventForm').reset();

    loadOptions().then(() => {
        setupAutoFill();
    });

    showModal();
}

// ======================================
// РЕДАКТИРОВАНИЕ
// ======================================
async function openEditModal(id) {

    document.getElementById('editId').value = id;

    document.getElementById('modalTitle').innerText =
        'Редактировать мероприятие';

    document.getElementById('eventForm').reset();

    showModal();

    try {

        const res = await fetch(`${API_BASE}/${id}`);

        if (!res.ok) {
            throw new Error('Ошибка загрузки');
        }

        const item = await res.json();

        document.getElementById('m_name').value =
            item.event_name || '';

        document.getElementById('m_level').value =
            item.event_level || '';

        document.getElementById('m_date').value =
            item.event_date || '';

        document.getElementById('m_fio').value =
            item.user_name || '';

        document.getElementById('m_year').value =
            item.year || '';

        const parts = (item.rezults || '')
            .split(',')
            .map(s => s.trim());

        document.getElementById('m_result').value =
            parts[0] || '';

        document.getElementById('m_diploms').value =
            parts[1] || '';

        document.getElementById('m_awards').value =
            parts[2] || '';

        if (USER_TYPE === 'stud') {

            document.getElementById('m_group').value =
                item.group || '';

            document.getElementById('m_mentor').value =
                item.mentor || '';
        }

        await loadOptions();

        setupAutoFill();

    } catch (err) {

        alert(err.message);
    }
}

// ======================================
// СОХРАНЕНИЕ
// ======================================
async function saveEvent() {

    const payload = {

        event_name:
            document.getElementById('m_name').value,

        event_level:
            document.getElementById('m_level').value,

        event_date:
            document.getElementById('m_date').value,

        fio:
            document.getElementById('m_fio').value,

        rezultat:
            document.getElementById('m_result').value,

        diplomi:
            document.getElementById('m_diploms').value,

        nagradi:
            document.getElementById('m_awards').value,

        year:
            document.getElementById('m_year').value
    };

    // ДЛЯ СТУДЕНТОВ
    if (USER_TYPE === 'stud') {

        payload.group =
            document.getElementById('m_group').value;

        payload.mentor =
            document.getElementById('m_mentor').value;
    }

    const id = document.getElementById('editId').value;

    const url = id
        ? `${API_BASE}/${id}`
        : API_BASE;

    const method = id
        ? 'PUT'
        : 'POST';

    try {

        const res = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || 'Ошибка сохранения');
        }

        hideModal();

        loadTable();

    } catch (err) {

        alert(err.message);
    }
}

// ======================================
// УДАЛЕНИЕ
// ======================================
async function deleteEvent(id) {

    if (!confirm('Удалить запись?')) {
        return;
    }

    try {

        const res = await fetch(`${API_BASE}/${id}`, {
            method: 'DELETE'
        });

        if (res.ok) {

            loadTable();

        } else {

            alert('Ошибка удаления');
        }

    } catch {

        alert('Ошибка сети');
    }
}

// ======================================
// MODAL
// ======================================
function showModal() {

    if (typeof bootstrap !== 'undefined') {

        new bootstrap.Modal(
            document.getElementById('eventModal')
        ).show();

    } else {

        document.getElementById('eventModal').style.display = 'block';
    }
}

function hideModal() {

    if (typeof bootstrap !== 'undefined') {

        const modal = bootstrap.Modal.getInstance(
            document.getElementById('eventModal')
        );

        if (modal) {
            modal.hide();
        }

    } else {

        document.getElementById('eventModal').style.display = 'none';
    }
}