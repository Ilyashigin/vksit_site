document.addEventListener('DOMContentLoaded', loadUsers);

const API_URL = '/api/user';
let currentUserData = [];

// 1. Загрузка и разделение данных
async function loadUsers() {
    const staffBody = document.getElementById('staff-body');
    const studentBody = document.getElementById('student-body');
    const loadStaff = document.getElementById('loading-staff');
    const loadStudent = document.getElementById('loading-students');
    const staffTable = document.getElementById('staff-table');
    const studentTable = document.getElementById('student-table');

    loadStaff.style.display = 'block'; loadStudent.style.display = 'block';
    staffTable.style.display = 'none'; studentTable.style.display = 'none';
    staffBody.innerHTML = ''; studentBody.innerHTML = '';

    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error('Ошибка загрузки данных');
        currentUserData = await res.json();

        currentUserData.forEach(u => {
            // Если есть группа и она не пустая → студент, иначе → преподаватель
            const isStudent = u.group && u.group.toString().trim() !== '';
            const targetBody = isStudent ? studentBody : staffBody;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${u.id}</td>
                <td>${u.fio}</td>
                ${isStudent ? `<td>${u.group}</td>` : ''}
                <td class="text-end">
                    <button class="btn btn-sm btn-warning" onclick="openModal('edit', ${u.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${u.id})">🗑️</button>
                </td>
            `;
            targetBody.appendChild(row);
        });
    } catch (err) {
        staffBody.innerHTML = `<tr><td colspan="3" class="text-danger text-center">${err.message}</td></tr>`;
        studentBody.innerHTML = `<tr><td colspan="4" class="text-danger text-center">${err.message}</td></tr>`;
    } finally {
        loadStaff.style.display = 'none'; loadStudent.style.display = 'none';
        staffTable.style.display = 'table'; studentTable.style.display = 'table';
    }
}

// 2. Управление модальным окном
const modalEl = document.getElementById('userModal');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('userForm');

function openModal(type, id = null) {
    form.reset();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const user = currentUserData.find(u => u.id === id);
        if (user) {
            modalTitle.innerText = 'Редактировать участника';
            document.getElementById('editId').value = user.id;
            document.getElementById('m_fio').value = user.fio;
            document.getElementById('m_group').value = user.group || '';
        }
    } else {
        modalTitle.innerText = 'Добавить участника';
    }

    // Bootstrap 5 modal show
    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Modal(modalEl).show();
    } else {
        modalEl.style.display = 'block';
        modalEl.classList.add('show');
    }
}

// 3. Сохранение (POST / PUT)
async function saveUser() {
    const id = document.getElementById('editId').value;
    const fio = document.getElementById('m_fio').value.trim();
    const groupRaw = document.getElementById('m_group').value.trim();
    const group = groupRaw !== '' ? groupRaw : null;

    if (!fio) { alert('Поле ФИО обязательно к заполнению'); return; }

    const payload = { fio: fio };
    if (group) payload.group = group;

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
        loadUsers(); // Перерисовываем таблицы
    } catch (err) {
        alert(err.message);
    }
}

// 4. Удаление (DELETE)
async function deleteUser(id) {
    if (!confirm('Вы уверены, что хотите удалить этого участника?')) return;
    try {
        const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });

        if (res.ok) {
            loadUsers();
        } else {
            const data = await res.json();
            alert(data.error || 'Ошибка при удалении');
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
    }
}

// Вспомогательная функция скрытия модалки
function hideModal() {
    if (typeof bootstrap !== 'undefined') {
        const instance = bootstrap.Modal.getInstance(modalEl);
        if (instance) instance.hide();
    } else {
        modalEl.style.display = 'none';
    }
}