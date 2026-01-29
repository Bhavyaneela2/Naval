
const map = L.map('map-select').setView([20.0, 80.0], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
let marker;
map.on('click', (e) => {
    if (marker) map.removeLayer(marker);
    marker = L.marker(e.latlng).addTo(map);
    document.getElementById('lat').value = e.latlng.lat.toFixed(5);
    document.getElementById('lng').value = e.latlng.lng.toFixed(5);
});

async function startScan() {
    const lat = document.getElementById('lat').value;
    const audio = document.getElementById('audioFile').files[0];
    const image = document.getElementById('imageFile').files[0];
    
    if (!lat || !audio || !image) { alert("Please select a location and upload files."); return; }
    
    document.getElementById('page-1').classList.add('hidden');
    document.getElementById('page-2').classList.remove('hidden');
    
    let width = 0;
    const interval = setInterval(() => { width += 5; document.getElementById('loaderBar').style.width = width + '%'; if(width > 90) clearInterval(interval); }, 100);
    
    const formData = new FormData();
    formData.append('lat', lat); formData.append('lng', document.getElementById('lng').value);
    formData.append('audio_file', audio); formData.append('image_file', image);
    
    try {
        const res = await fetch('/scan-area', { method: 'POST', body: formData });
        const data = await res.json();
        document.getElementById('loaderBar').style.width = '100%';
        setTimeout(() => renderDashboard(data.data), 500);
    } catch (err) { alert("Error connecting to AI Engine"); console.error(err); }
}

function renderDashboard(zones) {
    document.getElementById('page-2').classList.add('hidden');
    document.getElementById('page-3').classList.remove('hidden');
    const container = document.getElementById('cards-container'); container.innerHTML = '';
    const resMap = L.map('result-map').setView([zones[0].lat, zones[0].lng], 13);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(resMap);
    
    const labels = []; const aScores = []; const iScores = [];
    zones.forEach(z => {
        const card = document.createElement('div');
        card.className = `card ${z.color}`;
        card.innerHTML = `<div style="font-size:0.8rem; opacity:0.8;">${z.id} // ${z.name}</div><div class="score-big">${z.total_score}%</div><div style="font-size:0.8rem;">LEVEL: ${z.level}</div><small>Audio: ${z.audio_score} | Image: ${z.image_score}</small>`;
        container.appendChild(card);
        const bounds = [[z.lat - 0.002, z.lng - 0.002], [z.lat + 0.002, z.lng + 0.002]];
        let cHex = z.color === 'red' ? '#f87171' : (z.color === 'yellow' ? '#facc15' : '#4ade80');
        L.rectangle(bounds, { color: cHex, weight: 1 }).addTo(resMap).bindPopup(`<b>${z.id}</b>: ${z.level}`);
        labels.push(z.id); aScores.push(z.audio_score); iScores.push(z.image_score);
    });
    
    new Chart(document.getElementById('riskChart'), {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Audio', data: aScores, backgroundColor: '#38bdf8' }, { label: 'Visual', data: iScores, backgroundColor: '#c084fc' }] },
        options: { scales: { y: { beginAtZero: true, max: 100, grid: { color: '#334155'} } }, plugins: { legend: { labels: { color: 'white' } } } }
    });
}
