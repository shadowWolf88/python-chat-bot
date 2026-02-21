/**
 * TIER 1.1: Clinician Dashboard Module
 * Handles all dashboard data loading, rendering, and tab navigation
 * 
 * Features:
 * - Overview/summary loading
 * - Patient list with search/filter
 * - Patient detail view with 7 subtabs
 * - Mood/sleep/activity charts
 * - Risk alert monitoring
 * - Appointment calendar
 * - Messaging system
 * - Settings management
 */

// Global state
let currentClinicianPatient = null;
let clinicianCharts = {};
let clinicianMessageFilter = 'inbox';

/**
 * ============================================================================
 * CORE API HELPER - ALL REQUESTS GO THROUGH HERE
 * ============================================================================
 */

async function callClinicianAPI(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': await getCSRFToken()
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `API error: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`Clinician API Error [${endpoint}]:`, error);
        showError(`Failed to load data: ${error.message}`);
        throw error;
    }
}

async function getCSRFToken() {
    // Token should be available from main app, or fetch fresh
    try {
        const response = await fetch('/api/csrf-token');
        const data = await response.json();
        return data.token || '';
    } catch (e) {
        console.warn('Could not fetch CSRF token');
        return '';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('analyticsError');
    if (errorDiv) {
        errorDiv.textContent = `❌ ${message}`;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(`Error: ${message}`);
    }
}

function showSuccess(message) {
    console.log(`✅ ${message}`);
}

/**
 * ============================================================================
 * TAB NAVIGATION
 * ============================================================================
 */

function switchClinicalTab(tabName) {
    // Hide all clinical subtabs
    const tabs = document.querySelectorAll('.clinical-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`clinical${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.clinical-subtab-btn');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase().includes(tabName) || 
            btn.onclick.toString().includes(`'${tabName}'`)) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
            btn.style.borderColor = '#667eea';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
            btn.style.borderColor = '#667eea';
        }
    });
    
    // Load data for specific tabs
    if (tabName === 'overview') {
        loadAnalyticsDashboard();
    } else if (tabName === 'patients') {
        loadPatients();
    } else if (tabName === 'messages') {
        loadClinicalMessages();
    } else if (tabName === 'riskmonitor') {
        loadRiskDashboard();
    }
}

function switchPatientTab(tabName) {
    // Hide all patient subtabs
    const tabs = document.querySelectorAll('.patient-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`patient${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.patient-subtab-btn');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase().includes(tabName)) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
        }
    });
    
    // Load data for specific tabs
    if (!currentClinicianPatient) return;
    
    if (tabName === 'summary') {
        loadPatientSummary(currentClinicianPatient.username);
    } else if (tabName === 'charts') {
        loadPatientCharts(currentClinicianPatient.username);
    } else if (tabName === 'profile') {
        loadPatientProfile(currentClinicianPatient.username);
    } else if (tabName === 'moods') {
        loadPatientMoods(currentClinicianPatient.username);
    } else if (tabName === 'assessments') {
        loadPatientAssessments(currentClinicianPatient.username);
    } else if (tabName === 'therapy') {
        loadPatientSessions(currentClinicianPatient.username);
    } else if (tabName === 'alerts') {
        loadPatientAlerts(currentClinicianPatient.username);
    }
}

