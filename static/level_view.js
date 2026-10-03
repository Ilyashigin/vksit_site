document.addEventListener('DOMContentLoaded', loadLevels);

const API_URL = '/api/ur';
let currentLevelData = [];

const modalTitle = document.getElementById('modalTitle');
const form = document.getElementById('levelForm');

async function loadLevels() {
    const tableBody = document.getElementById('level-body');
    const loading = document.getElementById('loading-levels');
    const table = document.getElementById('level-table');

    loading.style.display = 'block';
    table.style.display = 'none';
    tableBody.innerHTML = '';

    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error('Ошибка загрузки данных');
        currentLevelData = await res.json();

        currentLevelData.forEach(level => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${level.id}</td>
                <td>${level.event_level}</td>
                <td class="table__actions">
                    <button class="btn btn--sm btn--warning" onclick="openLevelModal('edit', ${level.id})">Ред.</button>
                    <button class="btn btn--sm btn--danger" onclick="deleteLevel(${level.id})">Уд.</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="3" class="text-danger text-center">${err.message}</td></tr>`;
    } finally {
        loading.style.display = 'none';
        table.style.display = 'table';
    }
}

function openLevelModal(type, id = null) {
    form.reset();
    document.getElementById('editId').value = '';

    if (type === 'edit' && id) {
        const level = currentLevelData.find(l => l.id === id);
        if (level) {
            modalTitle.innerText = 'Редактировать уровень';
            document.getElementById('editId').value = level.id;
            document.getElementById('m_level').value = level.event_level;
        }
    } else {
        modalTitle.innerText = 'Добавить уровень';
    }

    openModal('levelModal');
}

async function saveLevel() {
    const id = document.getElementById('editId').value;
    const levelName = document.getElementById('m_level').value.trim();

    if (!levelName) {
        alert('Поле Название обязательно к заполнению');
        return;
    }

    const payload = { event_level: levelName };
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

        closeModal('levelModal');
        loadLevels();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteLevel(id) {
    if (!confirm('Вы уверены, что хотите удалить уровень?')) return;

    try {
        const res = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (res.ok) {
            loadLevels();
        } else {
            const data = await res.json();
            alert(data.error || 'Ошибка при удалении');
        }
    } catch (err) {
        alert('Ошибка сети: ' + err.message);
    }
}
