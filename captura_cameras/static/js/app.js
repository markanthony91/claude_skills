// Dashboard de Câmeras - JavaScript
// Estado da aplicação
let cameras = [];
let filteredCameras = [];
let currentCameraId = null;

// Elementos do DOM
const elements = {
    loading: document.getElementById('loading'),
    emptyState: document.getElementById('emptyState'),
    camerasGrid: document.getElementById('camerasGrid'),
    resultsCounter: document.getElementById('resultsCounter'),
    resultsCount: document.getElementById('resultsCount'),

    // Stats
    statTotalCameras: document.getElementById('statTotalCameras'),
    statTotalStores: document.getElementById('statTotalStores'),
    statMarkedBad: document.getElementById('statMarkedBad'),
    statMarkedOk: document.getElementById('statMarkedOk'),
    statLastUpdate: document.getElementById('statLastUpdate'),

    // Filters
    filterVersion: document.getElementById('filterVersion'),
    filterStore: document.getElementById('filterStore'),
    filterQuality: document.getElementById('filterQuality'),
    filterStatus: document.getElementById('filterStatus'),
    filterPosition: document.getElementById('filterPosition'),
    searchInput: document.getElementById('searchInput'),
    btnClearFilters: document.getElementById('btnClearFilters'),

    // Buttons
    btnDownload: document.getElementById('btnDownload'),
    btnDownloadEmpty: document.getElementById('btnDownloadEmpty'),
    btnRefresh: document.getElementById('btnRefresh'),
    btnExport: document.getElementById('btnExport'),

    // Modals
    noteModal: document.getElementById('noteModal'),
    modalCameraName: document.getElementById('modalCameraName'),
    noteTextarea: document.getElementById('noteTextarea'),
    btnSaveNote: document.getElementById('btnSaveNote'),
    btnCancelNote: document.getElementById('btnCancelNote'),

    downloadModal: document.getElementById('downloadModal'),
    downloadStatus: document.getElementById('downloadStatus'),

    imageModal: document.getElementById('imageModal'),
    imagePreview: document.getElementById('imagePreview'),
    imageInfoText: document.getElementById('imageInfoText'),

    toastContainer: document.getElementById('toastContainer')
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    setupEventListeners();
    await loadStores();
    await loadCameras();
    await loadStats();
}

// Event Listeners
function setupEventListeners() {
    // Buttons
    elements.btnDownload.addEventListener('click', startDownload);
    elements.btnDownloadEmpty.addEventListener('click', startDownload);
    elements.btnRefresh.addEventListener('click', () => {
        loadCameras();
        loadStats();
    });
    elements.btnExport.addEventListener('click', exportMarkedCameras);

    // Filters
    elements.filterVersion.addEventListener('change', applyFilters);
    elements.filterStore.addEventListener('change', applyFilters);
    elements.filterQuality.addEventListener('change', applyFilters);
    elements.filterStatus.addEventListener('change', applyFilters);
    elements.filterPosition.addEventListener('change', applyFilters);
    elements.searchInput.addEventListener('input', applyFilters);
    elements.btnClearFilters.addEventListener('click', clearFilters);

    // Note Modal
    elements.btnSaveNote.addEventListener('click', saveNote);
    elements.btnCancelNote.addEventListener('click', closeNoteModal);

    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    // Click fora do modal fecha
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
}