function switchMessageTab(tabName, button) {
    clinicianMessageFilter = tabName;
    
    // Hide all message subtabs
    const tabs = document.querySelectorAll('.message-subtab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    const activeTab = document.getElementById(`clinMessages${capitalizeFirst(tabName)}Tab`);
    if (activeTab) {
        activeTab.style.display = 'block';
    }
    
    // Update button styles
    const buttons = document.querySelectorAll('.message-subtab-btn');
    buttons.forEach(btn => {
        if (btn === button) {
            btn.style.background = '#667eea';
            btn.style.color = 'white';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
        }
    });
    
    // Load messages for specific filter
    if (tabName === 'inbox' || tabName === 'sent') {
        loadClinicalMessages(tabName);
    }
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * ============================================================================
 * OVERVIEW / SUMMARY LOADING
 * ============================================================================
 */

async function loadAnalyticsDashboard() {
    try {
        const data = await callClinicianAPI('/api/clinician/summary');
        
        document.getElementById('totalPatientsCount').textContent = data.total_patients || 0;
        document.getElementById('activePatientsCount').textContent = data.sessions_this_week || 0;
        document.getElementById('highRiskCount').textContent = data.critical_patients || 0;
        
        showSuccess('Dashboard loaded');
    } catch (error) {
        console.error('Error loading analytics dashboard:', error);
    }
}

/**
 * ============================================================================
 * PATIENT LIST / MANAGEMENT
 * ============================================================================
 */

async function loadPatients(filter = 'all', search = '') {
    try {
        const data = await callClinicianAPI('/api/clinician/patients');
        
        let patients = data.patients || [];
        
        // Apply filters
        if (filter === 'high_risk') {
            patients = patients.filter(p => p.risk_level === 'high' || p.risk_level === 'critical');
        } else if (filter === 'inactive') {
            patients = patients.filter(p => !p.last_session || 
                (new Date() - new Date(p.last_session)) > 7 * 24 * 60 * 60 * 1000);
        }
        
        // Apply search
        if (search) {
            patients = patients.filter(p =>
                (p.name || p.username).toLowerCase().includes(search.toLowerCase()) ||
                p.username.toLowerCase().includes(search.toLowerCase())
            );
        }
        
        renderPatientList(patients);
        showSuccess(`Loaded ${patients.length} patients`);
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

function renderPatientList(patients) {
    const container = document.getElementById('patientList');
    
    if (!patients || patients.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">No patients found</p>';
        return;
    }
    
    let html = `
        <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: #f5f5f5;">
                <tr>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Name</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Email</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Last Session</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e0e0e0;">Risk Level</th>
                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #e0e0e0;">Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    patients.forEach(patient => {
        const riskColor = {
            'critical': '#ff4444',
            'high': '#ff8800',
            'moderate': '#ffcc00',
            'low': '#44ff44'
        }[patient.risk_level] || '#999';
        
        const lastSession = patient.last_session ? new Date(patient.last_session).toLocaleDateString() : 'Never';
        
        html += `
            <tr style="border-bottom: 1px solid #e0e0e0; hover-background: #f9f9f9;">
                <td style="padding: 12px;">${sanitizeHTML(patient.name || patient.username)}</td>
                <td style="padding: 12px;">${sanitizeHTML(patient.email)}</td>
                <td style="padding: 12px;">${lastSession}</td>
                <td style="padding: 12px;">
                    <span style="background: ${riskColor}; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                        ${patient.risk_level || 'unknown'}
                    </span>
                </td>
                <td style="padding: 12px; text-align: center;">
                    <button class="btn" onclick="selectPatient('${patient.username}')" style="padding: 6px 12px; font-size: 12px;">View</button>
                </td>
            </tr>
        `;
    });
    
    html += `</tbody></table>`;
    container.innerHTML = html;
}

async function selectPatient(username) {
    // Hide the patient list tab and delegate to the full patient detail view
    // which handles tab switching, data loading, and AI summary correctly.
    document.getElementById('clinicalPatientsTab').style.display = 'none';
    if (typeof viewPatientDetail === 'function') {
        viewPatientDetail(username);
    }
}

function closePatientDetail() {
    currentClinicianPatient = null;
    document.getElementById('patientDetailSection').style.display = 'none';
    document.getElementById('clinicalPatientsTab').style.display = 'block';
    loadPatients();
}

/**
 * ============================================================================
 * PATIENT DETAIL TABS
 * ============================================================================
 */

async function loadPatientSummary(username) {
    try {
        // Use AI summary endpoint when available, otherwise show static profile
        const data = await callClinicianAPI(`/api/clinician/patient/${username}`);
        
        let html = `
            <div class="card" style="border-left: 4px solid #667eea; margin-bottom: 20px;">
                <h4 style="margin-top: 0;">📋 Patient Information</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Name</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.name || data.username || '')}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Email</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.email)}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Phone</strong>
                        <p style="margin: 0;">${sanitizeHTML(data.phone || 'Not provided')}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Current Risk Level</strong>
                        <p style="margin: 0; color: ${getRiskColor(data.risk_level)}; font-weight: 600;">
                            ${data.risk_level || 'Unknown'}
                        </p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Sessions Completed</strong>
                        <p style="margin: 0;">${data.sessions_count || 0}</p>
                    </div>
                    <div>
                        <strong style="display: block; color: #667eea; margin-bottom: 5px;">Last Assessment</strong>
                        <p style="margin: 0;">${new Date(data.risk_date || Date.now()).toLocaleDateString()}</p>
                    </div>
                </div>
            </div>
            
            ${data.treatment_goals && data.treatment_goals.length > 0 ? `
            <div class="card" style="border-left: 4px solid #2ecc71;">
                <h4>🎯 Treatment Goals</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    ${data.treatment_goals.map(g => `
                        <li style="margin: 10px 0; color: #333;">
                            ${sanitizeHTML(g.goal_text)} 
                            <span style="font-size: 0.9em; color: #999;">(${g.status})</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
        `;
        
        document.getElementById('aiSummary').innerHTML = html;
        showSuccess('Patient summary loaded');
    } catch (error) {
        console.error('Error loading patient summary:', error);
    }
}

async function loadPatientProfile(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}`);
        
        let html = `
            <div class="card">
                <h4>👤 Full Profile</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <strong>Full Name:</strong> ${sanitizeHTML(data.name || data.username || '')}
                    </div>
                    <div>
                        <strong>Username:</strong> ${sanitizeHTML(data.username)}
                    </div>
                    <div>
                        <strong>Email:</strong> ${sanitizeHTML(data.email)}
                    </div>
                    <div>
                        <strong>Phone:</strong> ${sanitizeHTML(data.phone || 'Not provided')}
                    </div>
                    <div>
                        <strong>Date of Birth:</strong> ${data.dob ? new Date(data.dob).toLocaleDateString() : 'Not provided'}
                    </div>
                    <div>
                        <strong>Gender:</strong> ${sanitizeHTML(data.gender || 'Not specified')}
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('patientDetailContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading patient profile:', error);
    }
}

async function loadPatientMoods(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/mood-logs`);
        
        let html = `<div class="card">
            <h4>😊 Mood Logs</h4>
            <div style="margin-bottom: 15px; padding: 12px; background: #f0f0f0; border-radius: 8px;">
                <strong>Weekly Average: </strong> ${(data.week_avg || 0).toFixed(1)}/10
            </div>
        `;
        
        if (data.logs && data.logs.length > 0) {
            html += `<table style="width: 100%; border-collapse: collapse;">
                <thead style="background: #f5f5f5;">
                    <tr>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Date</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Mood</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Energy</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #e0e0e0;">Notes</th>
                    </tr>
                </thead>
                <tbody>`;
            
            data.logs.forEach(log => {
                html += `
                    <tr style="border-bottom: 1px solid #e0e0e0;">
                        <td style="padding: 10px;">${new Date(log.date).toLocaleDateString()}</td>
                        <td style="padding: 10px; font-weight: 600;">
                            <span style="background: ${getMoodColor(log.mood)}; color: white; padding: 2px 8px; border-radius: 4px;">
                                ${log.mood}/10
                            </span>
                        </td>
                        <td style="padding: 10px;">${log.energy || '-'}</td>
                        <td style="padding: 10px; font-size: 0.9em; color: #666;">${sanitizeHTML(log.notes || '-')}</td>
                    </tr>
                `;
            });
            
            html += `</tbody></table>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No mood logs found</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientMoodsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading mood logs:', error);
    }
}

async function loadPatientAssessments(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/assessments`);
        
        let html = `<div class="card">
            <h4>📋 Clinical Assessments</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">`;
        
        // PHQ-9
        if (data.phq9) {
            const phq9Color = getAssessmentColor(data.phq9.score, 'phq9');
            html += `
                <div style="background: #f9f9f9; border-left: 4px solid ${phq9Color}; padding: 15px; border-radius: 8px;">
                    <h5 style="margin-top: 0; color: ${phq9Color};">PHQ-9 (Depression)</h5>
                    <p style="margin: 10px 0;"><strong>Score:</strong> <span style="font-size: 1.5em; color: ${phq9Color}; font-weight: 600;">${data.phq9.score}</span>/27</p>
                    <p style="margin: 10px 0;"><strong>Severity:</strong> ${data.phq9.interpretation || 'Unknown'}</p>
                    <p style="margin: 10px 0; font-size: 0.9em; color: #666;">Last assessed: ${new Date(data.phq9.date).toLocaleDateString()}</p>
                </div>
            `;
        }
        
        // GAD-7
        if (data.gad7) {
            const gad7Color = getAssessmentColor(data.gad7.score, 'gad7');
            html += `
                <div style="background: #f9f9f9; border-left: 4px solid ${gad7Color}; padding: 15px; border-radius: 8px;">
                    <h5 style="margin-top: 0; color: ${gad7Color};">GAD-7 (Anxiety)</h5>
                    <p style="margin: 10px 0;"><strong>Score:</strong> <span style="font-size: 1.5em; color: ${gad7Color}; font-weight: 600;">${data.gad7.score}</span>/21</p>
                    <p style="margin: 10px 0;"><strong>Severity:</strong> ${data.gad7.interpretation || 'Unknown'}</p>
                    <p style="margin: 10px 0; font-size: 0.9em; color: #666;">Last assessed: ${new Date(data.gad7.date).toLocaleDateString()}</p>
                </div>
            `;
        }
        
        html += `</div></div>`;
        document.getElementById('patientAssessmentsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading assessments:', error);
    }
}

