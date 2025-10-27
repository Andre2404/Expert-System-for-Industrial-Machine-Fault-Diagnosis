// JavaScript untuk Sistem Pakar

const API_BASE = '/api';

let symptoms = [];
let selectedSymptoms = new Set();
let currentResults = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadSymptoms();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('runDiagnosis').addEventListener('click', runDiagnosis);
    document.getElementById('resetSelection').addEventListener('click', resetSelection);
    document.getElementById('newDiagnosis').addEventListener('click', newDiagnosis);
    document.getElementById('searchSymptoms').addEventListener('input', filterSymptoms);
}

async function loadSymptoms() {
    try {
        const response = await fetch(`${API_BASE}/symptoms`);
        const data = await response.json();
        
        if (data.success) {
            symptoms = data.data;
            renderSymptoms(symptoms);
        }
    } catch (error) {
        console.error('Error loading symptoms:', error);
        showError('Gagal memuat gejala. Silakan refresh halaman.');
    }
}

function renderSymptoms(symptomsToRender) {
    const grid = document.getElementById('symptomsGrid');
    grid.innerHTML = '';
    
    symptomsToRender.forEach(symptom => {
        const card = document.createElement('div');
        card.className = 'symptom-card';
        card.dataset.id = symptom.id;
        
        card.innerHTML = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="symptom-${symptom.id}" 
                       value="${symptom.id}">
                <label class="form-check-label" for="symptom-${symptom.id}">
                    <strong>${symptom.id}:</strong> ${symptom.name}
                </label>
            </div>
        `;
        
        card.addEventListener('click', function(e) {
            if (e.target.type !== 'checkbox') {
                const checkbox = card.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                e.target.checked = checkbox.checked;
            }
            toggleSymptom(symptom.id, card.querySelector('input[type="checkbox"]').checked);
        });
        
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', function() {
            toggleSymptom(symptom.id, this.checked);
        });
        
        grid.appendChild(card);
    });
}

function toggleSymptom(id, isSelected) {
    if (isSelected) {
        selectedSymptoms.add(id);
        const card = document.querySelector(`[data-id="${id}"]`);
        if (card) card.classList.add('selected');
    } else {
        selectedSymptoms.delete(id);
        const card = document.querySelector(`[data-id="${id}"]`);
        if (card) card.classList.remove('selected');
    }
    
    updateSelectionCount();
    updateDiagnosisButton();
}

function updateSelectionCount() {
    document.getElementById('selectedCount').textContent = selectedSymptoms.size;
}

function updateDiagnosisButton() {
    const button = document.getElementById('runDiagnosis');
    button.disabled = selectedSymptoms.size === 0;
}

function filterSymptoms() {
    const searchTerm = document.getElementById('searchSymptoms').value.toLowerCase();
    const filtered = symptoms.filter(s => 
        s.name.toLowerCase().includes(searchTerm) || 
        s.id.toLowerCase().includes(searchTerm)
    );
    renderSymptoms(filtered);
}

async function runDiagnosis() {
    if (selectedSymptoms.size === 0) {
        alert('Pilih minimal satu gejala!');
        return;
    }
    
    // Show loading
    document.getElementById('selectionSection').classList.add('d-none');
    document.getElementById('resultsSection').classList.add('d-none');
    document.getElementById('loadingIndicator').classList.remove('d-none');
    
    try {
        const response = await fetch(`${API_BASE}/diagnose`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptoms: Array.from(selectedSymptoms)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data.data;
            renderResults(data.data);
            
            document.getElementById('loadingIndicator').classList.add('d-none');
            document.getElementById('resultsSection').classList.remove('d-none');
        } else {
            throw new Error(data.error || 'Error performing diagnosis');
        }
    } catch (error) {
        console.error('Error running diagnosis:', error);
        showError('Gagal melakukan diagnosis. ' + error.message);
        document.getElementById('loadingIndicator').classList.add('d-none');
        document.getElementById('selectionSection').classList.remove('d-none');
    }
}

function renderResults(data) {
    const resultsBody = document.getElementById('resultsBody');
    
    if (data.total_diagnoses === 0) {
        resultsBody.innerHTML = `
            <div class="no-results">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Tidak ada diagnosis yang cocok</h4>
                <p>Gejala yang dipilih tidak sesuai dengan rules dalam knowledge base.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>Ditemukan ' + 
                data.total_diagnoses + ' kemungkinan diagnosis</div>';
    
    const colors = ['primary', 'secondary', 'success', 'warning', 'info'];
    
    data.diagnoses.forEach((diagnosis, index) => {
        const colorClass = colors[index % colors.length];
        html += `
            <div class="diagnosis-card">
                <div class="diagnosis-header ${colorClass}">
                    <div class="confidence-badge">${diagnosis.confidence}%</div>
                    <h4 class="mb-2">${diagnosis.name}</h4>
                    <p class="mb-0 opacity-75">${diagnosis.description}</p>
                </div>
                
                <div class="card-body">
                    <!-- Confidence Bar -->
                    <div class="mb-4">
                        <div class="d-flex justify-content-between mb-2">
                            <span><strong>Tingkat Keyakinan:</strong></span>
                            <span class="badge bg-${colorClass}">${diagnosis.confidence}%</span>
                        </div>
                        <div class="progress confidence-progress">
                            <div class="progress-bar bg-${colorClass} progress-bar-striped progress-bar-animated" 
                                 role="progressbar" 
                                 style="width: ${diagnosis.confidence}%"
                                 aria-valuenow="${diagnosis.confidence}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${diagnosis.confidence}%
                            </div>
                        </div>
                    </div>
                    
                    <!-- Severity & Risk -->
                        <div class="col-md-6">
                            <strong>Risk Level:</strong> 
                            <span class="risk-${diagnosis.risk_level.toLowerCase()}">${diagnosis.risk_level}</span>
                        </div>
                    </div>
                    
                    <!-- Maintenance Time -->
                    <div class="alert alert-light">
                        <i class="fas fa-clock me-2"></i>
                        <strong>Estimasi Waktu Maintenance:</strong> ${diagnosis.maintenance_time}
                    </div>
                    
                    <!-- Causes -->
                    <div class="expandable-section">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>Kemungkinan Penyebab:</h5>
                        <ul class="list-unstyled">
                            ${diagnosis.causes.map(cause => `<li><i class="fas fa-circle-notch fa-xs me-2"></i>${cause}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <!-- Solutions -->
                    <div class="expandable-section mt-3">
                        <h5><i class="fas fa-tools me-2"></i>Solusi & Rekomendasi:</h5>
                        ${diagnosis.solutions.map((solution, idx) => `
                            <div class="solution-item">
                                <strong>Step ${idx + 1}:</strong> ${solution}
                            </div>
                        `).join('')}
                    </div>
                    
                    <!-- Tools Required -->
                    <div class="mt-3">
                     <container>
                        <h5><i class="fas fa-wrench me-2"></i>Alat yang Diperlukan:</h5>
                        <p>
                            ${diagnosis.tools_required.map(tool => `
                                <span class="tool-tag"><i class="fas fa-toolbox me-1"></i>${tool}</span>
                            `).join('')}
                        </p>
                    </container>
                        </div>
                </div>
            </div>
        `;
    });
    
    // Add explanation button
    html += `
    <div class="text-center mt-4">
        <button class="btn btn-outline-warning btn-lg" onclick="showExplanation(${JSON.stringify(data.reasoning).replace(/"/g, '&quot;')})">
            <i class="fas fa-question-circle me-2"></i>
            Lihat Proses Reasoning
        </button>
    </div>
`;
    
    resultsBody.innerHTML = html;
}

function showExplanation(reasoning) {
    let html = '<div class="table-responsive"><table class="table table-bordered">';
    html += '<thead><tr><th>Rule ID</th><th>Keterangan</th><th>Konklusi</th><th>CF</th></tr></thead><tbody>';
    
    reasoning.forEach(r => {
        html += `<tr>
            <td><strong>${r.rule_id}</strong></td>
            <td>${r.rule_description}</td>
            <td>${r.conclusion}</td>
            <td>${(r.cf * 100).toFixed(2)}%</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    document.getElementById('explanationContent').innerHTML = html;
    new bootstrap.Modal(document.getElementById('explanationModal')).show();
}

function resetSelection() {
    selectedSymptoms.clear();
    document.querySelectorAll('.symptom-card').forEach(card => {
        card.classList.remove('selected');
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (checkbox) checkbox.checked = false;
    });
    updateSelectionCount();
    updateDiagnosisButton();
    document.getElementById('searchSymptoms').value = '';
    renderSymptoms(symptoms);
}

function newDiagnosis() {
    currentResults = null;
    document.getElementById('resultsSection').classList.add('d-none');
    document.getElementById('selectionSection').classList.remove('d-none');
    resetSelection();
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alert, document.querySelector('.container').firstChild);
    setTimeout(() => alert.remove(), 5000);
}

// Make showExplanation available globally
window.showExplanation = showExplanation;

