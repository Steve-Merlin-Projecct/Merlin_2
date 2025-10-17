// Git Lock Metrics Dashboard - JavaScript Logic

let charts = {};
let metricsData = null;
let recentActivity = [];

// ==============================================================================
// Data Loading
// ==============================================================================

async function loadMetrics() {
    try {
        // In real usage, this would be served by a local web server
        // For file:// URLs, metrics must be manually copied to same directory
        const response = await fetch('../../.git/.lock-metrics-summary.json');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        metricsData = await response.json();

        if (metricsData.error) {
            showError(metricsData.error);
            return false;
        }

        hideLoading();
        return true;
    } catch (error) {
        showError(`Failed to load metrics: ${error.message}. Make sure to run 'bash .claude/scripts/git-lock-metrics.sh analyze' first.`);
        return false;
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('../../.git/.lock-metrics.csv');

        if (!response.ok) {
            return;
        }

        const text = await response.text();
        const lines = text.trim().split('\n').slice(1); // Skip header
        recentActivity = lines.slice(-20).reverse().map(line => {
            const [timestamp, event_type, lock_scope, lock_file, duration_ms, operation, pid] = line.split(',');
            return {
                timestamp: parseInt(timestamp),
                event_type,
                lock_scope,
                lock_file,
                duration_ms: parseInt(duration_ms),
                operation,
                pid
            };
        });
    } catch (error) {
        console.error('Failed to load activity:', error);
    }
}

// ==============================================================================
// UI Updates
// ==============================================================================

function updateStats() {
    if (!metricsData) return;

    const stats = metricsData.acquisition_stats;
    const events = metricsData.events;

    document.getElementById('stat-total').textContent = metricsData.total_operations.toLocaleString();
    document.getElementById('stat-avg').textContent = stats.avg_ms.toLocaleString();
    document.getElementById('stat-p95').textContent = stats.p95_ms.toLocaleString();

    // Calculate timeout rate
    const total = events.acquires + events.timeouts;
    const timeoutRate = total > 0 ? ((events.timeouts / total) * 100).toFixed(2) : '0.00';
    document.getElementById('stat-timeout-rate').textContent = timeoutRate;

    // P95 health indicator
    const p95Change = document.getElementById('p95-change');
    if (stats.p95_ms < 1000) {
        p95Change.textContent = '✓ Excellent';
        p95Change.className = 'stat-change good';
    } else if (stats.p95_ms < 5000) {
        p95Change.textContent = '⚠ Acceptable';
        p95Change.className = 'stat-change';
    } else {
        p95Change.textContent = '✗ Needs attention';
        p95Change.className = 'stat-change bad';
    }
}

function updateCharts() {
    if (!metricsData) return;

    const stats = metricsData.acquisition_stats;
    const events = metricsData.events;
    const scope = metricsData.scope_distribution;
    const topOps = metricsData.top_operations;

    // Scope Distribution Chart
    if (charts.scope) charts.scope.destroy();
    charts.scope = new Chart(document.getElementById('scopeChart'), {
        type: 'doughnut',
        data: {
            labels: ['Global Lock', 'Worktree Lock'],
            datasets: [{
                data: [scope.global, scope.worktree],
                backgroundColor: ['#58a6ff', '#3fb950'],
                borderColor: '#0d1117',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#c9d1d9',
                        font: { size: 12 }
                    }
                }
            }
        }
    });

    // Percentiles Chart
    if (charts.percentiles) charts.percentiles.destroy();
    charts.percentiles = new Chart(document.getElementById('percentilesChart'), {
        type: 'bar',
        data: {
            labels: ['Average', 'P50', 'P95', 'P99', 'Max'],
            datasets: [{
                label: 'Time (ms)',
                data: [stats.avg_ms, stats.p50_ms, stats.p95_ms, stats.p99_ms, stats.max_ms],
                backgroundColor: '#58a6ff',
                borderColor: '#1f6feb',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#8b949e' },
                    grid: { color: '#21262d' }
                },
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { display: false }
                }
            }
        }
    });

    // Events Chart
    if (charts.events) charts.events.destroy();
    charts.events = new Chart(document.getElementById('eventsChart'), {
        type: 'bar',
        data: {
            labels: ['Acquisitions', 'Waits', 'Timeouts', 'Stale Removals'],
            datasets: [{
                label: 'Count',
                data: [events.acquires, events.waits, events.timeouts, events.stale_removals],
                backgroundColor: ['#3fb950', '#d29922', '#f85149', '#8b949e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#8b949e' },
                    grid: { color: '#21262d' }
                },
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { display: false }
                }
            }
        }
    });

    // Operations Chart
    if (charts.operations) charts.operations.destroy();

    if (topOps && topOps.length > 0) {
        const labels = topOps.map(op => op.operation.substring(0, 30));
        const data = topOps.map(op => op.count);

        charts.operations = new Chart(document.getElementById('operationsChart'), {
            type: 'horizontalBar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Frequency',
                    data: data,
                    backgroundColor: '#58a6ff',
                    borderWidth: 0
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { color: '#8b949e' },
                        grid: { color: '#21262d' }
                    },
                    y: {
                        ticks: { color: '#8b949e' },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

function updateActivity() {
    const container = document.getElementById('activity-list');

    if (recentActivity.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b949e;">No recent activity</div>';
        return;
    }

    container.innerHTML = recentActivity.map(item => {
        const timestamp = new Date(item.timestamp).toLocaleTimeString();
        const iconClass = item.event_type;
        const icon = {
            'acquire': '🔒',
            'wait': '⏳',
            'timeout': '❌',
            'stale': '🧹'
        }[item.event_type] || '📝';

        const scopeBadge = item.lock_scope === 'global' ? 'Global' : 'Worktree';

        return `
            <div class="activity-item">
                <div class="activity-icon ${iconClass}">${icon}</div>
                <div class="activity-content">
                    <div class="activity-operation">${item.operation}</div>
                    <div class="activity-meta">${timestamp} • ${scopeBadge}</div>
                </div>
                <div class="activity-duration">${item.duration_ms}ms</div>
            </div>
        `;
    }).join('');
}

// ==============================================================================
// UI State Management
// ==============================================================================

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
    document.getElementById('error').textContent = message;
    document.getElementById('dashboard').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
}

function updateTimestamp() {
    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

// ==============================================================================
// Refresh Logic
// ==============================================================================

async function refresh() {
    const loaded = await loadMetrics();

    if (loaded) {
        await loadRecentActivity();
        updateStats();
        updateCharts();
        updateActivity();
        updateTimestamp();
    }
}

// ==============================================================================
// Initialization
// ==============================================================================

async function init() {
    await refresh();

    // Auto-refresh every 5 seconds
    setInterval(refresh, 5000);
}

// Start dashboard
document.addEventListener('DOMContentLoaded', init);
