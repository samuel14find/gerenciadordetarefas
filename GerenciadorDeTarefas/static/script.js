/* script.js - Lógica Corrigida e Otimizada */

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Inicialização: Verifica o estado inicial das tarefas ao carregar ---
    // Isso garante que tarefas que já vieram 100% do banco de dados fiquem verdes/riscadas
    const allTasks = document.querySelectorAll('.task-item');
    allTasks.forEach(task => {
        updateProgressBar(task);
    });

    // --- 2. Lógica do Acordeão (Abrir/Fechar) ---
    const headers = document.querySelectorAll('.task-header');
    
    if (headers) { 
        headers.forEach(header => {
            header.addEventListener('click', (e) => {
                // Impede que o acordeão abra/feche se clicar em links ou inputs dentro do header
                if (e.target.closest('a') || e.target.closest('input') || e.target.closest('label')) return;

                const item = header.parentElement; 
                item.classList.toggle('active');
                
                // Gira o ícone
                const icon = header.querySelector('.accordion-icon');
                if(icon) {
                    // Se tiver a classe active, gira 180, senão volta pra 0
                    icon.style.transform = item.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                }
            });
        });
    }

    // --- 3. Lógica para adicionar novas etapas (se houver botão) ---
    const addBtn = document.getElementById('add-etapa-btn');
    if (addBtn) {
        const container = document.getElementById('etapas-container');
        const totalFormsInput = document.getElementById('id_etapas-TOTAL_FORMS');
        const emptyFormDiv = document.getElementById('empty-form');

        if (container && totalFormsInput && emptyFormDiv) {
            addBtn.addEventListener('click', function() {
                let formIdx = parseInt(totalFormsInput.value);
                let newFormHtml = emptyFormDiv.innerHTML.replace(/__prefix__/g, formIdx);
                let newDiv = document.createElement('div');
                newDiv.innerHTML = newFormHtml;
                container.appendChild(newDiv.firstElementChild);
                totalFormsInput.value = formIdx + 1;
            });
        }
    }
});

// --- Função Global chamada pelo onchange no HTML ---
function toggleStep(checkbox) {
    const etapaId = checkbox.getAttribute('data-etapa-id');
    const taskItem = checkbox.closest('.task-item');
    
    // 1. Atualiza visualmente a barra e o status de "concluída" imediatamente
    updateProgressBar(taskItem);

    // 2. Envia ao Backend (Django)
    const csrftoken = getCookie('csrftoken');

    fetch(`/tarefas/api/etapa/${etapaId}/toggle/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'sucesso') {
            // Atualiza o Badge de texto (Em andamento / Concluída)
            const statusBadge = taskItem.querySelector('.task-status');
            if (statusBadge) {
                statusBadge.textContent = data.tarefa_status;
                // Remove classes antigas e adiciona a nova cor baseada no retorno
                statusBadge.className = 'task-status'; 
                if(data.tarefa_status === 'Concluída') statusBadge.classList.add('status-concluida');
                else if(data.tarefa_status === 'Em Andamento') statusBadge.classList.add('status-em_andamento');
                else statusBadge.classList.add('status-nao_iniciado');

                // Toggle Archive Button
                if (data.tarefa_id) {
                    const archiveBtn = document.getElementById(`btn-archive-${data.tarefa_id}`);
                    if (archiveBtn) {
                        if (data.tarefa_status_code === 'concluida') {
                            archiveBtn.style.display = ''; // Shows the button
                        } else {
                            archiveBtn.style.display = 'none'; // Hides the button
                        }
                    }
                }
            }
        }
    })
    .catch(error => console.error('Erro na API:', error));
}

// --- Função Central de Cálculo Visual ---
function updateProgressBar(taskItem) {
    const allCheckboxes = taskItem.querySelectorAll('input[type="checkbox"]');
    const progressBar = taskItem.querySelector('.progress-bar-fill');
    const progressText = taskItem.querySelector('.progress-text');

    if (!progressBar || !progressText) return; 

    let checkedCount = 0;
    
    // Conta quantos estão marcados e aplica o risco individual na linha
    allCheckboxes.forEach(box => {
        const listItem = box.closest('.step-item');
        if(box.checked) {
            checkedCount++;
            if(listItem) listItem.classList.add('completed');
        } else {
            if(listItem) listItem.classList.remove('completed');
        }
    });

    const total = allCheckboxes.length;
    // Evita divisão por zero
    const percentage = total === 0 ? 0 : (checkedCount / total) * 100;

    // Atualiza largura e texto
    progressBar.style.width = percentage + '%';
    progressText.innerText = checkedCount + '/' + total;

    // --- LÓGICA CRUCIAL: Muda a cor do card inteiro se for 100% ---
    if (percentage === 100) {
        taskItem.classList.add('task-finished');
    } else {
        taskItem.classList.remove('task-finished');
    }
}

// Função Auxiliar do Django para pegar Cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}