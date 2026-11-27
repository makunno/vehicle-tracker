import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# HTML Dashboard Template - Distinctive Design
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Vehicle Packet Tracker Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1'>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakob:wght@400;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <style>
        :root {
            --primary: #ec4899;
            --primary-glow: rgba(236, 72, 153, 0.4);
            --bg: #0f0f23;
            --card: #1a1a2e;
            --card-hover: #16213e;
            --accent: #4ade80;
            --text: #f8f9fa;
            --muted: #a3b1c1;
            --border: #2a2a40;
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Abstract background pattern */
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(ellipse 80% 50% at 20% 20%, rgba(236, 72, 153, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse 60% 40% at 80% 80%, rgba(74, 222, 128, 0.05) 0%, transparent 50%),
                var(--bg);
            pointer-events: none;
            animation: bgShift 20s ease infinite;
        }

        @keyframes bgShift {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(5%, 5%); }
        }

        .container {
            max-width: 1300px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Theme accent bars */
        .accent-bar {
            position: fixed;
            top: 0;
            width: 4px;
            height: 100vh;
            background: linear-gradient(var(--primary), var(--accent));
            z-index: 10;
        }

        /* Sidebar */
        .sidebar {
            position: fixed;
            left: 56px;
            top: 56px;
            bottom: 56px;
            width: 240px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 32px 20px;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .sidebar-brand {
            padding: 16px 0;
            border-bottom: 1px solid var(--border);
            margin: -16px -20px 24px;
        }

        .sidebar-brand i {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            margin-right: 12px;
        }

        .sidebar-brand h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }

        .sidebar-nav {
            margin-top: 32px;
        }

        .sidebar-nav a {
            display: block;
            padding: 14px 18px;
            color: var(--muted);
            text-decoration: none;
            border-radius: 10px;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }

        .sidebar-nav a:hover {
            background: var(--card-hover);
            color: var(--text);
            border-left: 3px solid var(--primary);
        }

        .sidebar-nav a.active {
            background: var(--primary-glow);
            color: var(--primary);
            border-left: 3px solid var(--primary);
        }

        .sidebar-nav a:hover i {
            color: var(--primary);
        }

        .sidebar-nav i {
            width: 20px;
            margin-right: 12px;
            flex-shrink: 0;
        }

        /* Main content */
        .main-content {
            margin-left: 296px;
            padding: 32px 40px 24px;
        }

        /* Header */
        .header {
            background: var(--card);
            padding: 28px 32px;
            border-radius: 20px;
            margin-bottom: 32px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        .header-title .icon {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, var(--primary), #f472b6);
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }

        .header-title .info h1 {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--text), var(--muted));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        .header-title .info p {
            font-size: 13px;
            color: var(--muted);
            margin: 4px 0 0;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }

        .stat-card {
            background: var(--card);
            padding: 32px 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--primary);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--primary);
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(236, 72, 153, 0.15);
        }

        .stat-card:hover::before {
            opacity: 1;
        }

        .stat-card .icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary), #f472b6);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            font-size: 24px;
            color: white;
        }

        .stat-card h3 {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .stat-card .number {
            font-family: 'Plus Jakob', serif;
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
            display: inline-block;
        }

        .stat-card .label {
            font-size: 11px;
            color: var(--muted);
        }

        /* Content section */
        .content-section {
            background: var(--card);
            padding: 32px;
            border-radius: 20px;
            border: 1px solid var(--border);
            margin-bottom: 32px;
        }

        .content-section h2 {
            font-family: 'Plus Jakob', serif;
            font-size: 22px;
            font-weight: 600;
            color: var(--text);
            margin: 0 0 24px 0;
            padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }

        /* Vehicles Table */
        .vehicles-table {
            width: 100%;
            border-collapse: collapse;
        }

        .vehicles-table thead {
            background: var(--bg);
        }

        .vehicles-table th {
            padding: 16px 18px;
            text-align: left;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--muted);
            border: none;
        }

        .vehicles-table td {
            padding: 16px 18px;
            border-bottom: 1px solid var(--border);
            transition: 0.2s;
        }

        .vehicles-table tbody tr {
            background: var(--card-hover);
        }

        .vehicles-table tbody tr:hover {
            background: var(--card);
        }

        .vehicles-table .rank {
            width: 40px;
            font-weight: 600;
            color: var(--primary);
        }

        .vehicles-table .vehicle-name {
            font-weight: 500;
        }

        .vehicles-table .packets {
            color: var(--primary);
            font-weight: 600;
        }

        .vehicles-table .status {
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 20px;
            text-transform: uppercase;
        }

        .status-active {
            background: rgba(74, 222, 128, 0.2);
            color: var(--accent);
        }

        .status-watch {
            background: rgba(251, 148, 0, 0.2);
            color: var(--warning);
        }

        /* Add Entry Form */
        .add-section {
            background: var(--card);
            padding: 32px;
            border-radius: 20px;
            border: 1px solid var(--border);
        }

        .add-section h2 {
            font-family: 'Plus Jakob', serif;
            font-size: 18px;
            font-weight: 600;
            color: var(--text);
            margin: 0 0 24px 0;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-size: 12px;
            font-weight: 500;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 14px 16px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text);
            font-size: 14px;
            font-family: 'Space Grotesk', sans-serif;
            transition: all 0.2s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px var(--primary-glow);
        }

        .form-group button {
            width: 100%;
            padding: 14px 24px;
            background: linear-gradient(135deg, var(--primary), #f472b6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Space Grotesk', sans-serif;
            cursor: pointer;
            margin-top: 8px;
            transition: all 0.2s ease;
        }

        .form-group button:hover {
            background: linear-gradient(135deg, #f472b6, #ec4899);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(236, 72, 153, 0.3);
        }

        .form-group button:focus {
            outline: none;
        }

        /* Recent Entries */
        .recent-section {
            margin-top: 32px;
        }

        .recent-section h2 {
            font-family: 'Plus Jakob', serif;
            font-size: 18px;
            font-weight: 600;
            color: var(--text);
            margin: 0 0 20px 0;
        }

        .entry-item {
            display: grid;
            grid-template-columns: 130px 1fr 80px 100px;
            gap: 16px;
            padding: 14px 0;
            border-bottom: 1px solid var(--border);
        }

        .entry-item:last-child {
            border-bottom: none;
        }

        .entry-vehicle {
            font-weight: 500;
        }

        .entry-packets {
            color: var(--primary);
            font-weight: 600;
        }

        .entry-date {
            font-size: 11px;
            color: var(--muted);
        }

        /* Toast */
        .toast-container {
            position: fixed;
            top: 24px;
            right: 24px;
            z-index: 1000;
        }

        .toast {
            position: relative;
            padding: 16px 20px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            min-width: 260px;
            animation: slideInRight 0.3s ease;
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .toast .close {
            position: absolute;
            top: 8px;
            right: 8px;
            color: var(--muted);
            font-size: 18px;
            cursor: pointer;
        }

        /* No data state */
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: var(--muted);
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .sidebar {
                left: 4px;
                width: calc(100vw - 52px);
            }
            .main-content {
                margin-left: 0;
                padding: 20px;
            }
            .header {
                padding: 16px;
            }
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            }
            .entry-item {
                grid-template-columns: 100px 1fr 50px;
            }
            .entry-date {
                grid-column: span 2;
                text-align: center;
                font-size: 10px;
            }
        }

        /* Entrance animations */
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInDelay1 { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInDelay2 { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInDelay3 { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        .delay-1 { animation-delay: 0.1s; }
        .delay-2 { animation-delay: 0.2s; }
        .delay-3 { animation-delay: 0.3s; }
    </style>
</head>
<body>
    <div class='accent-bar' style='left: 56px;'></div>
    <div class='accent-bar' style='left: calc(56px + 240px + 20px);'></div>

    <!-- Sidebar -->
    <div class='sidebar'>
        <div class='sidebar-brand'>
            <i>VT</i>
            <h3>Vehicle Tracker</h3>
        </div>
        <nav class='sidebar-nav'>
            <a href='#dashboard' active>
                <i data-feather='grid'></i>
                Dashboard
            </a>
            <a href='#vehicles'>
                <i data-feather='truck'></i>
                Vehicles
            </a>
            <a href='#add'>
                <i data-feather='plus-circle'></i>
                Add Entry
            </a>
            <a href='#reports'>
                <i data-feather='bar-chart-2'></i>
                Reports
            </a>
        </nav>
    </div>

    <!-- Main Content -->
    <div class='main-content'>
        <!-- Header -->
        <header class='header'>
            <div class='header-title'>
                <div class='icon'>
                    <i data-feather='truck-loading'></i>
                </div>
                <div>
                    <h1>Vehicle Packet Tracker Pro</h1>
                    <p class='sub'>Real-time Gate Monitoring System</p>
                </div>
            </div>
        </header>

        <!-- Stats Section -->
        <section class='stats-section' id='dashboard' style='animation: fadeIn 0.6s ease;'>
            <div class='stats-grid'>
                <div class='stat-card'>
                    <div class='icon'><i data-feather='users'></i></div>
                    <h3>Total Vehicles</h3>
                    <div class='number' id='total-vehicles'>Loading...</div>
                    <div class='label'>Unique vehicle IDs</div>
                </div>
                <div class='stat-card'>
                    <div class='icon'><i data-feather='trending-up'></i></div>
                    <div class='number' id='total-packets'>Loading...</div>
                    <div class='label'>Total packets recorded</div>
                </div>
                <div class='stat-card'>
                    <div class='icon'><i data-feather='clipboard'></i></div>
                    <div class='number' id='total-entries'>Loading...</div>
                    <div class='label'>Total data entries</div>
                </div>
            </div>
        </section>

        <!-- Vehicles Table -->
        <section class='vehicles-section' id='vehicles' style='animation: fadeInDelay1 0.6s ease;'>
            <h2><i data-feather='grid'></i> Vehicle Packet Loads</h2>
            <div class='table-responsive'>
                <table class='vehicles-table' id='vehicle-table'>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Vehicle ID</th>
                            <th>Total Packets</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- JavaScript will populate this -->
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Add Entry Section -->
        <section class='add-section' id='add' style='animation: fadeInDelay2 0.6s ease;'>
            <h2><i data-feather='plus-circle'></i> Add New Data Point</h2>
            <form id='add-entry-form'>
                <div class='form-group'>
                    <label for='vehicle-id' style='color: var(--primary);'>Vehicle ID <span style='color: var(--error);'>*</span></label>
                    <input type='text' id='vehicle-id' placeholder='e.g. HR55AU9547' required>
                </div>
                <div class='form-group'>
                    <label for='packets' style='color: var(--error);'>Packets <span style='color: var(--error);'>*</span></label>
                    <input type='number' id='packets' min='0' required>
                </div>
                <div class='form-group'>
                    <label for='entry-date' style='color: var(--muted);'>Date <span style='color: var(--muted);'>optional</span></label>
                    <input type='date' id='entry-date'>
                </div>
                <button type='submit' style='width: 100%; margin-top: 8px;">
                    <i data-feather='upload'></i> Add Entry to Dashboard
                </button>
            </form>
        </section>

        <!-- Recent Entries -->
        <section class='recent-section' id='recent' style='animation: fadeInDelay3 0.6s ease;'>
            <h2><i data-feather='clock'></i> Recent Entries</h2>
            <div class='recent-entries' id='recent-entries'>
                <!-- JavaScript will populate this -->
            </div>
        </section>
    </main>

    <!-- Toast Container -->
    <div class='toast-container' id='toast-container'>
        <!-- Toast notifications -->
    </div>

    <script>
        // Check for prefers-reduced-motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        feather.replace({ 'duration': prefersReducedMotion ? 0 : 400 });

        // State
        let dashboardData = null;

        // Format functions
        function formatNumber(num) {
            return num.toString().replace(/(?:\B(?=(\d{3})+(?!\d))|(?<=\d{3}))/g, ',');
        }

        function formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const d = new Date(dateStr + 'T00:00:00');
            return isNaN(d) ? 'Invalid' : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        }

        // Show toast notification
        function showToast(message, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            
            const colors = {
                success: { background: 'rgba(74, 222, 128, 0.2)', borderColor: 'var(--accent)' },
                error: { background: 'rgba(239, 67, 52, 0.2)', borderColor: '#f87171' }
            };
            
            const style = colors[type] || colors.success;
            toast.style.cssText = `
                background: ${style.background};
                border: 1px solid ${style.borderColor};
            `;
            
            toast.innerHTML = `
                <i data-feather='${type === 'success' ? 'check-circle' : 'excircle'}' 
                   style='margin-right: 8px; font-size: 16px; color: ${type === 'success' ? 'var(--accent)' : '#f87171'};'>
                </i>
                ${message}
                <span class='close' onclick='this.parentElement.remove()'>&times;</span>
            `;
            
            container.appendChild(toast);
            
            // Auto-remove after 4 seconds
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }

        // Load dashboard data
        async function loadDashboard() {
            try {
                // Fetch vehicle totals
                const vehiclesResp = await fetch('/vehicle_total');
                const vehicles = await vehiclesResp.json();

                // Update stats cards
                const totalVehicles = vehicles.length;
                const totalPackets = vehicles.reduce((sum, v) => sum + v.total_packets, 0);
                document.getElementById('total-vehicles').textContent = totalVehicles;
                document.getElementById('total-packets').textContent = formatNumber(totalPackets);
                document.getElementById('total-entries').textContent = stats.length || 0;

                // Sort vehicles by packet count (descending) and take top 20
                const sortedVehicles = vehicles.sort((a, b) => b.total_packets - a.total_packets).slice(0, 20);
                
                // Build table rows
                const tableBody = document.getElementById('vehicle-table');
                let tableHtml = '';
                
                sortedVehicles.forEach((v, index) => {
                    const rank = index + 1;
                    const statusClass = v.total_packets > 500 ? 'status-active' : 'status-watch';
                    tableHtml += `
                        <tr>
                            <td class='rank'>#${rank}</td>
                            <td class='vehicle-cell'>${v.vehicle_id}</td>
                            <td class='packets'>${formatNumber(v.total_packets)}</td>
                            <td><span class='status-badge ${statusClass}'>${v.total_packets > 500 ? 'Active' : 'Watch'}</span></td>
                        </tr>
                    `;
                });

                if (sortedVehicles.length === 0) {
                    tableHtml = '<tr><td colspan="4" style="text-align:center; color: var(--muted); padding: 20px;">No vehicle data yet</td></tr>';
                }

                tableBody.innerHTML = tableHtml;

                // Fetch recent entries
                const statsResp = await fetch('/stats');
                const stats = await statsResp.json();

                let recentHtml = '';
                const recent = stats.slice(-8);
                recent.forEach(entry => {
                    recentHtml += `
                        <div class='entry-item'>
                            <div class='entry-vehicle'>${entry.vehicle_id}</div>
                            <div class='entry-packets'>${formatNumber(entry.total_packets)} packets</div>
                            <div class='entry-date'>${formatDate(entry.date)}</div>
                        </div>
                    `;
                });

                if (recentHtml === '') {
                    recentHtml = '<p style="font-size: 13px; color: var(--muted); padding: 10px;">No entries yet</p>';
                }

                document.getElementById('recent-entries').innerHTML = recentHtml;

                // Store data for form submission
                dashboardData = { vehicles, stats };

                // Run entrance animations after data loads
                setTimeout(() => {
                    document.querySelectorAll('.fade-in').forEach(el => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    });
                }, 100);
            } catch (err) {
                console.error('Failed to load dashboard:', err);
                showToast('Error loading dashboard data', 'error');
            }
        }

        // Handle add entry form
        document.getElementById('add-entry-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const vehicleId = document.getElementById('vehicle-id').value.trim();
            const packets = document.getElementById('packets').value;
            const date = document.getElementById('entry-date').value;

            if (!vehicleId) {
                showToast('Please enter a Vehicle ID', 'error');
                return;
            }

            try {
                const resp = await fetch('/add_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        vehicle_id: vehicleId,
                        entry_date: date,
                        packet_count: parseInt(packets) || 0
                    })
                });

                const data = await resp.json();

                if (data.status === 'added') {
                    showToast('Entry added successfully!');
                    document.getElementById('add-entry-form').reset();
                    document.getElementById('entry-date').value = new Date().toISOString().split('T')[0];
                    loadDashboard();
                } else {
                    showToast('Error: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch (err) {
                showToast('Request failed: ' + err.message, 'error');
                console.error(err);
            }
        });

        // Initial load
        loadDashboard();
    </script>