async function loadPatientSessions(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/sessions`);
        
        let html = `<div class="card">
            <h4>💬 Therapy Sessions</h4>
            <p style="color: #666; margin-bottom: 15px;"><strong>Total Sessions:</strong> ${data.total || 0}</p>`;
        
        if (data.sessions && data.sessions.length > 0) {
            html += `<div style="display: flex; flex-direction: column; gap: 15px;">`;
            
            data.sessions.forEach(session => {
                html += `
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                            <div>
                                <strong style="display: block; color: #333;">${new Date(session.date).toLocaleDateString()}</strong>
                                <span style="font-size: 0.9em; color: #666;">Duration: ${session.duration} minutes</span>
                            </div>
                            <div style="text-align: right;">
                                ${session.mood_before ? `<div style="font-size: 0.9em;">Before: <strong style="color: ${getMoodColor(session.mood_before)};">${session.mood_before}/10</strong></div>` : ''}
                                ${session.mood_after ? `<div style="font-size: 0.9em;">After: <strong style="color: ${getMoodColor(session.mood_after)};">${session.mood_after}/10</strong></div>` : ''}
                            </div>
                        </div>
                        ${session.notes ? `<p style="margin: 10px 0; color: #555; font-size: 0.95em; line-height: 1.4;">${sanitizeHTML(session.notes)}</p>` : ''}
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No therapy sessions recorded</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientTherapyContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function loadPatientAlerts(username) {
    try {
        const data = await callClinicianAPI(`/api/clinician/risk-alerts`);
        
        // Filter alerts for this specific patient
        const patientAlerts = data.alerts ? data.alerts.filter(a => a.patient_username === username) : [];
        
        let html = `<div class="card">
            <h4>🚨 Risk Alerts</h4>`;
        
        if (patientAlerts.length > 0) {
            html += `<div style="display: flex; flex-direction: column; gap: 12px;">`;
            
            patientAlerts.forEach(alert => {
                const riskColor = getRiskColor(alert.risk_level);
                html += `
                    <div style="background: ${riskColor}15; border-left: 4px solid ${riskColor}; padding: 12px; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="color: ${riskColor};">${alert.risk_level.toUpperCase()}</strong>
                                <p style="margin: 5px 0; color: #333;">${sanitizeHTML(alert.trigger || 'Risk detected')}</p>
                                <span style="font-size: 0.85em; color: #666;">${new Date(alert.date).toLocaleDateString()}</span>
                            </div>
                            <button class="btn" onclick="acknowledgeAlert(${alert.alert_id})" style="padding: 6px 12px; font-size: 0.9em;">
                                ${alert.acknowledged ? '✅ Acknowledged' : '⏳ Acknowledge'}
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += `</div>`;
        } else {
            html += `<p style="color: #999; text-align: center; padding: 20px;">No risk alerts for this patient</p>`;
        }
        
        html += `</div>`;
        document.getElementById('patientAlertsContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadPatientCharts(username) {
    try {
        // Set default date range (last 30 days)
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        document.getElementById('patientChartFromDate').valueAsDate = thirtyDaysAgo;
        document.getElementById('patientChartToDate').valueAsDate = today;
        
        const data = await callClinicianAPI(`/api/clinician/patient/${username}/analytics`);
        
        // Render mood chart
        if (data.mood_data && data.mood_data.length > 0) {
            renderMoodChart(data.mood_data);
        }
        
        // Render activity/sleep chart
        if (data.activity_data && data.activity_data.length > 0) {
            renderActivityChart(data.activity_data);
        }
        
        showSuccess('Charts loaded');
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

function renderMoodChart(moodData) {
    const ctx = document.getElementById('moodChart');
    if (!ctx) return;
    
    if (clinicianCharts.mood) {
        clinicianCharts.mood.destroy();
    }
    
    clinicianCharts.mood = new Chart(ctx, {
        type: 'line',
        data: {
            labels: moodData.map(d => new Date(d.date).toLocaleDateString()),
            datasets: [{
                label: 'Mood Score',
                data: moodData.map(d => d.mood),
                borderColor: '#667eea',
                backgroundColor: '#667eea15',
                tension: 0.3,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: { min: 0, max: 10 }
            }
        }
    });
}

function renderActivityChart(activityData) {
    const ctx = document.getElementById('sleepChart');
    if (!ctx) return;
    
    if (clinicianCharts.activity) {
        clinicianCharts.activity.destroy();
    }
    
    clinicianCharts.activity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: activityData.map(d => d.week || d.date),
            datasets: [{
                label: 'Hours',
                data: activityData.map(d => d.hours || d.value),
                backgroundColor: '#2ecc71'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true }
            }
        }
    });
}

/**
 * ============================================================================
 * RISK MONITORING
 * ============================================================================
 */

async function loadRiskDashboard() {
    try {
        const data = await callClinicianAPI('/api/clinician/risk-alerts');
        
        // Count by risk level
        const counts = { critical: 0, high: 0, moderate: 0, low: 0, unreviewed: 0 };
        
        (data.alerts || []).forEach(alert => {
            counts[alert.risk_level] = (counts[alert.risk_level] || 0) + 1;
            if (!alert.acknowledged) counts.unreviewed++;
        });
        
        document.getElementById('riskCriticalCount').textContent = counts.critical;
        document.getElementById('riskHighCount').textContent = counts.high;
        document.getElementById('riskModerateCount').textContent = counts.moderate;
        document.getElementById('riskLowCount').textContent = counts.low;
        document.getElementById('riskUnreviewedCount').textContent = counts.unreviewed;
        
        renderRiskAlerts(data.alerts || []);
        
        showSuccess('Risk dashboard loaded');
    } catch (error) {
        console.error('Error loading risk dashboard:', error);
    }
}

function renderRiskAlerts(alerts) {
    const container = document.getElementById('riskActiveAlertsList');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No active alerts</p>';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 10px;">';
    
    alerts.slice(0, 10).forEach(alert => {
        const riskColor = getRiskColor(alert.risk_level);
        html += `
            <div style="background: ${riskColor}15; border-left: 4px solid ${riskColor}; padding: 12px; border-radius: 8px; cursor: pointer;" 
                 onclick="showRiskDetail('${alert.patient_username}')">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: ${riskColor};">${alert.patient_name}</strong>
                        <p style="margin: 5px 0; color: #333; font-size: 0.9em;">${sanitizeHTML(alert.trigger || 'Risk alert')}</p>
                        <span style="font-size: 0.8em; color: #666;">${new Date(alert.date).toLocaleString()}</span>
                    </div>
                    <span style="background: ${riskColor}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: 600;">
                        ${alert.risk_level}
                    </span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function filterRiskPatients(level) {
    console.log('Filter risk patients:', level);
    loadRiskDashboard();
}

function showRiskDetail(patientUsername) {
    selectPatient(patientUsername);
    switchPatientTab('alerts');
}

/**
 * ============================================================================
 * MESSAGING
 * ============================================================================
 */

async function loadClinicalMessages(filter = 'inbox') {
    try {
        // For now, show placeholder
        const container = filter === 'inbox' ? 
            document.getElementById('clinMessagesInboxContainer') :
            document.getElementById('clinMessagesSentContainer');
        
        if (container) {
            container.innerHTML = `
                <p style="text-align: center; color: #999; padding: 40px;">
                    ${filter === 'inbox' ? 'No messages in inbox' : 'No sent messages'}
                </p>
            `;
        }
        
        showSuccess(`Messages loaded (${filter})`);
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

async function sendNewMessage() {
    const recipient = document.getElementById('clinMessageRecipient').value;
    const subject = document.getElementById('clinMessageSubject').value;
    const message = document.getElementById('clinMessageContent').value;
    
    if (!recipient || !message) {
        showError('Please fill in required fields');
        return;
    }
    
    try {
        await callClinicianAPI('/api/clinician/message', 'POST', {
            recipient_username: recipient,
            message: message
        });
        
        document.getElementById('clinMessageContent').value = '';
        document.getElementById('clinMessageRecipient').value = '';
        document.getElementById('clinMessageSubject').value = '';
        
        showSuccess('Message sent successfully');
        loadClinicalMessages('inbox');
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

/**
 * ============================================================================
 * UTILITY FUNCTIONS
 * ============================================================================
 */

function sanitizeHTML(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getRiskColor(level) {
    return {
        'critical': '#ff4444',
        'high': '#ff8800',
        'moderate': '#ffcc00',
        'low': '#44ff44'
    }[level] || '#999';
}

function getMoodColor(mood) {
    if (mood >= 8) return '#2ecc71';
    if (mood >= 6) return '#f39c12';
    if (mood >= 4) return '#e67e22';
    return '#e74c3c';
}

function getAssessmentColor(score, type) {
    if (type === 'phq9') {
        if (score < 5) return '#2ecc71';
        if (score < 10) return '#f39c12';
        if (score < 15) return '#e67e22';
        return '#e74c3c';
    } else if (type === 'gad7') {
        if (score < 5) return '#2ecc71';
        if (score < 10) return '#f39c12';
        if (score < 15) return '#e67e22';
        return '#e74c3c';
    }
    return '#667eea';
}

function setPatientChartRange(days) {
    const today = new Date();
    const startDate = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
    
    document.getElementById('patientChartFromDate').valueAsDate = startDate;
    document.getElementById('patientChartToDate').valueAsDate = today;
    
    if (currentClinicianPatient) {
        loadPatientCharts(currentClinicianPatient.username);
    }
}

function acknowledgeAlert(alertId) {
    console.log('Acknowledge alert:', alertId);
    showSuccess('Alert acknowledged');
}

/**
 * ============================================================================
 * APPOINTMENTS (Placeholder functions)
 * ============================================================================
 */

function showNewAppointmentForm() {
    document.getElementById('newAppointmentForm').style.display = 'block';
    loadPatients(); // Load patient list for appointment dropdown
}

function cancelNewAppointment() {
    document.getElementById('newAppointmentForm').style.display = 'none';
}

async function createAppointment() {
    const patientUsername = document.getElementById('appointmentPatient').value;
    const dateTime = document.getElementById('appointmentDateTime').value;
    const duration = document.getElementById('appointmentDuration').value;
    const notes = document.getElementById('appointmentNotes').value;
    
    if (!patientUsername || !dateTime || !duration) {
        showError('Please fill in all required fields');
        return;
    }
    
    try {
        await callClinicianAPI(`/api/clinician/patient/${patientUsername}/appointments`, 'POST', {
            date: dateTime.split('T')[0],
            time: dateTime.split('T')[1],
            duration: parseInt(duration),
            notes: notes
        });
        
        showSuccess('Appointment created successfully');
        cancelNewAppointment();
        switchClinicalTab('appointments');
    } catch (error) {
        console.error('Error creating appointment:', error);
    }
}

/**
 * ============================================================================
 * SEARCH & FILTER
 * ============================================================================
 */

function searchPatients() {
    const search = document.getElementById('patientSearchInput').value;
    const filter = document.getElementById('patientFilterSelect').value;
    loadPatients(filter, search);
}

function previousMonth() {
    console.log('Previous month');
}

function nextMonth() {
    console.log('Next month');
}

function goToToday() {
    console.log('Go to today');
}

function setCalendarView(view) {
    console.log('Set calendar view:', view);
}

// Export for use
window.clinician = {
    switchClinicalTab,
    switchPatientTab,
    switchMessageTab,
    loadAnalyticsDashboard,
    loadPatients,
    selectPatient,
    closePatientDetail,
    loadPatientSummary,
    loadPatientProfile,
    loadPatientMoods,
    loadPatientAssessments,
    loadPatientSessions,
    loadPatientAlerts,
    loadPatientCharts,
    loadRiskDashboard,
    filterRiskPatients,
    showRiskDetail,
    loadClinicalMessages,
    sendNewMessage,
    searchPatients,
    createAppointment,
    showNewAppointmentForm,
    cancelNewAppointment,
    showLoadingOverlay,
    hideLoadingOverlay,
    showToast,
    createCalendar,
    updateChartStyles,
    enhanceMobileExperience
};

/**
 * ============================================================================
 * PHASE 5: UX ENHANCEMENTS - LOADING SPINNERS, TOASTS, CALENDAR, CHARTS
 * ============================================================================
 */

/**
 * Loading Overlay Management
 */
function showLoadingOverlay(message = 'Loading...') {
    let overlay = document.getElementById('clinicianLoadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'clinicianLoadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-overlay-content">
                <div class="loading-spinner lg"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('clinicianLoadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

/**
 * Toast Notification System
 */
function showToast(type = 'info', title = '', message = '', duration = 4000) {
    // Ensure toast container exists
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Icons for toast types
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-content">
            ${title ? `<div class="toast-title">${sanitizeHTML(title)}</div>` : ''}
            <div class="toast-message">${sanitizeHTML(message)}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.classList.add('exiting'); setTimeout(() => this.parentElement.remove(), 300);">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto-dismiss after duration
    if (duration > 0) {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('exiting');
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }
    
    return toast;
}

/**
 * Calendar Component
 */
function createCalendar(containerId, onDateSelect = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    function renderCalendar(y, m) {
        container.innerHTML = '';
        
        // Header
        const header = document.createElement('div');
        header.className = 'calendar-header';
        header.innerHTML = `
            <h3>Appointments</h3>
            <div class="calendar-nav">
                <button onclick="window.nextCalendarMonth(-1)" title="Previous">◀</button>
                <span class="calendar-month-year">${new Date(y, m).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
                <button onclick="window.nextCalendarMonth(1)" title="Next">▶</button>
            </div>
        `;
        container.appendChild(header);
        
        // Weekday headers
        const weekdaysDiv = document.createElement('div');
        weekdaysDiv.className = 'calendar-weekdays';
        const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        weekdays.forEach(day => {
            const weekday = document.createElement('div');
            weekday.className = 'calendar-weekday';
            weekday.textContent = day;
            weekdaysDiv.appendChild(weekday);
        });
        container.appendChild(weekdaysDiv);
        
        // Days grid
        const daysDiv = document.createElement('div');
        daysDiv.className = 'calendar-days';
        
        const firstDay = new Date(y, m, 1).getDay();
        const daysInMonth = new Date(y, m + 1, 0).getDate();
        const daysInPrevMonth = new Date(y, m, 0).getDate();
        
        // Previous month days
        for (let i = firstDay - 1; i >= 0; i--) {
            const day = document.createElement('div');
            day.className = 'calendar-day other-month';
            day.textContent = daysInPrevMonth - i;
            daysDiv.appendChild(day);
        }
        
        // Current month days
        for (let i = 1; i <= daysInMonth; i++) {
            const day = document.createElement('div');
            day.className = 'calendar-day';
            day.textContent = i;
            
            const date = new Date(y, m, i);
            const today = new Date();
            
            // Mark today
            if (date.toDateString() === today.toDateString()) {
                day.classList.add('today');
            }
            
            // Mark days with events (mock data - would be real appointments)
            if (i % 5 === 0) {
                day.classList.add('has-event');
            }
            
            // Click handler
            day.addEventListener('click', () => {
                document.querySelectorAll('#' + containerId + ' .calendar-day.selected').forEach(d => d.classList.remove('selected'));
                day.classList.add('selected');
                if (onDateSelect) onDateSelect(new Date(y, m, i));
                showToast('info', 'Date Selected', `${new Date(y, m, i).toLocaleDateString()}`);
            });
            
            daysDiv.appendChild(day);
        }
        
        // Next month days
        const totalCells = daysDiv.children.length;
        const remainingCells = 42 - totalCells; // 6 rows × 7 days
        for (let i = 1; i <= remainingCells; i++) {
            const day = document.createElement('div');
            day.className = 'calendar-day other-month';
            day.textContent = i;
            daysDiv.appendChild(day);
        }
        
        container.appendChild(daysDiv);
    }
    
    // Store month navigation functions globally
    window.nextCalendarMonth = function(offset) {
        const newMonth = month + offset;
        if (newMonth < 0) {
            year--;
            month = 11;
        } else if (newMonth > 11) {
            year++;
            month = 0;
        } else {
            month = newMonth;
        }
        renderCalendar(year, month);
    };
    
    renderCalendar(year, month);
}

/**
 * Enhance Chart Visualizations with Smooth Updates
 */
function updateChartStyles() {
    // Add smooth transitions to all chart containers
    const charts = document.querySelectorAll('.chart-container');
    charts.forEach(chart => {
        chart.style.transition = 'all 0.3s ease';
    });
    
    // Ensure Chart.js charts have proper styling
    const canvases = document.querySelectorAll('canvas[id*="Chart"]');
    canvases.forEach(canvas => {
        const container = canvas.parentElement;
        if (container && !container.classList.contains('chart-container')) {
            container.classList.add('chart-container');
        }
    });
}

/**
 * Mobile Experience Enhancements
 */
function enhanceMobileExperience() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Adjust loading overlay text size
        const overlayContent = document.querySelector('.loading-overlay-content');
        if (overlayContent) {
            overlayContent.style.padding = '20px';
        }
        
        // Ensure toasts don't overflow
        const toasts = document.querySelectorAll('.toast');
        toasts.forEach(toast => {
            toast.style.maxWidth = 'calc(100vw - 20px)';
        });
        
        // Make calendar more touch-friendly
        const calendarDays = document.querySelectorAll('.calendar-day');
        calendarDays.forEach(day => {
            day.style.minHeight = '44px'; // Touch-friendly minimum
            day.style.padding = '4px';
        });
    }
}

/**
 * Wrap API calls with loading overlay
 */
const originalCallClinicianAPI = callClinicianAPI;
async function callClinicianAPIWithLoader(endpoint, method = 'GET', body = null, showLoader = true) {
    if (showLoader) showLoadingOverlay('Loading data...');
    try {
        const result = await originalCallClinicianAPI(endpoint, method, body);
        if (showLoader) hideLoadingOverlay();
        return result;
    } catch (error) {
        if (showLoader) hideLoadingOverlay();
        showToast('error', 'Error', error.message, 5000);
        throw error;
    }
}

// Initialize enhancements on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        updateChartStyles();
        enhanceMobileExperience();
    });
} else {
    updateChartStyles();
    enhanceMobileExperience();
}

// Update on window resize
window.addEventListener('resize', () => {
    enhanceMobileExperience();
});

// Override original API function to use loader version for key operations
const originalLoadAnalyticsDashboard = loadAnalyticsDashboard;
async function loadAnalyticsDashboardWithLoader() {
    showLoadingOverlay('Loading dashboard...');
    try {
        await originalLoadAnalyticsDashboard();
        hideLoadingOverlay();
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Dashboard Error', 'Failed to load dashboard');
    }
}

const originalLoadPatients = loadPatients;
async function loadPatientsWithLoader() {
    showLoadingOverlay('Loading patients...');
    try {
        await originalLoadPatients();
        hideLoadingOverlay();
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Patients Error', 'Failed to load patients');
    }
}

// ========== TIER 2.1: C-SSRS ASSESSMENT UI FUNCTIONS ==========

/**
 * Start a new C-SSRS assessment session
 * @param {string} username - Patient username
 * @returns {Promise<Object>} Assessment session with questions
 */
async function startCSSRSAssessment(username) {
    showLoadingOverlay('Starting C-SSRS Assessment...');
    try {
        const response = await fetch('/api/c-ssrs/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify({
                clinician_username: currentUser
            })
        });
        
        if (!response.ok) throw new Error('Failed to start assessment');
        
        const data = await response.json();
        hideLoadingOverlay();
        return data;
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Assessment Error', error.message);
        return null;
    }
}

/**
 * Display C-SSRS assessment form modal
 * @param {Object} questions - Array of C-SSRS questions
 * @param {Object} answerOptions - Available answer choices
 */
function displayCSSRSForm(questions, answerOptions) {
    const modal = document.createElement('div');
    modal.id = 'cssrs-modal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content cssrs-assessment-form">
            <div class="modal-header">
                <h2>Columbia-Suicide Severity Rating Scale (C-SSRS)</h2>
                <p class="assessment-subtitle">6-Question Assessment | Please answer all questions honestly</p>
                <button class="close-btn" onclick="closeCSSRSModal()">✕</button>
            </div>
            
            <div class="assessment-progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="cssrs-progress"></div>
                </div>
                <span id="cssrs-question-count">Question 1 of 6</span>
            </div>
            
            <form id="cssrs-form" onsubmit="submitCSSRSResponse(event)">
                <div id="cssrs-questions-container"></div>
                
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeCSSRSModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit Assessment</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('active');
    
    // Render questions
    renderCSSRSQuestions(questions, answerOptions);
}

/**
 * Render C-SSRS questions in the form
 */
function renderCSSRSQuestions(questions, answerOptions) {
    const container = document.getElementById('cssrs-questions-container');
    container.innerHTML = '';
    
    questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'cssrs-question-group';
        questionDiv.innerHTML = `
            <div class="question-header">
                <span class="question-number">Q${question.id}:</span>
                <span class="question-text">${question.text}</span>
            </div>
            
            <div class="question-options">
                ${Object.entries(answerOptions).map(([score, label]) => `
                    <label class="radio-option">
                        <input type="radio" 
                               name="q${question.id}" 
                               value="${score}" 
                               required>
                        <span class="option-label">
                            <strong>${score}</strong> - ${label}
                        </span>
                    </label>
                `).join('')}
            </div>
        `;
        
        container.appendChild(questionDiv);
        
        // Add event listener to update progress
        const radios = questionDiv.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', () => updateCSSRSProgress(questions.length));
        });
    });
}

/**
 * Update progress bar and question counter
 */
function updateCSSRSProgress(totalQuestions) {
    const form = document.getElementById('cssrs-form');
    const answeredQuestions = form.querySelectorAll('input[type="radio"]:checked').length;
    
    const progressPercent = (answeredQuestions / totalQuestions) * 100;
    document.getElementById('cssrs-progress').style.width = progressPercent + '%';
    document.getElementById('cssrs-question-count').textContent = 
        `Question ${Math.min(answeredQuestions + 1, totalQuestions)} of ${totalQuestions}`;
}

/**
 * Submit C-SSRS assessment responses
 */
async function submitCSSRSResponse(event) {
    event.preventDefault();
    
    showLoadingOverlay('Scoring Assessment...');
    
    try {
        const form = document.getElementById('cssrs-form');
        const formData = new FormData(form);
        
        const responses = {
            q1: parseInt(formData.get('q1')),
            q2: parseInt(formData.get('q2')),
            q3: parseInt(formData.get('q3')),
            q4: parseInt(formData.get('q4')),
            q5: parseInt(formData.get('q5')),
            q6: parseInt(formData.get('q6')),
            clinician_username: currentUser
        };
        
        const response = await fetch('/api/c-ssrs/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify(responses)
        });
        
        if (!response.ok) throw new Error('Failed to submit assessment');
        
        const result = await response.json();
        
        hideLoadingOverlay();
        closeCSSRSModal();
        
        // Display results
        displayCSSRSResults(result);
        
        // If high/critical risk, trigger safety plan
        if (result.requires_safety_plan) {
            setTimeout(() => displaySafetyPlanForm(result.assessment_id), 1000);
        }
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Assessment Failed', error.message);
    }
}

/**
 * Display C-SSRS assessment results to patient
 */
function displayCSSRSResults(result) {
    const riskColors = {
        'low': '#4CAF50',
        'moderate': '#FFC107',
        'high': '#FF9800',
        'critical': '#F44336'
    };
    
    const modal = document.createElement('div');
    modal.id = 'cssrs-results-modal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content cssrs-results">
            <div class="modal-header">
                <h2>Assessment Complete</h2>
            </div>
            
            <div class="assessment-results">
                <div class="risk-score-display" style="border-color: ${riskColors[result.risk_level]}">
                    <div class="risk-level" style="color: ${riskColors[result.risk_level]}">
                        ${result.risk_level.toUpperCase()}
                    </div>
                    <div class="risk-score">Score: ${result.total_score}/30</div>
                </div>
                
                <div class="patient-message">
                    <p>${result.patient_message}</p>
                </div>
                
                ${result.next_steps ? `
                    <div class="next-steps">
                        <h4>Next Steps:</h4>
                        <ul>
                            ${result.next_steps.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${result.emergency_contacts ? `
                    <div class="emergency-contacts">
                        <h4>Emergency Support:</h4>
                        <div class="contact-list">
                            ${Object.entries(result.emergency_contacts).map(([type, value]) => `
                                <div class="contact-item">
                                    <strong>${type}:</strong> ${value}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
            
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" onclick="closeCSSRSResultsModal()">
                    Continue
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('active');
}

/**
 * Display safety plan form modal
 */
function displaySafetyPlanForm(assessmentId) {
    const modal = document.createElement('div');
    modal.id = 'safety-plan-modal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content safety-plan-form">
            <div class="modal-header">
                <h2>Create Your Safety Plan</h2>
                <p class="form-subtitle">Complete this plan to keep yourself safe</p>
            </div>
            
            <form id="safety-plan-form" onsubmit="submitSafetyPlan(event, ${assessmentId})">
                <div class="safety-plan-section">
                    <h4>1. Warning Signs</h4>
                    <p>What signs tell you that a crisis is developing?</p>
                    <textarea name="warning_signs" placeholder="e.g., unable to sleep, increased substance use, social withdrawal" rows="3" required></textarea>
                </div>
                
                <div class="safety-plan-section">
                    <h4>2. Internal Coping Strategies</h4>
                    <p>What can you do on your own when you feel suicidal?</p>
                    <textarea name="internal_coping" placeholder="e.g., distraction, mindfulness, exercise, journaling" rows="3" required></textarea>
                </div>
                
                <div class="safety-plan-section">
                    <h4>3. People & Places for Distraction</h4>
                    <p>Who and where can help distract you?</p>
                    <textarea name="distraction_people" placeholder="e.g., trusted friends, family, support groups, safe places" rows="3" required></textarea>
                </div>
                
                <div class="safety-plan-section">
                    <h4>4. People to Contact for Help</h4>
                    <p>Who can you call when in crisis?</p>
                    <textarea name="people_for_help" placeholder="Include names, relationships, phone numbers" rows="3" required></textarea>
                </div>
                
                <div class="safety-plan-section">
                    <h4>5. Professional Resources</h4>
                    <p>Emergency and professional contacts</p>
                    <div class="default-resources">
                        • Samaritans: 116 123 (24/7, free)<br>
                        • Emergency: 999 (immediate danger)<br>
                        • Your Clinician: [Contact will be provided]
                    </div>
                </div>
                
                <div class="safety-plan-section">
                    <h4>6. Making Your Environment Safer</h4>
                    <p>Ways to make your environment safer right now</p>
                    <textarea name="means_safety" placeholder="e.g., secure medications, remove sharp objects" rows="3" required></textarea>
                </div>
                
                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary btn-large">Save Safety Plan</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('active');
}

/**
 * Submit safety plan
 */
async function submitSafetyPlan(event, assessmentId) {
    event.preventDefault();
    
    showLoadingOverlay('Saving Safety Plan...');
    
    try {
        const form = document.getElementById('safety-plan-form');
        const formData = new FormData(form);
        
        const safetyPlan = {
            warning_signs: formData.get('warning_signs').split('\n').filter(s => s.trim()),
            internal_coping: formData.get('internal_coping').split('\n').filter(s => s.trim()),
            distraction_people: formData.get('distraction_people').split('\n').filter(s => s.trim()),
            people_for_help: formData.get('people_for_help').split('\n').filter(s => s.trim()),
            professionals: ['Samaritans: 116 123', 'Emergency: 999'],
            means_safety: formData.get('means_safety').split('\n').filter(s => s.trim())
        };
        
        const response = await fetch(`/api/c-ssrs/${assessmentId}/safety-plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': getCsrfToken()
            },
            body: JSON.stringify(safetyPlan)
        });
        
        if (!response.ok) throw new Error('Failed to save safety plan');
        
        hideLoadingOverlay();
        closeSafetyPlanModal();
        
        showToast('success', 'Safety Plan Saved', 'Your safety plan has been saved and will be reviewed by your clinician');
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Save Failed', error.message);
    }
}

