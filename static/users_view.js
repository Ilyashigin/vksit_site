const API_URL = '/api/user';
let currentUserData = [];
let optionsData = { groups: [] };

const modalEl = document.getElementById('userModal');
const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('userForm');
const datalistGroups = document.getElementById('dl_groups');
const groupField = document.getElementById('groupField');
const userRoleInput = document.getElementById('userRole');

async function loadOptions() {
    try {
        const res = await fetch('/api/options');
        if (!res.ok) throw new Error('Ошибка загрузки списков');
        optionsData = await res.json();

        if (datalistGroups && optionsData.groups) {
            datalistGroups.innerHTML = optionsData.groups
                .map(g => `<option value="${g.name || g}">`)
                .join('');
        }
    } catch (err) {
        console.warn('Не удалось загрузить подсказки для групп:', err);
    }
}

async function loadUsers() {
    const staffBody = document.getElementById('staff-body');
    const studentBody = document.getElementById('student-body');
    const loadStaff = document.getElementById('loading-staff');
    const loadStudent = document.getElementById('loading-students');
    const staffTable = document.getElementById('staff-table');
    const studentTable = document.getElementById('student-table');

    loadStaff.style.display = 'block';
    loadStudent.style.display = 'block';
    staffTable.style.display = 'none';
    studentTable.style.display = 'none';
    staffBody.innerHTML = '';
    studentBody.innerHTML = '';

    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error('Ошибка загрузки данных');
        currentUserData = await res.json();

        currentUserData.forEach(u => {
            const isStudent = u.group && u.group.toString().trim() !== '';
            const targetBody = isStudent ? studentBody : staffBody;
            const userJson = JSON.stringify(u).replace(/"/g, '&quot;');

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${u.id}</td>
                <td>${u.fio}</td>
                ${isStudent ? `<td>${u.group}</td>` : ''}
                <td class="table__actions">
                    <button class="btn btn--sm btn--secondary" onclick="viewUserEvents(${u.id})">Просмотр</button>
                    <button class="btn btn--sm btn--warning" onclick="openUserModal('edit', ${u.id})">Ред.</button>
                    <button class="btn btn--sm btn--danger" onclick="deleteUser(${u.id})">Уд.</button>
                </td>
            `;
            targetBody.appendChild(row);
        });
    } catch (err) {
        staffBody.innerHTML = `<tr><td colspan="3" class="text-danger text-center">${err.message}</td></tr>`;
        studentBody.innerHTML = `<tr><td colspan="4" class="text-danger text-center">${err.message}</td></tr>`;
    } finally {
        loadStaff.style.display = 'none';
        loadStudent.style.display = 'none';
        staffTable.style.display = 'table';
        studentTable.style.display = 'table';
    }
}

function setRoleFields(role) {
    userRoleInput.value = role;
    const groupInput = document.getElementById('m_group');

    if (role === 'teacher') {
        groupField.classList.add('form-group--hidden');
        groupInput.value = '';
        groupInput.removeAttribute('required');
    } else {
        groupField.classList.remove('form-group--hidden');
        groupInput.setAttribute('required', 'required');
    }
}

function openUserModal(type, id = null, role = 'teacher') {
    form.reset();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const user = currentUserData.find(u => u.id === id);
        if (user) {
            const isStudent = user.group && user.group.toString().trim() !== '';
            setRoleFields(isStudent ? 'student' : 'teacher');
            modalTitle.innerText = 'Редактировать участника';
            document.getElementById('editId').value = user.id;
            document.getElementById('m_fio').value = user.fio;
            document.getElementById('m_group').value = user.group || '';
        }
    } else {
        setRoleFields(role);
        modalTitle.innerText = role === 'student'
            ? 'Добавить студента'
            : 'Добавить преподавателя';
    }

    openModal('userModal');
}

function viewUserEvents(id) {
    const user = currentUserData.find(u => u.id === id);
    if (!user) return;

    const isStudent = user.group && user.group.toString().trim() !== '';
    if (isStudent) {
        const params = new URLSearchParams({ fio: user.fio, group: user.group });
        location.href = `/students?${params.toString()}`;
    } else {
        location.href = `/rabotniki?fio=${encodeURIComponent(user.fio)}`;
    }
}

async function saveUser() {
    const id = document.getElementById('editId').value;
    const fio = document.getElementById('m_fio').value.trim();
    const role = userRoleInput.value;
    const groupRaw = document.getElementById('m_group').value.trim();

    if (!fio) {
        alert('Поле ФИО обязательно к заполнению');
        return;
    }

    if (role === 'student' && !groupRaw) {
        alert('Поле Группа обязательно к заполнению');
        return;
    }

    const payload = { fio };
    if (role === 'student') payload.group = groupRaw;

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

        closeModal('userModal');
        loadUsers();
    } catch (err) {
        alert(err.message);
    }
}

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

document.addEventListener('DOMContentLoaded', async () => {
    await loadOptions();
    await loadUsers();
});
