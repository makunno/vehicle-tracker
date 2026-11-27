document.getElementById('entryForm').addEventListener('submit', async (e) => {
    console.log('Form submitted');
    e.preventDefault();
    const vehicleId = document.getElementById('vehicle_id').value.trim();
    console.log('Vehicle ID:', vehicleId);
    const entryDate = document.getElementById('entry_date').value;
    console.log('Date:', entryDate);
    const packetCount = document.getElementById('packet_count').value;
    console.log('Packets:', packetCount);
    const photoFile = document.getElementById('photo').files[0];
    let photoFilename = '';

    // If only vehicle ID is provided (no date, no packet count), show total packets for that vehicle
    if (!entryDate && !packetCount) {
        console.log('Fetching vehicle total for:', vehicleId);
        try {
            const totalResp = await fetch(`/vehicle_total?vehicle_id=${encodeURIComponent(vehicleId)}`);
            console.log('Total resp status:', totalResp.status);
            if (!totalResp.ok) {
                const errText = await totalResp.text();
                throw new Error(`Server error: ${errText}`);
            }
            const totalData = await totalResp.json();
            console.log('Total data:', totalData);
            const totalPackets = totalData[0] ? totalData[0].total_packets : 0;
            alert(`Vehicle ${vehicleId} has brought a total of ${totalPackets} packets.`);
            document.getElementById('entryForm').reset();
            return;
        } catch (err) {
            alert('Error: ' + err.message);
            console.error(err);
            return;
        }
    }

    // Otherwise, add new data entry (date and/or packet count optional)
    const formData = new FormData();
    formData.append('vehicle_id', vehicleId);
    if (entryDate) formData.append('entry_date', entryDate);
    if (packetCount) formData.append('packet_count', packetCount);
    if (photoFile) {
        const uploadResp = await fetch('/upload', {
            method: 'POST',
            body: photoFile
        });
        if (!uploadResp.ok) {
            const err = await uploadResp.json();
            alert('Photo upload failed: ' + err.error);
            return;
        }
        const {filename} = await uploadResp.json();
        photoFilename = filename;
        formData.append('photo_filename', filename);
    }

    const jsonData = {
        vehicle_id: vehicleId,
        entry_date: entryDate || '',
        packet_count: packetCount || 0,
        photo_filename: photoFilename
    };

    try {
        const addResp = await fetch('/add_data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(jsonData)
        });
        if (!addResp.ok) {
            const err = await addResp.json();
            alert('Add data failed: ' + err.error);
            return;
        }
        // Reset form
        document.getElementById('entryForm').reset();
        document.getElementById('photo').value = '';
        // Load dashboard
        loadDashboard();
    } catch (err) {
        alert('Error: ' + err.message);
        console.error(err);
    }
});

// Load dashboard data
async function loadDashboard() {
    try {
        // Get vehicle totals
        const resp = await fetch('/vehicle_total');
        const vehicles = await resp.json();
        
        // Update stats cards
        const totalVehicles = vehicles.length;
        const totalPackets = vehicles.reduce((sum, v) => sum + v.total_packets, 0);
        const statsResp = await fetch('/stats');
        const stats = await statsResp.json();
        const totalEntries = stats.length;  // count of rows = number of entries
        
        document.getElementById('total-vehicles').textContent = totalVehicles;
        document.getElementById('total-packets').textContent = totalPackets;
        document.getElementById('total-entries').textContent = totalEntries;
        
        // Populate vehicle table (top 20 vehicles by packet count)
        const tableBody = document.getElementById('vehicle-table');
        tableBody.innerHTML = '';
        // Sort by total_packets descending and take top 20
        const sorted = vehicles.sort((a, b) => b.total_packets - a.total_packets).slice(0, 20);
        sorted.forEach(v => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${v.vehicle_id}</td><td>${v.total_packets}</td><td></td><td></td>`;
            tableBody.appendChild(row);
        });
        if (vehicles.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No data yet</td></tr>';
        }
    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

// Initial load
loadDashboard();