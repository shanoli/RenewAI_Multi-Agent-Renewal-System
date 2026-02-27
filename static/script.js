document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginSection = document.getElementById('login-section');
    const dashboardSection = document.getElementById('dashboard-section');
    const userInfo = document.getElementById('user-info');
    const userNameSpan = document.getElementById('user-name');
    const logoutBtn = document.getElementById('logout-btn');

    let token = localStorage.getItem('token');
    let user = JSON.parse(localStorage.getItem('user'));

    if (token && user) {
        showDashboard();
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password: 'dummy' })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data));
                token = data.access_token;
                user = data;
                showDashboard();
            } else {
                alert('Login failed. Please check your email.');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
    });

    function showDashboard() {
        loginSection.classList.add('hidden');
        dashboardSection.classList.remove('hidden');
        userInfo.classList.remove('hidden');
        userNameSpan.textContent = user.name;
        fetchOverview();
        fetchPolicies(); // Load policies immediately
    }

    async function fetchWithAuth(url, options = {}) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
        try {
            const response = await fetch(url, options);
            if (response.status === 401) {
                handleUnauthorized();
                return null;
            }
            return response;
        } catch (e) {
            console.error('Fetch error:', e);
            return null;
        }
    }

    function handleUnauthorized() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.reload();
    }

    async function fetchOverview() {
        const response = await fetchWithAuth('/dashboard/overview');
        if (response && response.ok) {
            const data = await response.json();
            document.getElementById('total-policies').textContent = data.total_policies || 0;
            document.getElementById('active-renewals').textContent = data.active_policies || 0;
            document.getElementById('total-escalations').textContent = data.open_escalations || 0;
        }
    }

    async function fetchPolicies() {
        const response = await fetchWithAuth('/dashboard/policies');
        if (response && response.ok) {
            const data = await response.json();
            const tbody = document.querySelector('#policies-table tbody');
            if (!tbody) return;
            tbody.innerHTML = '';

            data.policies.forEach(policy => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${policy.policy_id}</td>
                    <td>${policy.customer_name}</td>
                    <td>${policy.policy_type}</td>
                    <td>${policy.segment}</td>
                    <td><span class="status-tag">${policy.status}</span></td>
                    <td>
                        <button class="btn-sm" onclick="triggerWorkflow('${policy.policy_id}')">🚀 Trigger</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // Workflow Monitor Logic
    const modal = document.getElementById('workflow-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const timeline = document.getElementById('workflow-timeline');
    const logsContainer = document.getElementById('logs-container');
    const monitorPolicyId = document.getElementById('monitor-policy-id');
    const monitorStatus = document.getElementById('monitor-status');

    let monitorInterval = null;
    // Step IDs mapped to possible backend current_node values
    const workflowSteps = [
        { id: 'ORCHESTRATOR', label: 'Orchestrator' },
        { id: 'CRITIQUE_A', label: 'Critique A' },
        { id: 'PLANNER', label: 'Planner' },
        { id: 'DRAFT_AND_GREETING', label: 'Drafting' },
        { id: 'CRITIQUE_B', label: 'Critique B' },
        { id: 'CHANNEL_SEND', label: 'Delivery' }
    ];

    window.triggerWorkflow = async (policyId) => {
        const response = await fetchWithAuth('/renewal/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ policy_id: policyId })
        });

        if (response && response.ok) {
            startMonitor(policyId);
        } else {
            alert('Could not trigger workflow. Check policy status.');
        }
    };

    function startMonitor(policyId) {
        modal.classList.remove('hidden');
        monitorPolicyId.textContent = policyId;
        monitorStatus.textContent = 'RUNNING';

        timeline.innerHTML = workflowSteps.map((step, idx) => `
            <div class="step" id="step-${step.id}">
                <div class="dot">${idx + 1}</div>
                <div class="step-label">${step.label}</div>
            </div>
        `).join('');

        logsContainer.innerHTML = '<p class="empty-msg">Agents connecting...</p>';

        if (monitorInterval) clearInterval(monitorInterval);
        monitorInterval = setInterval(() => updateMonitor(policyId), 2000);
        updateMonitor(policyId);
    }

    async function updateMonitor(policyId) {
        const statusRes = await fetchWithAuth(`/renewal/status/${policyId}`);
        if (!statusRes || !statusRes.ok) return;
        const statusData = await statusRes.json();

        const currentNode = statusData.current_node;
        let foundCurrent = false;

        workflowSteps.forEach(step => {
            const stepEl = document.getElementById(`step-${step.id}`);
            if (!stepEl) return;

            if (step.id === currentNode) {
                stepEl.classList.add('active');
                stepEl.classList.remove('completed');
                foundCurrent = true;
            } else if (!foundCurrent) {
                stepEl.classList.add('completed');
                stepEl.classList.remove('active');
            } else {
                stepEl.classList.remove('active', 'completed');
            }
        });

        const logsRes = await fetchWithAuth(`/renewal/logs/${policyId}`);
        if (logsRes && logsRes.ok) {
            const logsData = await logsRes.json();
            if (logsData.logs.length > 0) {
                logsContainer.innerHTML = logsData.logs.map(log => `
                    <div class="log-entry">
                        <span class="log-time">${new Date(log.created_at).toLocaleTimeString()}</span>
                        <span class="log-node">[${log.node_name.toUpperCase()}]</span>
                        <span class="log-content">${log.content}</span>
                    </div>
                `).join('');
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }
        }

        if (currentNode === 'COMPLETED' || currentNode === 'ESCALATION') {
            monitorStatus.textContent = currentNode;
            clearInterval(monitorInterval);
            if (currentNode === 'COMPLETED') {
                document.querySelectorAll('.step').forEach(s => s.classList.add('completed'));
            }
        }
    }

    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
        if (monitorInterval) clearInterval(monitorInterval);
    });

    const navItems = document.querySelectorAll('.sidebar nav li');
    const views = document.querySelectorAll('.view');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const view = item.getAttribute('data-view');
            const viewId = view + '-view';
            views.forEach(v => v.classList.add('hidden'));
            const targetView = document.getElementById(viewId);
            if (targetView) targetView.classList.remove('hidden');

            if (view === 'overview') fetchOverview();
            if (view === 'policies') fetchPolicies();
        });
    });
});