</body>
</html>
'''

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def init_db():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'data.db'))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            entry_date TEXT NOT NULL,
            packet_count INTEGER NOT NULL,
            photo_filename TEXT
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/', methods=['GET'])
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photo' not in request.files:
        return 'No file part', 400
    file = request.files['photo']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'filename': filename}), 200
    return 'File type not allowed', 400


@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()
    vehicle_id = data.get('vehicle_id')
    entry_date = data.get('entry_date')
    packet_count = data.get('packet_count')
    
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id is required'}), 400
    
    conn, c = get_db()
    try:
        c.execute('''
            INSERT INTO entries (vehicle_id, entry_date, packet_count, photo_filename)
            VALUES (?, ?, ?, ?)
        ''', (vehicle_id, entry_date or '', packet_count or 0, None))
        conn.commit()
    finally:
        conn.close()
    return jsonify({'status': 'added'})


@app.route('/stats')
def stats():
    conn, c = get_db()
    c.execute('''
        SELECT vehicle_id, entry_date, SUM(packet_count) as total_packets
        FROM entries
        GROUP BY vehicle_id, entry_date
        ORDER BY entry_date, vehicle_id
    ''')
    rows = c.fetchall()
    conn.close()
    result = [{'vehicle_id': row[0], 'date': row[1], 'total_packets': row[2]} for row in rows]
    return jsonify(result)


@app.route('/vehicle_total')
def vehicle_total():
    vid = request.args.get('vehicle_id')
    conn, c = get_db()
    if vid:
        c.execute('''
            SELECT SUM(packet_count) as total_packets FROM entries WHERE vehicle_id = ?
        ''', (vid,))
        row = c.fetchone()
        result = [{'vehicle_id': vid, 'total_packets': row[0] if row[0] else 0}]
    else:
        c.execute('''
            SELECT vehicle_id, SUM(packet_count) as total_packets FROM entries GROUP BY vehicle_id
        ''')
        rows = c.fetchall()
        result = [{'vehicle_id': row[0], 'total_packets': row[1]} for row in rows]
    conn.close()
    return jsonify(result)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)