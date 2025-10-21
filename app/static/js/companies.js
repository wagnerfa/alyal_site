document.addEventListener('DOMContentLoaded', () => {
    const createCompanyForm = document.getElementById('createCompanyForm');
    if (createCompanyForm) {
        createCompanyForm.addEventListener('submit', handleCompanyCreate);
    }

    document.querySelectorAll('.add-client-form').forEach(form => {
        form.addEventListener('submit', handleClientCreate);
    });

    document.querySelectorAll('.remove-client').forEach(button => {
        button.addEventListener('click', handleClientRemove);
    });
});

async function handleCompanyCreate(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    toggleButtonLoading(submitButton, true);

    const payload = {
        name: form.name.value,
        description: form.description.value
    };

    try {
        const response = await fetch('/companies/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => window.location.reload(), 700);
        } else {
            showNotification(data.message || 'Não foi possível criar a empresa.', 'error');
        }
    } catch (error) {
        showNotification('Erro inesperado ao criar empresa.', 'error');
    } finally {
        toggleButtonLoading(submitButton, false);
    }
}

async function handleClientCreate(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const url = form.dataset.url;

    toggleButtonLoading(submitButton, true);

    const payload = {
        username: form.username.value,
        email: form.email.value,
        password: form.password.value
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            form.reset();
            setTimeout(() => window.location.reload(), 700);
        } else {
            showNotification(data.message || 'Não foi possível adicionar o cliente.', 'error');
        }
    } catch (error) {
        showNotification('Erro inesperado ao adicionar cliente.', 'error');
    } finally {
        toggleButtonLoading(submitButton, false);
    }
}

async function handleClientRemove(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const url = button.dataset.url;

    button.disabled = true;
    button.classList.add('loading');

    try {
        const response = await fetch(url, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            const clientItem = button.closest('.client-item');
            if (clientItem) {
                clientItem.classList.add('fade-out');
                setTimeout(() => {
                    clientItem.remove();
                    if (!button.closest('.client-list').querySelector('.client-item')) {
                        window.location.reload();
                    }
                }, 300);
            } else {
                window.location.reload();
            }
        } else {
            showNotification(data.message || 'Não foi possível remover o cliente.', 'error');
        }
    } catch (error) {
        showNotification('Erro inesperado ao remover cliente.', 'error');
    } finally {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

function toggleButtonLoading(button, isLoading) {
    if (!button) return;
    if (isLoading) {
        button.classList.add('loading');
        button.setAttribute('disabled', 'disabled');
    } else {
        button.classList.remove('loading');
        button.removeAttribute('disabled');
    }
}