// Carregar câmeras
async function loadCameras() {
    showLoading(true);

    try {
        const response = await fetch('/api/cameras');
        const data = await response.json();

        if (data.success) {
            cameras = data.cameras;
            applyFilters();

            if (cameras.length === 0) {
                showEmptyState();
            }
        } else {
            showToast('Erro ao carregar câmeras', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    } finally {
        showLoading(false);
    }
}

// Carregar lojas
async function loadStores() {
    try {
        const response = await fetch('/api/stores');
        const data = await response.json();

        if (data.success) {
            const stores = data.stores;

            // Limpar opções existentes (exceto "Todas as Lojas")
            elements.filterStore.innerHTML = '<option value="all">Todas as Lojas</option>';

            // Adicionar opções de lojas
            stores.forEach(store => {
                const option = document.createElement('option');
                option.value = store;
                option.textContent = store;
                elements.filterStore.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar lojas:', error);
    }
}

// Carregar estatísticas
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;

            elements.statTotalCameras.textContent = stats.total_cameras;
            elements.statTotalStores.textContent = stats.total_stores;
            elements.statMarkedBad.textContent = stats.marked_bad;
            elements.statMarkedOk.textContent = stats.marked_ok;

            if (stats.last_update) {
                const date = new Date(stats.last_update);
                elements.statLastUpdate.textContent = formatTimeAgo(date);
            } else {
                elements.statLastUpdate.textContent = 'Nunca';
            }
        }
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

// Aplicar filtros
function applyFilters() {
    const versionFilter = elements.filterVersion.value;
    const storeFilter = elements.filterStore.value;
    const qualityFilter = elements.filterQuality.value;
    const statusFilter = elements.filterStatus.value;
    const positionFilter = elements.filterPosition.value;
    const searchTerm = elements.searchInput.value.toLowerCase().trim();

    filteredCameras = cameras.filter(camera => {
        // Filtro de versão (últimas vs todas)
        if (versionFilter === 'latest' && !camera.is_latest) return false;

        // Filtro de loja específica
        if (storeFilter !== 'all' && camera.loja !== storeFilter) return false;

        // Filtro de qualidade (análise IA) - 5 níveis
        if (qualityFilter !== 'all') {
            const score = getCameraScore(camera.base_id);

            if (qualityFilter === 'excellent') {
                // Excelentes (≥90%)
                if (score === null || score < 90) return false;
            } else if (qualityFilter === 'good') {
                // Boas (≥85%)
                if (score === null || score < 85) return false;
            } else if (qualityFilter === 'attention') {
                // Atenção (70-84%)
                if (score === null || score < 70 || score >= 85) return false;
            } else if (qualityFilter === 'problems') {
                // Problemas (50-69%)
                if (score === null || score < 50 || score >= 70) return false;
            } else if (qualityFilter === 'critical') {
                // Críticas (<50%)
                if (score === null || score >= 50) return false;
            } else if (qualityFilter === 'not_analyzed') {
                // Não analisadas
                if (score !== null) return false;
            }
        }

        // Filtro de status manual
        if (statusFilter === 'ok' && camera.marked) return false;
        if (statusFilter === 'bad' && !camera.marked) return false;

        // Filtro de posição
        if (positionFilter !== 'all' && camera.position !== positionFilter) return false;

        // Filtro de busca rápida (adicional ao filtro de loja)
        if (searchTerm && !camera.loja.toLowerCase().includes(searchTerm)) return false;

        return true;
    });

    renderCameras();
}

// Renderizar câmeras em 3 colunas (P1, P2, P3)
function renderCameras() {
    if (filteredCameras.length === 0 && cameras.length > 0) {
        // Tem câmeras mas nenhuma passa nos filtros
        elements.camerasGrid.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
                <h3>Nenhuma câmera encontrada</h3>
                <p style="color: var(--text-secondary);">Tente ajustar os filtros</p>
            </div>
        `;
        elements.camerasGrid.style.display = 'flex';
        elements.resultsCounter.style.display = 'none';
        return;
    }

    elements.camerasGrid.innerHTML = '';

    // Agrupar câmeras por loja
    const storeGroups = {};
    filteredCameras.forEach(camera => {
        if (!storeGroups[camera.loja]) {
            storeGroups[camera.loja] = {
                P1: null,
                P2: null,
                P3: null
            };
        }
        // Sempre pegar a mais recente se houver múltiplas
        if (!storeGroups[camera.loja][camera.position] || camera.is_latest) {
            storeGroups[camera.loja][camera.position] = camera;
        }
    });

    // Ordenar lojas alfabeticamente
    const sortedStores = Object.keys(storeGroups).sort();

    // Criar uma linha para cada loja
    sortedStores.forEach(storeName => {
        const storeRow = document.createElement('div');
        storeRow.className = 'store-row';

        // Header da loja
        const storeHeader = document.createElement('div');
        storeHeader.className = 'store-header';
        storeHeader.innerHTML = `<h3 class="store-name">${escapeHtml(storeName)}</h3>`;
        storeRow.appendChild(storeHeader);

        // Container das 3 colunas
        const cameraColumns = document.createElement('div');
        cameraColumns.className = 'camera-columns';

        // Obter filtro de posição
        const positionFilter = elements.filterPosition.value;

        // Criar colunas para P1, P2, P3
        ['P1', 'P2', 'P3'].forEach(position => {
            const column = document.createElement('div');
            column.className = 'camera-column';

            // Aplicar destaque se filtro de posição estiver ativo
            if (positionFilter !== 'all') {
                if (position !== positionFilter) {
                    column.classList.add('dimmed');
                }
            }

            // Header da coluna
            const columnHeader = document.createElement('div');
            columnHeader.className = 'column-header';
            if (positionFilter === position) {
                columnHeader.classList.add('highlighted');
            }
            columnHeader.textContent = position;
            column.appendChild(columnHeader);

            // Card da câmera ou mensagem de vazio
            const camera = storeGroups[storeName][position];
            if (camera) {
                const card = createCameraCard(camera);
                column.appendChild(card);
            } else {
                const emptyDiv = document.createElement('div');
                emptyDiv.className = 'column-empty';
                emptyDiv.textContent = 'Sem câmera';
                column.appendChild(emptyDiv);
            }

            cameraColumns.appendChild(column);
        });

        storeRow.appendChild(cameraColumns);
        elements.camerasGrid.appendChild(storeRow);
    });

    elements.camerasGrid.style.display = 'flex';
    elements.resultsCounter.style.display = 'block';
    elements.resultsCount.textContent = `${sortedStores.length} lojas`;
}

// Criar card de câmera
function createCameraCard(camera) {
    const card = document.createElement('div');
    card.className = `camera-card ${camera.marked ? 'marked' : ''}`;

    const markedBadge = camera.marked ? '<span class="camera-badge marked-badge">⚠️ Ruim</span>' : '';

    // Badge de versão antiga (só mostra quando filtro está em "Todas as Versões")
    const versionBadge = !camera.is_latest && elements.filterVersion.value === 'all'
        ? '<span class="camera-badge version-badge">📚 Antiga</span>'
        : '';

    // Badge de score de similaridade (se disponível)
    const score = getCameraScore(camera.base_id);
    let scoreBadge = '';
    if (score !== null) {
        const scoreClass = score >= 85 ? 'high' : score >= 70 ? 'medium' : 'low';
        scoreBadge = `<span class="camera-score ${scoreClass}">${score}%</span>`;
    }

    const noteSection = camera.marked && camera.mark_info.note ? `
        <div class="camera-note">
            <div class="camera-note-label">Nota:</div>
            <div class="camera-note-text">${escapeHtml(camera.mark_info.note)}</div>
        </div>
    ` : '';

    // Seção de metadados adicionais (Lugar, Área, UUID, IPs, etc.)
    let metadataSection = '';
    if (camera.metadata) {
        const meta = camera.metadata;
        metadataSection = `
        <div class="camera-metadata">
            ${meta.lugar ? `<div class="metadata-item"><strong>Lugar:</strong> ${escapeHtml(meta.lugar)}</div>` : ''}
            ${meta.area ? `<div class="metadata-item"><strong>Área:</strong> ${escapeHtml(meta.area)}</div>` : ''}
            ${meta.ip_local ? `<div class="metadata-item"><strong>IP Local:</strong> ${escapeHtml(meta.ip_local)}</div>` : ''}
            ${meta.ip_internet ? `<div class="metadata-item"><strong>IP Internet:</strong> ${escapeHtml(meta.ip_internet)}</div>` : ''}
            ${meta.versao_sistema ? `<div class="metadata-item"><strong>Versão:</strong> ${escapeHtml(meta.versao_sistema)}</div>` : ''}
            ${meta.temperatura_cpu ? `<div class="metadata-item"><strong>CPU:</strong> ${escapeHtml(meta.temperatura_cpu)}°C</div>` : ''}
            ${meta.uuid ? `<div class="metadata-item"><strong>UUID:</strong> <small>${escapeHtml(meta.uuid)}</small></div>` : ''}
        </div>
        `;
    }

    // Badge de status online/offline
    let onlineStatusBadge = '';
    if (camera.online !== null && camera.online !== undefined) {
        if (camera.online) {
            onlineStatusBadge = '<span class="online-badge online">🟢 Online</span>';
        } else {
            onlineStatusBadge = '<span class="online-badge offline">🔴 Offline</span>';
        }
    }

    card.innerHTML = `
        <div class="camera-image-container">
            <img src="/${camera.path}" alt="${camera.loja} - ${camera.position}" class="camera-image" loading="lazy">
            ${scoreBadge}
            <span class="camera-badge">${camera.position}</span>
            ${markedBadge}
            ${versionBadge}
        </div>
        <div class="camera-info">
            <div class="camera-header">
                <div>
                    <div class="camera-title">
                        ${escapeHtml(camera.loja)}
                        ${onlineStatusBadge}
                    </div>
                    <div class="camera-position">Câmera ${camera.position}</div>
                </div>
                <div class="camera-actions">
                    <button class="btn-icon" title="Ver imagem" onclick="previewImage('${camera.id}')">
                        🔍
                    </button>
                    ${score !== null ?
                        `<button class="btn-icon" title="Comparar com referência" onclick="compareCamera('${camera.base_id}')">🔬</button>` :
                        ''
                    }
                    ${camera.marked ?
                        `<button class="btn-icon" title="Desmarcar" onclick="unmarkCamera('${camera.base_id}')">✅</button>` :
                        `<button class="btn-icon" title="Marcar como ruim" onclick="markCamera('${camera.base_id}')">⚠️</button>`
                    }
                </div>
            </div>
            ${noteSection}
            ${metadataSection}
            <div class="camera-meta">
                Atualizada: ${camera.modified_readable}
            </div>
        </div>
    `;

    return card;
}

// Marcar câmera como ruim
function markCamera(baseId) {
    currentCameraId = baseId;
    const camera = cameras.find(c => c.base_id === baseId);

    if (camera) {
        elements.modalCameraName.textContent = `${camera.loja} - ${camera.position}`;
        elements.noteTextarea.value = '';
        openNoteModal();
    }
}

// Salvar nota e marcar câmera
async function saveNote() {
    const note = elements.noteTextarea.value.trim();

    try {
        const response = await fetch(`/api/cameras/${currentCameraId}/mark`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ note })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Câmera marcada como ruim', 'success');
            closeNoteModal();
            await loadCameras();
            await loadStats();
        } else {
            showToast('Erro ao marcar câmera', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    }
}

// Desmarcar câmera
async function unmarkCamera(cameraId) {
    try {
        const response = await fetch(`/api/cameras/${cameraId}/unmark`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Marcação removida', 'success');
            await loadCameras();
            await loadStats();
        } else {
            showToast('Erro ao desmarcar câmera', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    }
}

// Preview de imagem
function previewImage(cameraId) {
    const camera = cameras.find(c => c.id === cameraId);

    if (camera) {
        elements.imagePreview.src = `/${camera.path}`;
        elements.imageInfoText.textContent = `${camera.loja} - ${camera.position} | ${camera.modified_readable}`;
        openImageModal();
    }
}

// Iniciar download
async function startDownload() {
    openDownloadModal();

    try {
        const response = await fetch('/api/download/start', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            // Monitorar progresso via SSE
            monitorDownloadSSE();
        } else {
            showToast(data.message || 'Erro ao iniciar download', 'error');
            closeDownloadModal();
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
        closeDownloadModal();
    }
}

// Monitorar progresso do download via Server-Sent Events
function monitorDownloadSSE() {
    const eventSource = new EventSource('/api/download/status-stream');

    // Elementos do DOM
    const statusText = document.getElementById('downloadStatus');
    const cameraText = document.getElementById('downloadCurrentCamera');
    const progressBar = document.getElementById('downloadProgressBar');
    const progressPercent = document.getElementById('downloadProgressPercent');
    const progressCount = document.getElementById('downloadProgressCount');
    const successCount = document.getElementById('downloadSuccess');
    const failedCount = document.getElementById('downloadFailed');
    const btnClose = document.getElementById('btnCloseDownload');

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);

            // Verificar se terminou
            if (data.done) {
                eventSource.close();
                statusText.textContent = '✅ Download concluído!';
                cameraText.textContent = '';
                btnClose.style.display = 'block';

                showToast(`Download concluído! ${data.sucesso || 0} sucessos, ${data.falha || 0} falhas`, 'success');

                // Recarregar dados
                setTimeout(async () => {
                    await loadCameras();
                    await loadStats();
                }, 1000);

                return;
            }

            // Atualizar UI com progresso
            const { running, progresso, total, atual, sucesso, falha } = data;

            if (running) {
                statusText.textContent = '📥 Baixando imagens...';
                cameraText.textContent = atual || '';

                // Atualizar barra de progresso
                progressBar.style.width = `${progresso}%`;
                progressPercent.textContent = `${progresso}%`;
                progressCount.textContent = `${sucesso + falha} / ${total}`;

                // Atualizar estatísticas
                successCount.textContent = sucesso;
                failedCount.textContent = falha;
            }

        } catch (error) {
            console.error('Erro ao processar evento SSE:', error);
        }
    };

    eventSource.onerror = function(error) {
        console.error('Erro no SSE:', error);
        eventSource.close();
        statusText.textContent = '❌ Erro no download';
        btnClose.style.display = 'block';
        showToast('Erro durante o download', 'error');
    };

    // Fechar conexão SSE quando fechar modal
    btnClose.addEventListener('click', () => {
        eventSource.close();
        closeDownloadModal();
    }, { once: true });
}

// Exportar câmeras marcadas
async function exportMarkedCameras() {
    try {
        const response = await fetch('/api/export/marked');
        const data = await response.json();

        if (data.success) {
            if (data.total === 0) {
                showToast('Nenhuma câmera marcada para exportar', 'warning');
                return;
            }

            // Criar CSV
            let csv = 'Loja,Posição,Arquivo,Marcada em,Nota\n';

            data.cameras.forEach(camera => {
                const loja = camera.loja.replace(/,/g, ';');
                const note = (camera.note || '').replace(/,/g, ';').replace(/\n/g, ' ');
                const markedAt = new Date(camera.marked_at).toLocaleString('pt-BR');

                csv += `${loja},${camera.position},${camera.filename},${markedAt},${note}\n`;
            });

            // Download do arquivo
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `cameras_ruins_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();
            URL.revokeObjectURL(url);

            showToast(`${data.total} câmeras exportadas`, 'success');
        } else {
            showToast('Erro ao exportar', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com o servidor', 'error');
    }
}

// Limpar filtros
function clearFilters() {
    elements.filterVersion.value = 'latest';
    elements.filterStore.value = 'all';
    elements.filterQuality.value = 'all';
    elements.filterStatus.value = 'all';
    elements.filterPosition.value = 'all';
    elements.searchInput.value = '';
    applyFilters();
}

// Modals
function openNoteModal() {
    elements.noteModal.classList.add('active');
}

function closeNoteModal() {
    elements.noteModal.classList.remove('active');
    currentCameraId = null;
}

function openDownloadModal() {
    elements.downloadModal.classList.add('active');
}

function closeDownloadModal() {
    elements.downloadModal.classList.remove('active');
}

function openImageModal() {
    elements.imageModal.classList.add('active');
}

function closeImageModal() {
    elements.imageModal.classList.remove('active');
}

function closeAllModals() {
    closeNoteModal();
    closeDownloadModal();
    closeImageModal();
}

// UI Helpers
function showLoading(show) {
    elements.loading.style.display = show ? 'flex' : 'none';
    if (!show) {
        elements.emptyState.style.display = 'none';
    }
}

function showEmptyState() {
    elements.loading.style.display = 'none';
    elements.emptyState.style.display = 'block';
    elements.camerasGrid.style.display = 'none';
    elements.resultsCounter.style.display = 'none';
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };

    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || '📢'}</div>
        <div class="toast-message">${escapeHtml(message)}</div>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTimeAgo(date) {
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Agora mesmo';
    if (minutes < 60) return `há ${minutes} min`;
    if (hours < 24) return `há ${hours}h`;
    if (days < 7) return `há ${days} dias`;

    return date.toLocaleDateString('pt-BR');
}

// ==================== AI Analysis Functions ====================

// Estado da análise
let analysisCache = {};
let visionStatus = {
    available: false,
    referencesCount: 0
};

// Elementos adicionais para IA
elements.btnAiPanel = document.getElementById('btnAiPanel');
elements.aiPanel = document.getElementById('aiPanel');
elements.btnCloseAiPanel = document.getElementById('btnCloseAiPanel');
elements.btnAutoLearn = document.getElementById('btnAutoLearn');
elements.btnManualReference = document.getElementById('btnManualReference');
elements.btnAnalyzeAll = document.getElementById('btnAnalyzeAll');
elements.btnViewReferences = document.getElementById('btnViewReferences');
elements.btnClearReferences = document.getElementById('btnClearReferences');
elements.aiStatus = document.getElementById('aiStatus');
elements.aiReferencesCount = document.getElementById('aiReferencesCount');

// View References Modal Elements
elements.viewReferencesModal = document.getElementById('viewReferencesModal');
elements.btnCloseViewReferences = document.getElementById('btnCloseViewReferences');
elements.btnCloseViewReferencesFooter = document.getElementById('btnCloseViewReferencesFooter');
elements.viewReferencesGrid = document.getElementById('viewReferencesGrid');
elements.viewRefFilterStore = document.getElementById('viewRefFilterStore');
elements.viewRefFilterPosition = document.getElementById('viewRefFilterPosition');
elements.viewRefTotal = document.getElementById('viewRefTotal');

// Reference Modal Elements
elements.referenceModal = document.getElementById('referenceModal');
elements.btnCloseReferenceModal = document.getElementById('btnCloseReferenceModal');
elements.referenceGrid = document.getElementById('referenceGrid');
elements.refFilterStore = document.getElementById('refFilterStore');
elements.refFilterPosition = document.getElementById('refFilterPosition');
elements.refSelectedCount = document.getElementById('refSelectedCount');
elements.btnSaveReferences = document.getElementById('btnSaveReferences');
elements.btnCancelReferences = document.getElementById('btnCancelReferences');
elements.comparisonModal = document.getElementById('comparisonModal');
elements.btnCloseComparison = document.getElementById('btnCloseComparison');
elements.btnSetAsReference = document.getElementById('btnSetAsReference');

// Novos elementos para melhorias
elements.btnViewGrid = document.getElementById('btnViewGrid');
elements.btnViewByStore = document.getElementById('btnViewByStore');
elements.imageZoomModal = document.getElementById('imageZoomModal');
elements.zoomedImage = document.getElementById('zoomedImage');
elements.reviewReferencesModal = document.getElementById('reviewReferencesModal');
elements.btnCloseReviewModal = document.getElementById('btnCloseReviewModal');
elements.btnCloseReview = document.getElementById('btnCloseReview');
elements.reviewGrid = document.getElementById('reviewGrid');
elements.reviewTotalCount = document.getElementById('reviewTotalCount');

// Verificar status da visão ao iniciar
async function checkVisionStatus() {
    try {
        const response = await fetch('/api/vision/status');
        const data = await response.json();

        if (data.success) {
            visionStatus = {
                available: data.vision_available,
                referencesCount: data.references_count
            };

            if (data.vision_available) {
                elements.aiStatus.textContent = '✅ Disponível';
                elements.aiStatus.style.color = 'var(--success-color)';
            } else {
                elements.aiStatus.textContent = '⚠️ Instalar dependências';
                elements.aiStatus.style.color = 'var(--warning-color)';
            }

            elements.aiReferencesCount.textContent = data.references_count;
        }
    } catch (error) {
        console.error('Erro ao verificar status de visão:', error);
        elements.aiStatus.textContent = '❌ Indisponível';
        elements.aiStatus.style.color = 'var(--danger-color)';
    }
}

// Carregar cache de análises
async function loadAnalysisCache() {
    try {
        const response = await fetch('/api/vision/cache');
        const data = await response.json();

        if (data.success) {
            analysisCache = data.cache || {};
        }
    } catch (error) {
        console.error('Erro ao carregar cache:', error);
    }
}

// Auto-aprendizado
async function autoLearnReferences() {
    if (!visionStatus.available) {
        showToast('Sistema de visão não está disponível. Instale as dependências primeiro.', 'error');
        return;
    }

    if (!confirm('Isso irá usar as imagens mais recentes como referência para comparação. Continuar?')) {
        return;
    }

    elements.btnAutoLearn.disabled = true;
    elements.btnAutoLearn.innerHTML = '<span class="spinner"></span> Aprendendo...';

    try {
        const response = await fetch('/api/vision/auto-learn', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`${data.message}! Sistema pronto para análise.`, 'success');
            await checkVisionStatus();
            await loadAnalysisCache();
        } else {
            showToast(data.error || 'Erro ao aprender referências', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com servidor', 'error');
    } finally {
        elements.btnAutoLearn.disabled = false;
        elements.btnAutoLearn.innerHTML = '<span class="icon">🎓</span> Aprender Referências (Usar Últimas)';
    }
}

// Analisar todas as câmeras
async function analyzeAllCameras() {
    if (!visionStatus.available) {
        showToast('Sistema de visão não está disponível', 'error');
        return;
    }

    if (visionStatus.referencesCount === 0) {
        showToast('Nenhuma referência encontrada. Execute o auto-aprendizado primeiro.', 'warning');
        return;
    }

    // Obter modo de análise selecionado
    const selectedMode = document.querySelector('input[name="analysisMode"]:checked')?.value || 'complete';

    elements.btnAnalyzeAll.disabled = true;
    elements.btnAnalyzeAll.innerHTML = '<span class="spinner"></span> Analisando...';

    try {
        const response = await fetch('/api/vision/analyze-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_mode: selectedMode
            })
        });

        const data = await response.json();

        if (data.success) {
            // Recarregar cache primeiro
            await loadAnalysisCache();

            // Recarregar câmeras para mostrar scores
            await loadCameras();

            // Contar por nível de classificação
            const excellent = data.results.filter(r => r.score >= 90);
            const good = data.results.filter(r => r.score >= 85 && r.score < 90);
            const attention = data.results.filter(r => r.score >= 70 && r.score < 85);
            const problems = data.results.filter(r => r.score >= 50 && r.score < 70);
            const critical = data.results.filter(r => r.score < 50);

            // Mostrar relatório
            showAnalysisReport(data, {excellent, good, attention, problems, critical}, selectedMode);
        } else {
            showToast(data.error || 'Erro ao analisar', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com servidor', 'error');
    } finally {
        elements.btnAnalyzeAll.disabled = false;
        elements.btnAnalyzeAll.innerHTML = '<span class="icon">🔍</span> Analisar Todas as Câmeras';
    }
}

// Mostrar relatório de análise
function showAnalysisReport(data, levels, analysisMode = 'complete') {
    const total = data.analyzed;
    const {excellent, good, attention, problems, critical} = levels;

    const modeText = analysisMode === 'structural' ?
        '<div style="margin-bottom: 10px; padding: 8px; background: #f0f4ff; border-left: 3px solid #6366f1; border-radius: 4px; font-size: 13px;"><strong>Modo:</strong> Estrutural (apenas posição/ângulo da câmera)</div>' :
        '<div style="margin-bottom: 10px; padding: 8px; background: #f0f4ff; border-left: 3px solid #6366f1; border-radius: 4px; font-size: 13px;"><strong>Modo:</strong> Completo (detecta qualquer mudança)</div>';

    const issuesCount = problems.length + critical.length;

    let reportHTML = `
        <div style="padding: 20px;">
            <h3 style="margin-bottom: 15px;">📊 Relatório de Análise Detalhado</h3>
            ${modeText}

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;">
                <div style="padding: 12px; background: #fef9c3; border-radius: 8px; text-align: center; border: 2px solid #fde047;">
                    <div style="font-size: 24px; font-weight: bold; color: #854d0e;">🌟 ${excellent.length}</div>
                    <div style="font-size: 11px; color: #713f12;">Excelentes (≥90%)</div>
                </div>
                <div style="padding: 12px; background: #dcfce7; border-radius: 8px; text-align: center; border: 2px solid #86efac;">
                    <div style="font-size: 24px; font-weight: bold; color: #15803d;">✅ ${good.length}</div>
                    <div style="font-size: 11px; color: #166534;">Boas (85-89%)</div>
                </div>
                <div style="padding: 12px; background: #fed7aa; border-radius: 8px; text-align: center; border: 2px solid #fdba74;">
                    <div style="font-size: 24px; font-weight: bold; color: #c2410c;">⚠️ ${attention.length}</div>
                    <div style="font-size: 11px; color: #9a3412;">Atenção (70-84%)</div>
                </div>
                <div style="padding: 12px; background: #fecaca; border-radius: 8px; text-align: center; border: 2px solid #f87171;">
                    <div style="font-size: 24px; font-weight: bold; color: #b91c1c;">🔴 ${problems.length}</div>
                    <div style="font-size: 11px; color: #991b1b;">Problemas (50-69%)</div>
                </div>
                <div style="padding: 12px; background: #f3e8ff; border-radius: 8px; text-align: center; border: 2px solid #d8b4fe;">
                    <div style="font-size: 24px; font-weight: bold; color: #6b21a8;">❌ ${critical.length}</div>
                    <div style="font-size: 11px; color: #581c87;">Críticas (<50%)</div>
                </div>
                <div style="padding: 12px; background: #f0f9ff; border-radius: 8px; text-align: center; border: 2px solid #7dd3fc;">
                    <div style="font-size: 24px; font-weight: bold; color: #0369a1;">📊 ${total}</div>
                    <div style="font-size: 11px; color: #075985;">Total</div>
                </div>
            </div>
    `;

    if (critical.length > 0) {
        reportHTML += `
            <div style="margin-top: 15px;">
                <h4 style="color: #6b21a8; margin-bottom: 10px;">❌ CRÍTICAS - Verificar Urgente (${critical.length}):</h4>
                <div style="max-height: 150px; overflow-y: auto; background: #faf5ff; padding: 10px; border-radius: 8px; border: 1px solid #d8b4fe;">
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${critical.map(p => `
                            <li style="padding: 6px; border-bottom: 1px solid #e9d5ff; display: flex; justify-content: space-between; font-size: 13px;">
                                <span><strong>${p.loja}</strong> - ${p.position}</span>
                                <span style="color: #6b21a8; font-weight: bold;">${p.score.toFixed(1)}%</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    if (problems.length > 0) {
        reportHTML += `
            <div style="margin-top: 15px;">
                <h4 style="color: #dc2626; margin-bottom: 10px;">🔴 Problemas Detectados (${problems.length}):</h4>
                <div style="max-height: 150px; overflow-y: auto; background: #fef2f2; padding: 10px; border-radius: 8px; border: 1px solid #fecaca;">
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${problems.map(p => `
                            <li style="padding: 6px; border-bottom: 1px solid #fecaca; display: flex; justify-content: space-between; font-size: 13px;">
                                <span><strong>${p.loja}</strong> - ${p.position}</span>
                                <span style="color: #dc2626; font-weight: bold;">${p.score.toFixed(1)}%</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    const suspiciousCount = attention.length + problems.length + critical.length;

    reportHTML += `
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                ${suspiciousCount > 0 ?
                    '<button onclick="openReviewReferencesModalWrapper()" class="btn btn-primary">🔍 Revisar Referências Suspeitas (' + suspiciousCount + ')</button>' :
                    '<button onclick="closeAnalysisReport()" class="btn btn-primary">✅ Tudo OK!</button>'
                }
                ${issuesCount > 0 ?
                    '<button onclick="filterProblems()" class="btn btn-secondary">🔍 Ver Apenas Problemas</button>' :
                    ''
                }
                <button onclick="closeAnalysisReport()" class="btn btn-secondary">Fechar</button>
            </div>
        </div>
    `;

    // Criar modal temporário
    const reportModal = document.createElement('div');
    reportModal.id = 'analysisReportModal';
    reportModal.className = 'modal active';
    reportModal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            ${reportHTML}
        </div>
    `;

    document.body.appendChild(reportModal);
}

function closeAnalysisReport() {
    const modal = document.getElementById('analysisReportModal');
    if (modal) {
        modal.remove();
    }
}

function filterProblems() {
    closeAnalysisReport();

    // Ativar filtro de qualidade = problemas
    const qualityFilter = document.getElementById('filterQuality');
    if (qualityFilter) {
        qualityFilter.value = 'problems';  // Mostra 50-69%
        applyFilters();
    }

    showToast('Mostrando apenas câmeras com problemas (score < 70%)', 'warning');
}

// Wrapper para abrir modal de revisão e fechar relatório
function openReviewReferencesModalWrapper() {
    closeAnalysisReport();
    openReviewReferencesModal();
}

// Comparar câmera específica
async function compareCamera(baseId) {
    const camera = cameras.find(c => c.base_id === baseId);

    if (!camera) return;

    try {
        const response = await fetch('/api/vision/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loja: camera.loja,
                position: camera.position,
                image_path: camera.path
            })
        });

        const data = await response.json();

        if (data.success) {
            const result = data.result;

            // Abrir modal de comparação
            openComparisonModal(camera, result);

            // Atualizar cache
            await loadAnalysisCache();
        } else {
            if (data.error === 'Referência não encontrada') {
                showToast('Nenhuma referência encontrada para esta câmera', 'warning');
            } else {
                showToast(data.error || 'Erro ao comparar', 'error');
            }
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com servidor', 'error');
    }
}

// Abrir modal de comparação
function openComparisonModal(camera, result) {
    elements.comparisonCameraName.textContent = `${camera.loja} - ${camera.position}`;

    // Score
    const score = result.final_score;
    const scoreClass = score >= 85 ? 'score-high' : score >= 70 ? 'score-medium' : 'score-low';
    elements.comparisonScore.textContent = `${score}%`;
    elements.comparisonScore.className = `score-badge ${scoreClass}`;

    // Imagens
    document.getElementById('currentImage').src = `/${camera.path}`;
    document.getElementById('referenceImage').src = `/data/referencias/${camera.loja}_${camera.position}.jpg`;

    // Detalhes
    const detailsHTML = `
        <h4>Detalhes da Análise:</h4>
        <ul>
            <li><strong>SSIM Score:</strong> ${result.ssim_score}%</li>
            <li><strong>Histogram Score:</strong> ${result.histogram_score}%</li>
            <li><strong>Status:</strong> ${result.status}</li>
            <li><strong>Resumo:</strong> ${result.summary}</li>
        </ul>
    `;
    document.getElementById('comparisonDetails').innerHTML = detailsHTML;

    // Salvar contexto para botão "Usar como Referência"
    elements.btnSetAsReference.onclick = () => setAsReference(camera);

    elements.comparisonModal.classList.add('active');
}

function closeComparisonModal() {
    elements.comparisonModal.classList.remove('active');
}

// Definir imagem atual como referência
async function setAsReference(camera) {
    if (!confirm(`Usar esta imagem como nova referência para ${camera.loja} - ${camera.position}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/vision/reference/${camera.loja}/${camera.position}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_path: camera.path
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Referência atualizada com sucesso!', 'success');
            closeComparisonModal();
            await checkVisionStatus();
        } else {
            showToast(data.error || 'Erro ao salvar referência', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao conectar com servidor', 'error');
    }
}

// Obter score de uma câmera do cache
function getCameraScore(baseId) {
    return analysisCache[baseId]?.final_score || null;
}

// ==================== Seleção Manual de Referências ====================

let selectedReferences = new Set();
let referenceImages = [];

async function openReferenceModal() {
    // Carregar todas as câmeras (apenas as mais recentes)
    referenceImages = cameras.filter(c => c.is_latest);

    // Preencher filtro de lojas
    const stores = [...new Set(referenceImages.map(c => c.loja))].sort();
    elements.refFilterStore.innerHTML = '<option value="all">Todas as Lojas</option>';
    stores.forEach(store => {
        const option = document.createElement('option');
        option.value = store;
        option.textContent = store;
        elements.refFilterStore.appendChild(option);
    });

    // Limpar seleções anteriores
    selectedReferences.clear();
    updateReferenceCount();

    // Renderizar grid
    renderReferenceGrid();

    // Abrir modal
    elements.referenceModal.classList.add('active');
}

function closeReferenceModal() {
    elements.referenceModal.classList.remove('active');
    selectedReferences.clear();
}

function filterReferenceGrid() {
    renderReferenceGrid();
}

function renderReferenceGrid() {
    const storeFilter = elements.refFilterStore.value;
    const positionFilter = elements.refFilterPosition.value;

    let filtered = referenceImages;

    if (storeFilter !== 'all') {
        filtered = filtered.filter(c => c.loja === storeFilter);
    }

    if (positionFilter !== 'all') {
        filtered = filtered.filter(c => c.position === positionFilter);
    }

    // Renderizar grid
    elements.referenceGrid.innerHTML = '';

    if (filtered.length === 0) {
        elements.referenceGrid.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-secondary);">Nenhuma imagem encontrada com os filtros selecionados.</p>';
        return;
    }

    filtered.forEach(camera => {
        const item = document.createElement('div');
        item.className = 'reference-item';
        item.dataset.baseId = camera.base_id;

        const isSelected = selectedReferences.has(camera.base_id);
        if (isSelected) {
            item.classList.add('selected');
        }

        item.innerHTML = `
            <div class="reference-item-container">
                ${isSelected ? '<div class="reference-item-badge">✓ Selecionada</div>' : ''}
                <img src="/${camera.path}" alt="${camera.loja} - ${camera.position}" class="reference-item-image" loading="lazy">
                <div class="reference-item-info">
                    <div class="reference-item-name">${camera.loja} - ${camera.position}</div>
                    <div class="reference-item-meta">
                        <span>${camera.modified_readable}</span>
                        <span>${(camera.size / 1024).toFixed(1)} KB</span>
                    </div>
                </div>
            </div>
        `;

        item.addEventListener('click', () => {
            toggleReferenceSelection(camera.base_id, camera);
        });

        elements.referenceGrid.appendChild(item);
    });
}

function toggleReferenceSelection(baseId, camera) {
    if (selectedReferences.has(baseId)) {
        selectedReferences.delete(baseId);
    } else {
        selectedReferences.add(baseId);
    }

    updateReferenceCount();
    renderReferenceGrid();
}

function updateReferenceCount() {
    elements.refSelectedCount.textContent = selectedReferences.size;
}

async function saveManualReferences() {
    if (selectedReferences.size === 0) {
        showToast('Nenhuma referência selecionada', 'warning');
        return;
    }

    elements.btnSaveReferences.disabled = true;
    elements.btnSaveReferences.innerHTML = '<span class="spinner"></span> Salvando...';

    try {
        let saved = 0;
        let failed = 0;

        for (const baseId of selectedReferences) {
            const camera = referenceImages.find(c => c.base_id === baseId);

            if (!camera) continue;

            const response = await fetch(`/api/vision/reference/${camera.loja}/${camera.position}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_path: camera.path
                })
            });

            const data = await response.json();

            if (data.success) {
                saved++;
            } else {
                failed++;
            }
        }

        if (saved > 0) {
            showToast(`${saved} referência(s) salva(s) com sucesso!`, 'success');
            await checkVisionStatus();
            closeReferenceModal();
        }

        if (failed > 0) {
            showToast(`${failed} referência(s) falharam`, 'error');
        }

    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao salvar referências', 'error');
    } finally {
        elements.btnSaveReferences.disabled = false;
        elements.btnSaveReferences.innerHTML = '<span class="icon">💾</span> Salvar Referências';
    }
}

// View References Modal Functions
let viewReferencesData = [];
let filteredViewReferences = [];

async function openViewReferencesModal() {
    try {
        const response = await fetch('/api/vision/references');
        const data = await response.json();

        if (!data.success) {
            showToast('Erro ao carregar referências', 'error');
            return;
        }

        // Converter estrutura {loja: {position: {path, ...}}} para array
        viewReferencesData = [];
        for (const [loja, positions] of Object.entries(data.references)) {
            for (const [position, info] of Object.entries(positions)) {
                viewReferencesData.push({
                    loja,
                    position,
                    ...info
                });
            }
        }

        // Atualizar contador
        elements.viewRefTotal.textContent = viewReferencesData.length;

        // Popular filtro de lojas
        const stores = [...new Set(viewReferencesData.map(r => r.loja))].sort();
        elements.viewRefFilterStore.innerHTML = '<option value="all">Todas as Lojas</option>';
        stores.forEach(store => {
            const option = document.createElement('option');
            option.value = store;
            option.textContent = store;
            elements.viewRefFilterStore.appendChild(option);
        });

        // Resetar filtros
        elements.viewRefFilterStore.value = 'all';
        elements.viewRefFilterPosition.value = 'all';

        // Renderizar grid
        filterViewReferencesGrid();

        // Abrir modal
        elements.viewReferencesModal.classList.add('active');

    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao carregar referências', 'error');
    }
}

function closeViewReferencesModal() {
    elements.viewReferencesModal.classList.remove('active');
}

function filterViewReferencesGrid() {
    const storeFilter = elements.viewRefFilterStore.value;
    const positionFilter = elements.viewRefFilterPosition.value;

    filteredViewReferences = viewReferencesData.filter(ref => {
        if (storeFilter !== 'all' && ref.loja !== storeFilter) return false;
        if (positionFilter !== 'all' && ref.position !== positionFilter) return false;
        return true;
    });

    renderViewReferencesGrid();
}

function renderViewReferencesGrid() {
    elements.viewReferencesGrid.innerHTML = '';

    if (filteredViewReferences.length === 0) {
        elements.viewReferencesGrid.innerHTML = '<p style="text-align: center; padding: 20px; color: #666;">Nenhuma referência encontrada</p>';
        return;
    }

    filteredViewReferences.forEach(ref => {
        const item = document.createElement('div');
        item.className = 'reference-grid-item';

        // Caminho da referência (formato: data/referencias/Loja_P1.jpg)
        const refPath = `/data/referencias/${ref.loja}_${ref.position}.jpg`;

        item.innerHTML = `
            <img src="${refPath}"
                 alt="${ref.loja} - ${ref.position}"
                 onerror="this.style.display='none'">
            <div class="reference-grid-item-info">
                <div class="reference-grid-item-title">${ref.loja}</div>
                <div class="reference-grid-item-position">${ref.position}</div>
                <div class="reference-grid-item-actions">
                    <button class="btn-mini btn-delete" onclick="deleteReference('${ref.loja}', '${ref.position}')">
                        🗑️ Remover
                    </button>
                </div>
            </div>
        `;

        elements.viewReferencesGrid.appendChild(item);
    });
}

async function deleteReference(loja, position) {
    if (!confirm(`Remover referência de ${loja} - ${position}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/vision/reference/${loja}/${position}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Referência removida: ${loja} - ${position}`, 'success');

            // Recarregar lista
            await openViewReferencesModal();
            await checkVisionStatus();
        } else {
            showToast('Erro ao remover referência', 'error');
        }

    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao remover referência', 'error');
    }
}

async function clearAllReferences() {
    const count = await fetch('/api/vision/status').then(r => r.json()).then(d => d.references_count || 0);

    if (count === 0) {
        showToast('Não há referências para remover', 'info');
        return;
    }

    if (!confirm(`⚠️ ATENÇÃO: Isso irá remover TODAS as ${count} referências salvas!\n\nDeseja continuar?`)) {
        return;
    }

    try {
        const response = await fetch('/api/vision/references/clear', {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`${data.deleted_count} referências removidas com sucesso!`, 'success');
            await checkVisionStatus();

            // Se o modal de visualização estiver aberto, fechar
            if (elements.viewReferencesModal.classList.contains('active')) {
                closeViewReferencesModal();
            }
        } else {
            showToast('Erro ao remover referências', 'error');
        }

    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao remover referências', 'error');
    }
}

// ==================== Melhorias no Modal de Seleção Manual ====================

// Estado do modo de visualização
let viewMode = 'grid'; // 'grid' ou 'by-store'

// Alternar modo de visualização
function switchViewMode(mode) {
    viewMode = mode;

    if (elements.btnViewGrid) elements.btnViewGrid.classList.toggle('active', mode === 'grid');
    if (elements.btnViewByStore) elements.btnViewByStore.classList.toggle('active', mode === 'by-store');

    renderReferenceGrid();
}

// Renderizar grid agrupado por loja (sobrescreve a função original)
const originalRenderReferenceGrid = renderReferenceGrid;

renderReferenceGrid = function() {
    if (viewMode === 'grid') {
        // Modo grid normal (usar função original)
        originalRenderReferenceGrid();

        // Adicionar evento de zoom em cada imagem
        document.querySelectorAll('.reference-item img').forEach(img => {
            img.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                showImageZoom(img.src);
            });
        });
    } else {
        // Modo agrupado por loja
        renderReferenceGridByStore();
    }
};

function renderReferenceGridByStore() {
    const storeFilter = elements.refFilterStore.value;
    const positionFilter = elements.refFilterPosition.value;

    let filtered = referenceImages;

    if (storeFilter !== 'all') {
        filtered = filtered.filter(c => c.loja === storeFilter);
    }

    if (positionFilter !== 'all') {
        filtered = filtered.filter(c => c.position === positionFilter);
    }

    elements.referenceGrid.innerHTML = '';

    if (filtered.length === 0) {
        elements.referenceGrid.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-secondary);">Nenhuma imagem encontrada.</p>';
        return;
    }

    // Agrupar por loja
    const byStore = {};
    filtered.forEach(camera => {
        if (!byStore[camera.loja]) {
            byStore[camera.loja] = [];
        }
        byStore[camera.loja].push(camera);
    });

    // Renderizar cada grupo
    Object.entries(byStore).sort(([a], [b]) => a.localeCompare(b)).forEach(([storeName, cameras]) => {
        const storeGroup = document.createElement('div');
        storeGroup.className = 'reference-store-group';

        const selected = cameras.filter(c => selectedReferences.has(c.base_id)).length;

        storeGroup.innerHTML = `
            <div class="reference-store-header">
                <div class="reference-store-title">
                    🏪 ${storeName}
                    <span class="reference-store-count">(${cameras.length} câmeras)</span>
                </div>
                <div class="reference-store-actions">
                    <span style="font-size: 12px; color: #059669; font-weight: 600;">${selected} selecionadas</span>
                    <button class="store-select-all" data-store="${storeName}">✓ Selecionar Todas</button>
                    <button class="store-select-none" data-store="${storeName}">✗ Limpar</button>
                </div>
            </div>
            <div class="reference-grid large-thumbs" style="background: white;"></div>
        `;

        const gridContainer = storeGroup.querySelector('.reference-grid');

        cameras.forEach(camera => {
            const item = document.createElement('div');
            item.className = 'reference-item';
            item.dataset.baseId = camera.base_id;

            const isSelected = selectedReferences.has(camera.base_id);
            if (isSelected) {
                item.classList.add('selected');
            }

            item.innerHTML = `
                <div class="reference-item-container">
                    ${isSelected ? '<div class="reference-item-badge">✓ Selecionada</div>' : ''}
                    <img src="/${camera.path}" alt="${camera.loja} - ${camera.position}" class="reference-item-image" loading="lazy">
                    <div class="reference-item-info">
                        <div class="reference-item-name">${camera.position}</div>
                        <div class="reference-item-meta">
                            <span>${camera.modified_readable}</span>
                        </div>
                    </div>
                </div>
            `;

            item.addEventListener('click', () => {
                toggleReferenceSelection(camera.base_id, camera);
            });

            // Zoom ao duplo clique
            item.querySelector('img').addEventListener('dblclick', (e) => {
                e.stopPropagation();
                showImageZoom(`/${camera.path}`);
            });

            gridContainer.appendChild(item);
        });

        // Event listeners para seleção em lote
        storeGroup.querySelector('.store-select-all').addEventListener('click', (e) => {
            e.preventDefault();
            cameras.forEach(c => selectedReferences.add(c.base_id));
            updateReferenceCount();
            renderReferenceGrid();
        });

        storeGroup.querySelector('.store-select-none').addEventListener('click', (e) => {
            e.preventDefault();
            cameras.forEach(c => selectedReferences.delete(c.base_id));
            updateReferenceCount();
            renderReferenceGrid();
        });

        elements.referenceGrid.appendChild(storeGroup);
    });
}

// Zoom de imagem
function showImageZoom(imageSrc) {
    if (elements.zoomedImage && elements.imageZoomModal) {
        elements.zoomedImage.src = imageSrc;
        elements.imageZoomModal.classList.add('active');
    }
}

function closeImageZoom() {
    if (elements.imageZoomModal) {
        elements.imageZoomModal.classList.remove('active');
    }
}

// ==================== Revisão de Referências Suspeitas ====================

let suspiciousReferences = [];

async function openReviewReferencesModal() {
    // Buscar análises com score < 70%
    const cache = await fetch('/api/vision/cache').then(r => r.json()).then(d => d.cache || {});

    suspiciousReferences = [];

    for (const [baseId, analysis] of Object.entries(cache)) {
        if (analysis.final_score < 70 && analysis.final_score >= 0) {
            // Encontrar câmera correspondente
            const camera = cameras.find(c => c.base_id === baseId);
            if (camera) {
                suspiciousReferences.push({
                    baseId,
                    camera,
                    analysis
                });
            }
        }
    }

    if (suspiciousReferences.length === 0) {
        showToast('Nenhuma câmera suspeita encontrada! Todas estão OK.', 'success');
        return;
    }

    elements.reviewTotalCount.textContent = suspiciousReferences.length;

    renderReviewGrid();

    elements.reviewReferencesModal.classList.add('active');
}

function closeReviewReferencesModal() {
    elements.reviewReferencesModal.classList.remove('active');
}

function renderReviewGrid() {
    elements.reviewGrid.innerHTML = '';

    suspiciousReferences.forEach(item => {
        const { camera, analysis } = item;

        const refPath = `/data/referencias/${camera.loja}_${camera.position}.jpg`;
        const currentPath = `/${camera.path}`;

        const reviewItem = document.createElement('div');
        reviewItem.className = 'review-item';

        const scoreClass = analysis.final_score >= 50 ? 'warning' : 'ok';

        reviewItem.innerHTML = `
            <div class="review-image-container">
                <span class="review-image-label">Referência (Ideal)</span>
                <img src="${refPath}" alt="Referência" onerror="this.src='/static/images/no-image.png'">
            </div>
            <div class="review-image-container">
                <span class="review-image-label">Atual</span>
                <img src="${currentPath}" alt="Atual">
            </div>
            <div class="review-actions">
                <div class="review-info">
                    <div><strong>${camera.loja}</strong></div>
                    <div style="font-size: 13px; color: #6b7280;">${camera.position}</div>
                    <div class="review-score ${scoreClass}">${analysis.final_score.toFixed(1)}%</div>
                    <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">${analysis.status}</div>
                </div>

                <button class="btn btn-primary" onclick="useCurrentAsReference('${camera.loja}', '${camera.position}', '${camera.path}')">
                    ⭐ Usar Atual como Referência
                </button>

                <button class="btn btn-secondary" onclick="keepCurrentReference('${camera.loja}', '${camera.position}')">
                    ✓ Manter Referência Atual
                </button>

                <button class="btn btn-ghost" style="color: #dc2626;" onclick="removeReference('${camera.loja}', '${camera.position}')">
                    🗑️ Remover Referência
                </button>
            </div>
        `;

        elements.reviewGrid.appendChild(reviewItem);
    });
}

async function useCurrentAsReference(loja, position, imagePath) {
    try {
        const response = await fetch(`/api/vision/reference/${loja}/${position}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({image_path: imagePath})
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Referência atualizada: ${loja} - ${position}`, 'success');
            // Remover da lista de suspeitas
            suspiciousReferences = suspiciousReferences.filter(s => !(s.camera.loja === loja && s.camera.position === position));
            elements.reviewTotalCount.textContent = suspiciousReferences.length;
            renderReviewGrid();

            if (suspiciousReferences.length === 0) {
                showToast('Todas as referências foram revisadas!', 'success');
                closeReviewReferencesModal();
            }
        } else {
            showToast('Erro ao atualizar referência', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao atualizar referência', 'error');
    }
}

function keepCurrentReference(loja, position) {
    // Apenas remove da lista de revisão
    suspiciousReferences = suspiciousReferences.filter(s => !(s.camera.loja === loja && s.camera.position === position));
    elements.reviewTotalCount.textContent = suspiciousReferences.length;
    renderReviewGrid();

    showToast(`Referência mantida: ${loja} - ${position}`, 'info');

    if (suspiciousReferences.length === 0) {
        showToast('Todas as referências foram revisadas!', 'success');
        closeReviewReferencesModal();
    }
}

async function removeReference(loja, position) {
    if (!confirm(`Remover referência de ${loja} - ${position}?`)) {
        return;
    }

    await deleteReference(loja, position);

    // Remover da lista
    suspiciousReferences = suspiciousReferences.filter(s => !(s.camera.loja === loja && s.camera.position === position));
    elements.reviewTotalCount.textContent = suspiciousReferences.length;
    renderReviewGrid();

    if (suspiciousReferences.length === 0) {
        closeReviewReferencesModal();
    }
}

// Toggle AI Panel
function toggleAiPanel() {
    const isVisible = elements.aiPanel.style.display !== 'none';
    elements.aiPanel.style.display = isVisible ? 'none' : 'block';
}

// Event listeners para IA
if (elements.btnAiPanel) {
    elements.btnAiPanel.addEventListener('click', toggleAiPanel);
}

if (elements.btnCloseAiPanel) {
    elements.btnCloseAiPanel.addEventListener('click', () => {
        elements.aiPanel.style.display = 'none';
    });
}

if (elements.btnAutoLearn) {
    elements.btnAutoLearn.addEventListener('click', autoLearnReferences);
}

if (elements.btnAnalyzeAll) {
    elements.btnAnalyzeAll.addEventListener('click', analyzeAllCameras);
}

if (elements.btnManualReference) {
    elements.btnManualReference.addEventListener('click', openReferenceModal);
}

if (elements.btnCloseReferenceModal) {
    elements.btnCloseReferenceModal.addEventListener('click', closeReferenceModal);
}

if (elements.btnCancelReferences) {
    elements.btnCancelReferences.addEventListener('click', closeReferenceModal);
}

if (elements.btnSaveReferences) {
    elements.btnSaveReferences.addEventListener('click', saveManualReferences);
}

if (elements.refFilterStore) {
    elements.refFilterStore.addEventListener('change', filterReferenceGrid);
}

if (elements.refFilterPosition) {
    elements.refFilterPosition.addEventListener('change', filterReferenceGrid);
}

// View References Modal
if (elements.btnViewReferences) {
    elements.btnViewReferences.addEventListener('click', openViewReferencesModal);
}

if (elements.btnCloseViewReferences) {
    elements.btnCloseViewReferences.addEventListener('click', closeViewReferencesModal);
}

if (elements.btnCloseViewReferencesFooter) {
    elements.btnCloseViewReferencesFooter.addEventListener('click', closeViewReferencesModal);
}

if (elements.viewRefFilterStore) {
    elements.viewRefFilterStore.addEventListener('change', filterViewReferencesGrid);
}

if (elements.viewRefFilterPosition) {
    elements.viewRefFilterPosition.addEventListener('change', filterViewReferencesGrid);
}

// Clear All References
if (elements.btnClearReferences) {
    elements.btnClearReferences.addEventListener('click', clearAllReferences);
}

// Novos event listeners para melhorias
if (elements.btnViewGrid) {
    elements.btnViewGrid.addEventListener('click', () => switchViewMode('grid'));
}

if (elements.btnViewByStore) {
    elements.btnViewByStore.addEventListener('click', () => switchViewMode('by-store'));
}

if (elements.imageZoomModal) {
    elements.imageZoomModal.addEventListener('click', closeImageZoom);
}

if (elements.btnCloseReviewModal) {
    elements.btnCloseReviewModal.addEventListener('click', closeReviewReferencesModal);
}

if (elements.btnCloseReview) {
    elements.btnCloseReview.addEventListener('click', closeReviewReferencesModal);
}

if (elements.btnCloseComparison) {
    elements.btnCloseComparison.addEventListener('click', closeComparisonModal);
}

// Inicializar visão no carregamento
async function initVision() {
    await checkVisionStatus();
    await loadAnalysisCache();
}

// Chamar no init
const originalInit = init;
init = async function() {
    await originalInit();
    await initVision();
};

// Tornar funções disponíveis globalmente para onclick
window.markCamera = markCamera;
window.unmarkCamera = unmarkCamera;
window.previewImage = previewImage;
window.compareCamera = compareCamera;
