document.addEventListener('DOMContentLoaded', () => {
    const createCompanyForm = document.getElementById('createCompanyForm');
    const modalOverlay = document.getElementById('companyModal');
    const modalClose = modalOverlay?.querySelector('[data-action="close-modal"]');
    const modalClientForm = document.getElementById('modalClientForm');
    const logoUploadForm = document.getElementById('logoUploadForm');

    if (createCompanyForm) {
        createCompanyForm.addEventListener('submit', handleCompanyCreate);
    }

    document.querySelectorAll('.company-entry').forEach(entry => {
        entry.addEventListener('click', () => openCompanyModal(JSON.parse(entry.dataset.company)));
    });

    modalClose?.addEventListener('click', closeCompanyModal);
    modalOverlay?.addEventListener('click', event => {
        if (event.target === modalOverlay) {
            closeCompanyModal();
        }
    });

    if (modalClientForm) {
        modalClientForm.addEventListener('submit', handleClientCreate);
    }

    if (logoUploadForm) {
        logoUploadForm.addEventListener('submit', handleLogoUpload);
    }
});

let activeCompany = null;

function handleCompanyCreate(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    toggleButtonLoading(submitButton, true);

    const formData = new FormData(form);

    fetch('/companies/', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => window.location.reload(), 800);
            } else {
                showNotification(data.message || 'Não foi possível criar a empresa.', 'error');
            }
        })
        .catch(() => {
            showNotification('Erro inesperado ao criar empresa.', 'error');
        })
        .finally(() => {
            toggleButtonLoading(submitButton, false);
        });
}

function openCompanyModal(companyData) {
    activeCompany = companyData;
    const modalOverlay = document.getElementById('companyModal');
    if (!modalOverlay) return;

    renderCompanyModal();
    modalOverlay.classList.add('active');
    modalOverlay.setAttribute('aria-hidden', 'false');
}

function renderCompanyModal() {
    if (!activeCompany) return;

    const modalOverlay = document.getElementById('companyModal');
    const nameElement = document.getElementById('modalCompanyName');
    const descriptionElement = document.getElementById('modalCompanyDescription');
    const metaElement = document.getElementById('modalCompanyMeta');
    const logoPreview = document.getElementById('modalLogoPreview');
    const clientsContainer = document.getElementById('modalClients');
    const clientForm = document.getElementById('modalClientForm');
    const logoForm = document.getElementById('logoUploadForm');

    if (!modalOverlay || !nameElement || !metaElement || !clientsContainer || !clientForm) {
        return;
    }

    modalOverlay.dataset.companyId = activeCompany.id;
    nameElement.textContent = activeCompany.name;
    descriptionElement.textContent = activeCompany.description || 'Sem descrição cadastrada.';

    metaElement.innerHTML = '';
    const metaItems = [
        `Criada em ${activeCompany.createdAt}`,
        `${activeCompany.clients.length} cliente${activeCompany.clients.length === 1 ? '' : 's'}`
    ];
    metaItems.forEach(text => {
        const span = document.createElement('span');
        span.textContent = text;
        metaElement.appendChild(span);
    });

    if (logoPreview) {
        logoPreview.innerHTML = '';
        if (activeCompany.logoUrl) {
            const img = document.createElement('img');
            img.src = activeCompany.logoUrl;
            img.alt = `Logotipo ${activeCompany.name}`;
            logoPreview.appendChild(img);
        } else {
            logoPreview.textContent = activeCompany.name.slice(0, 2).toUpperCase();
        }
    }

    if (logoForm) {
        logoForm.reset();
    }

    renderClientList(clientsContainer);

    clientForm.reset();
}

function renderClientList(container) {
    container.innerHTML = '';

    if (!activeCompany.clients.length) {
        const empty = document.createElement('p');
        empty.className = 'form-note';
        empty.textContent = 'Nenhum cliente associado ainda.';
        container.appendChild(empty);
        return;
    }

    activeCompany.clients.forEach(client => {
        const pill = document.createElement('div');
        pill.className = 'client-pill';

        const info = document.createElement('div');
        info.className = 'client-meta';

        const name = document.createElement('strong');
        name.textContent = client.username;
        info.appendChild(name);

        const email = document.createElement('span');
        email.textContent = client.email;
        info.appendChild(email);

        const role = document.createElement('span');
        role.className = 'client-role';
        role.textContent = client.role.charAt(0).toUpperCase() + client.role.slice(1);

        const invited = document.createElement('span');
        invited.className = 'form-note';
        invited.textContent = `Desde ${client.invited_at}`;
        info.appendChild(invited);

        const actions = document.createElement('div');
        actions.className = 'client-actions';

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'icon-button remove-client';
        removeButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        `;
        removeButton.addEventListener('click', () => handleClientRemove(client.membership_id, pill));

        actions.appendChild(role);
        actions.appendChild(removeButton);

        pill.appendChild(info);
        pill.appendChild(actions);

        container.appendChild(pill);
    });
}

function closeCompanyModal() {
    const modalOverlay = document.getElementById('companyModal');
    if (!modalOverlay) return;
    modalOverlay.classList.remove('active');
    modalOverlay.setAttribute('aria-hidden', 'true');
    activeCompany = null;
}

function handleClientCreate(event) {
    event.preventDefault();
    if (!activeCompany) return;

    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    toggleButtonLoading(submitButton, true);

    const payload = {
        username: form.username.value,
        email: form.email.value,
        password: form.password.value,
        role: form.role.value
    };

    fetch(`/companies/${activeCompany.id}/clients`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                form.reset();
                activeCompany.clients.unshift({
                    membership_id: data.client.membership_id,
                    username: data.client.username,
                    email: data.client.email,
                    role: data.client.role,
                    invited_at: new Date(data.client.invited_at).toLocaleDateString('pt-BR')
                });
                renderCompanyModal();
            } else {
                showNotification(data.message || 'Não foi possível adicionar o cliente.', 'error');
            }
        })
        .catch(() => {
            showNotification('Erro inesperado ao adicionar cliente.', 'error');
        })
        .finally(() => {
            toggleButtonLoading(submitButton, false);
        });
}

function handleClientRemove(membershipId, element) {
    if (!activeCompany) return;

    const button = element.querySelector('button');
    if (!button) return;

    button.disabled = true;

    fetch(`/companies/${activeCompany.id}/clients/${membershipId}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                activeCompany.clients = activeCompany.clients.filter(client => client.membership_id !== membershipId);
                element.classList.add('fade-out');
                setTimeout(() => renderCompanyModal(), 250);
            } else {
                showNotification(data.message || 'Não foi possível remover o cliente.', 'error');
            }
        })
        .catch(() => {
            showNotification('Erro inesperado ao remover cliente.', 'error');
        })
        .finally(() => {
            button.disabled = false;
        });
}

function handleLogoUpload(event) {
    event.preventDefault();
    if (!activeCompany) return;

    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput || !fileInput.files.length) {
        showNotification('Selecione um arquivo de imagem antes de enviar.', 'warning');
        return;
    }

    toggleButtonLoading(submitButton, true);

    const formData = new FormData();
    formData.append('logo', fileInput.files[0]);

    fetch(`/companies/${activeCompany.id}/logo`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                activeCompany.logoUrl = data.logo_url;
                renderCompanyModal();
            } else {
                showNotification(data.message || 'Não foi possível atualizar o logotipo.', 'error');
            }
        })
        .catch(() => {
            showNotification('Erro inesperado ao atualizar o logotipo.', 'error');
        })
        .finally(() => {
            toggleButtonLoading(submitButton, false);
            form.reset();
        });
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
