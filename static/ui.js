function openModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('modal--open');
    document.body.classList.add('modal-open');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('modal--open');
    document.body.classList.remove('modal-open');
}

function hideModal() {
    document.querySelectorAll('.modal.modal--open').forEach(modal => {
        closeModal(modal.id);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = btn.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    document.querySelectorAll('.modal__overlay').forEach(overlay => {
        overlay.addEventListener('click', () => {
            const modal = overlay.closest('.modal');
            if (modal) closeModal(modal.id);
        });
    });

    document.querySelectorAll('[data-dropdown-toggle]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const wrap = btn.closest('.dropdown');
            const menu = wrap ? wrap.querySelector('.dropdown__menu') : null;
            if (!menu) return;

            document.querySelectorAll('.dropdown__menu--open').forEach(item => {
                if (item !== menu) item.classList.remove('dropdown__menu--open');
            });
            menu.classList.toggle('dropdown__menu--open');
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown__menu--open').forEach(menu => {
            menu.classList.remove('dropdown__menu--open');
        });
    });
});