/**
 * Display C-SSRS assessment history for patient
 */
async function displayCSSRSHistory(username) {
    showLoadingOverlay('Loading Assessment History...');
    
    try {
        const response = await fetch(`/api/c-ssrs/history`, {
            headers: { 'X-CSRF-Token': getCsrfToken() }
        });
        
        if (!response.ok) throw new Error('Failed to load history');
        
        const data = await response.json();
        hideLoadingOverlay();
        
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content cssrs-history">
                <div class="modal-header">
                    <h2>Assessment History</h2>
                </div>
                
                <div class="history-list">
                    ${data.assessments.length > 0 ? data.assessments.map(assessment => `
                        <div class="history-item">
                            <div class="history-date">${new Date(assessment.created_at).toLocaleDateString()}</div>
                            <div class="history-risk" style="color: ${getRiskColor(assessment.risk_level)}">
                                ${assessment.risk_level.toUpperCase()} - Score: ${assessment.total_score}
                            </div>
                            <div class="history-reasoning">${assessment.reasoning}</div>
                            <button class="btn btn-sm" onclick="viewAssessmentDetails(${assessment.assessment_id})">
                                View Details
                            </button>
                        </div>
                    `).join('') : '<p>No assessments completed yet.</p>'}
                </div>
                
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.classList.add('active');
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'History Error', error.message);
    }
}

/**
 * Close C-SSRS modals
 */
function closeCSSRSModal() {
    const modal = document.getElementById('cssrs-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

function closeCSSRSResultsModal() {
    const modal = document.getElementById('cssrs-results-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

function closeSafetyPlanModal() {
    const modal = document.getElementById('safety-plan-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

/**
 * Get color for risk level
 */
function getRiskColor(riskLevel) {
    const colors = {
        'low': '#4CAF50',
        'moderate': '#FFC107',
        'high': '#FF9800',
        'critical': '#F44336'
    };
    return colors[riskLevel] || '#999';
}
// ============================================================================
// TIER 2.2: CRISIS ALERT SYSTEM
// ============================================================================

/**
 * Load crisis alerts dashboard for clinician
 */
async function loadCrisisAlerts() {
    try {
        showLoadingOverlay();
        
        const data = await callClinicianAPI('/api/crisis/alerts', 'GET');
        
        const container = document.getElementById('risk-alerts-container');
        if (!container) return;
        
        if (data.count === 0) {
            container.innerHTML = `
                <div class="alert-card alert-success">
                    <p>✓ No active crisis alerts. All patients appear safe.</p>
                </div>
            `;
            return;
        }
        
        // Group by severity
        const bySeverity = {
            critical: [],
            high: [],
            moderate: [],
            low: []
        };
        
        data.alerts.forEach(alert => {
            if (bySeverity[alert.severity]) {
                bySeverity[alert.severity].push(alert);
            }
        });
        
        let html = '';
        
        // Render critical alerts first
        for (const severity of ['critical', 'high', 'moderate', 'low']) {
            if (bySeverity[severity].length === 0) continue;
            
            html += `<h4 class="severity-${severity}" style="margin-top: 20px; margin-bottom: 10px;">
                ${severity.toUpperCase()} SEVERITY (${bySeverity[severity].length})
            </h4>`;
            
            bySeverity[severity].forEach(alert => {
                const ackedClass = alert.acknowledged ? 'alert-acknowledged' : '';
                const ackedLabel = alert.acknowledged ? '✓ Acknowledged' : '⚠️ Requires Action';
                
                html += `
                    <div class="crisis-alert-card ${ackedClass}">
                        <div class="alert-header">
                            <div>
                                <h5>${alert.title}</h5>
                                <p class="text-sm text-muted">${alert.patient_name} (${alert.patient_username})</p>
                            </div>
                            <span class="severity-badge severity-${alert.severity}">
                                ${alert.severity.toUpperCase()}
                            </span>
                        </div>
                        
                        <div class="alert-body">
                            <p><strong>Type:</strong> ${alert.alert_type}</p>
                            <p><strong>Details:</strong> ${alert.details || 'N/A'}</p>
                            <p><strong>Source:</strong> ${alert.source} (Confidence: ${Math.round(alert.confidence)}%)</p>
                            <p class="text-xs text-muted">Created: ${formatDate(alert.created_at)}</p>
                        </div>
                        
                        <div class="alert-status">
                            <span class="status-label">${ackedLabel}</span>
                            ${alert.acknowledged_at ? `
                                <p class="text-xs">by ${alert.acknowledged_by} at ${formatDate(alert.acknowledged_at)}</p>
                            ` : ''}
                        </div>
                        
                        <div class="alert-actions">
                            ${!alert.acknowledged ? `
                                <button class="btn btn-sm btn-primary" 
                                    onclick="showCrisisAcknowledgmentModal(${alert.id}, '${alert.patient_username}')">
                                    Acknowledge & Respond
                                </button>
                            ` : `
                                <button class="btn btn-sm btn-success" 
                                    onclick="resolveCrisisAlert(${alert.id})">
                                    Mark as Resolved
                                </button>
                            `}
                            <button class="btn btn-sm btn-secondary" 
                                onclick="showCopingStrategies()">
                                View Coping Strategies
                            </button>
                        </div>
                    </div>
                `;
            });
        }
        
        container.innerHTML = html;
        hideLoadingOverlay();
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Crisis Alerts Error', error.message);
    }
}

/**
 * Show modal for acknowledging crisis alert
 */
async function showCrisisAcknowledgmentModal(alertId, patientUsername) {
    try {
        // Get crisis contacts and coping strategies
        const contactsData = await callClinicianAPI(`/api/crisis/contacts?patient=${patientUsername}`, 'GET');
        const strategiesData = await callClinicianAPI('/api/crisis/coping-strategies', 'GET');
        
        const modal = document.createElement('div');
        modal.id = 'crisis-ack-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content crisis-modal">
                <div class="modal-header">
                    <h3>⚠️ Crisis Response</h3>
                    <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                
                <div class="modal-body">
                    <div class="tabs-nav">
                        <button class="tab-btn active" onclick="switchCrisisTab(this, 'contacts')">
                            Emergency Contacts
                        </button>
                        <button class="tab-btn" onclick="switchCrisisTab(this, 'strategies')">
                            Coping Strategies
                        </button>
                        <button class="tab-btn" onclick="switchCrisisTab(this, 'response')">
                            Acknowledge Alert
                        </button>
                    </div>
                    
                    <!-- Contacts Tab -->
                    <div id="tab-contacts" class="tab-content active">
                        <h4>Patient's Emergency Contacts</h4>
                        ${contactsData.contacts && contactsData.contacts.length > 0 ? `
                            <div class="contacts-list">
                                ${contactsData.contacts.map(contact => `
                                    <div class="contact-card">
                                        <div class="contact-info">
                                            <h5>${contact.name}</h5>
                                            <p><strong>Relationship:</strong> ${contact.relationship}</p>
                                            ${contact.phone ? `<p><strong>Phone:</strong> <a href="tel:${contact.phone}">${contact.phone}</a></p>` : ''}
                                            ${contact.email ? `<p><strong>Email:</strong> <a href="mailto:${contact.email}">${contact.email}</a></p>` : ''}
                                            ${contact.is_primary ? '<span class="badge-primary">Primary Contact</span>' : ''}
                                            ${contact.is_professional ? '<span class="badge-professional">Professional</span>' : ''}
                                        </div>
                                        <button class="btn btn-sm btn-secondary" 
                                            onclick="notifyEmergencyContact('${contact.phone}', '${contact.name}')">
                                            Notify
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p>No emergency contacts on file.</p>'}
                    </div>
                    
                    <!-- Coping Strategies Tab -->
                    <div id="tab-strategies" class="tab-content">
                        <h4>Recommend Coping Strategies to Patient</h4>
                        <div class="strategies-grid">
                            ${strategiesData.strategies.map(strategy => `
                                <div class="strategy-card">
                                    <h5>${strategy.title}</h5>
                                    <p class="text-sm">${strategy.description}</p>
                                    <div class="strategy-details">
                                        <span class="badge">${strategy.category}</span>
                                        <span class="text-xs text-muted">${strategy.duration_minutes} min</span>
                                    </div>
                                    <button class="btn btn-sm btn-secondary" 
                                        onclick="sendCopingStrategy(${strategy.id}, '${strategy.title}')">
                                        Send to Patient
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Response Tab -->
                    <div id="tab-response" class="tab-content">
                        <h4>Document Your Response</h4>
                        <form onsubmit="submitCrisisAcknowledgment(event, ${alertId})">
                            <div class="form-group">
                                <label for="action-taken">Action Taken:</label>
                                <textarea id="action-taken" name="action_taken" 
                                    placeholder="Document the steps you've taken to address this crisis..."
                                    required></textarea>
                            </div>
                            
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="follow-up-scheduled" name="follow_up">
                                    Schedule Follow-up
                                </label>
                            </div>
                            
                            <div id="follow-up-date" style="display:none;">
                                <label for="follow-up-when">Follow-up Date/Time:</label>
                                <input type="datetime-local" id="follow-up-when" name="follow_up_when">
                            </div>
                            
                            <button type="submit" class="btn btn-primary btn-lg">
                                Acknowledge & Send Response
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.classList.add('active');
        
        // Show follow-up date when checkbox is checked
        document.getElementById('follow-up-scheduled').addEventListener('change', (e) => {
            document.getElementById('follow-up-date').style.display = e.target.checked ? 'block' : 'none';
        });
        
    } catch (error) {
        showToast('error', 'Modal Error', error.message);
    }
}

/**
 * Switch between crisis response tabs
 */
function switchCrisisTab(button, tabName) {
    // Remove active from all tabs and buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    
    // Add active to clicked
    button.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

/**
 * Submit crisis alert acknowledgment
 */
async function submitCrisisAcknowledgment(event, alertId) {
    event.preventDefault();
    
    try {
        showLoadingOverlay();
        
        const actionTaken = document.getElementById('action-taken').value;
        
        const response = await callClinicianAPI(`/api/crisis/alerts/${alertId}/acknowledge`, 'POST', {
            action_taken: actionTaken
        });
        
        hideLoadingOverlay();
        showToast('success', 'Alert Acknowledged', 'Crisis response documented');
        
        // Close modal
        document.getElementById('crisis-ack-modal').remove();
        
        // Refresh alerts
        loadCrisisAlerts();
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Acknowledgment Error', error.message);
    }
}

/**
 * Resolve crisis alert
 */
async function resolveCrisisAlert(alertId) {
    if (!confirm('Mark this crisis alert as resolved?')) return;
    
    try {
        showLoadingOverlay();
        
        await callClinicianAPI(`/api/crisis/alerts/${alertId}/resolve`, 'POST', {});
        
        hideLoadingOverlay();
        showToast('success', 'Alert Resolved', 'Crisis alert status updated');
        
        loadCrisisAlerts();
        
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', 'Resolution Error', error.message);
    }
}

/**
 * Show coping strategies to patient
 */
function showCopingStrategies() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>🧘 Coping Strategies for Crisis Support</h3>
                <button class="btn-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            
            <div class="modal-body">
                <p>Choose a coping strategy to send to the patient right now:</p>
                <div id="strategies-container"></div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.classList.add('active');
    
    loadCopingStrategiesList();
}

/**
 * Load and display coping strategies
 */
async function loadCopingStrategiesList() {
    try {
        const data = await callClinicianAPI('/api/crisis/coping-strategies', 'GET');
        
        const container = document.getElementById('strategies-container');
        container.innerHTML = data.strategies.map(strategy => `
            <div class="strategy-card">
                <h5>${strategy.title}</h5>
                <p>${strategy.description}</p>
                <ul class="strategy-steps">
                    ${strategy.steps.map(step => `<li>${step}</li>`).join('')}
                </ul>
                <div class="text-sm text-muted">Duration: ${strategy.duration_minutes} minutes</div>
                <button class="btn btn-sm btn-primary" 
                    onclick="sendCopingStrategy(${strategy.id}, '${strategy.title}')">
                    Send to Patient
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        showToast('error', 'Strategies Error', error.message);
    }
}

/**
 * Send coping strategy to patient
 */
async function sendCopingStrategy(strategyId, strategyTitle) {
    try {
        showToast('success', 'Coping Strategy Sent', `"${strategyTitle}" sent to patient`);
        
        // In production, this would send a notification/message to the patient
        console.log(`Coping strategy ${strategyId} (${strategyTitle}) sent to patient`);
        
    } catch (error) {
        showToast('error', 'Send Error', error.message);
    }
}

/**
 * Notify emergency contact
 */
async function notifyEmergencyContact(phone, contactName) {
    try {
        if (!phone) {
            showToast('warning', 'No Phone', `No phone number on file for ${contactName}`);
            return;
        }
        
        // Copy to clipboard and show instruction
        navigator.clipboard.writeText(phone).then(() => {
            showToast('info', 'Phone Copied', `Contact: ${contactName} - ${phone}`);
            alert(`Phone number copied to clipboard:\n${phone}\n\nYou can now call or text this contact to alert them of the crisis situation.`);
        });
        
    } catch (error) {
        showToast('error', 'Notification Error', error.message);
    }
}