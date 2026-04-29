from flask import Flask, request, jsonify
import datetime
import sqlite3

app = Flask(__name__)

# 🗄️ INIT DATABASE
def init_db():
    conn = sqlite3.connect('agrosense.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moisture INTEGER,
            status TEXT,
            temperature REAL,
            humidity INTEGER,
            ldr INTEGER,
            time TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


latest_data = {
    "moisture": None,
    "status": None,
    "temperature": None,
    "humidity": None,
    "ldr": None,
    "time": None
}


# 📡 RECEIVE DATA FROM ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    content = request.json

    latest_data["moisture"] = content.get("moisture")
    latest_data["status"] = content.get("status")
    latest_data["temperature"] = content.get("temperature")
    latest_data["humidity"] = content.get("humidity")
    latest_data["ldr"] = content.get("ldr")
    latest_data["time"] = datetime.datetime.now().strftime("%H:%M:%S")

    # 🗄️ SAVE TO DATABASE
    conn = sqlite3.connect('agrosense.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO sensor_data (moisture, status, temperature, humidity, ldr, time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        latest_data["moisture"],
        latest_data["status"],
        latest_data["temperature"],
        latest_data["humidity"],
        latest_data["ldr"],
        latest_data["time"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "OK"})


# 📊 LATEST DATA
@app.route('/latest')
def latest():
    return jsonify(latest_data)


# 📈 HISTORY FROM DATABASE
@app.route('/history')
def history_data():
    conn = sqlite3.connect('agrosense.db')
    c = conn.cursor()

    c.execute("""
        SELECT moisture, temperature, humidity, ldr, time 
        FROM sensor_data 
        ORDER BY id DESC LIMIT 30
    """)
    
    rows = c.fetchall()
    conn.close()

    data = []
    for r in rows[::-1]:
        data.append({
            "moisture": r[0],
            "temperature": r[1],
            "humidity": r[2],
            "ldr": r[3],
            "time": r[4]
        })

    return jsonify(data)


# 🌐 DASHBOARD
@app.route('/')
def dashboard():
    return """<!DOCTYPE html>
<html>
<head>
<title>🌱 Smart Plant Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
    margin: 0;
    font-family: Arial;
    background: radial-gradient(circle at top, #0f172a, #020617 70%);
    color: white;
}

h1 {
    text-align: center;
    margin: 20px;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 20px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
}

.card {
    background: rgba(30,41,59,0.6);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
}

.value {
    font-size: 26px;
    font-weight: bold;
    margin-top: 10px;
}

.chart {
    margin-top: 25px;
    background: rgba(30,41,59,0.6);
    padding: 20px;
    border-radius: 16px;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
}

canvas {
    width: 100% !important;
    height: 300px !important;
}

@media(max-width:900px){
    .grid { grid-template-columns: 1fr; }
    .chart { grid-template-columns: 1fr; }
}
</style>
</head>

<body>

<h1>🌱 AgroSense: Intelligent Soil Monitoring Platform</h1>

<div class="container">

<div class="grid">
<div class="card"><div>Moisture</div><div id="m" class="value">--</div></div>
<div class="card"><div>Status</div><div id="s" class="value">--</div></div>
<div class="card"><div>Temp</div><div id="t" class="value">--</div></div>
<div class="card"><div>Humidity</div><div id="h" class="value">--</div></div>
<div class="card"><div>Light</div><div id="l" class="value">--</div></div>
</div>

<div class="card" style="margin-top:15px;">
Last Update: <span id="time">--</span>
</div>

<div class="card" style="margin-top:15px;">
<div style="opacity:0.7;">Plant Status</div>
<div id="plant" class="value">--</div>
</div>

<div class="chart">
    <canvas id="lineChart"></canvas>
    <canvas id="pieChart"></canvas>
</div>

</div>

<script>

function getPlantStatus(d){
    if(d.moisture > 3500) return "🚨 NEED WATER NOW 🌵";
    if(d.temperature > 35) return "🔥 TOO HOT";
    if(d.humidity < 30) return "💧 AIR TOO DRY";
    if(d.ldr < 1000) return "🌑 LOW LIGHT";
    return "🌿 HEALTHY PLANT";
}

async function updateData(){
    const res = await fetch('/latest');
    const d = await res.json();

    document.getElementById("m").innerText = d.moisture ?? "--";
    document.getElementById("s").innerText = d.status ?? "--";
    document.getElementById("t").innerText = (d.temperature ?? "--") + "°C";
    document.getElementById("h").innerText = (d.humidity ?? "--") + "%";
    document.getElementById("l").innerText = d.ldr ?? "--";
    document.getElementById("time").innerText = d.time ?? "--";

    document.getElementById("plant").innerText = getPlantStatus(d);

    if(d.status=="DRY") document.getElementById("s").style.color="red";
    else if(d.status=="WET") document.getElementById("s").style.color="lime";
    else document.getElementById("s").style.color="yellow";

    pieChart.data.datasets[0].data = [
        d.moisture || 0,
        d.temperature || 0,
        d.humidity || 0,
        d.ldr || 0
    ];
    pieChart.update();
}

const ctx = document.getElementById('lineChart').getContext('2d');

const lineChart = new Chart(ctx,{
    type:'line',
    data:{
        labels:[],
        datasets:[
            {label:'Moisture',data:[],borderColor:'#38bdf8'},
            {label:'Temp',data:[],borderColor:'#f97316'},
            {label:'Humidity',data:[],borderColor:'#22c55e'},
            {label:'Light',data:[],borderColor:'#eab308'}
        ]
    }
});

const pieCtx = document.getElementById('pieChart').getContext('2d');

const pieChart = new Chart(pieCtx,{
    type:'doughnut',
    data:{
        labels:['Moisture','Temp','Humidity','Light'],
        datasets:[{
            data:[0,0,0,0],
            backgroundColor:['#38bdf8','#f97316','#22c55e','#eab308']
        }]
    }
});

async function updateChart(){
    const res = await fetch('/history');
    const data = await res.json();

    lineChart.data.labels = data.map(x => x.time);

    lineChart.data.datasets[0].data = data.map(x => x.moisture);
    lineChart.data.datasets[1].data = data.map(x => x.temperature);
    lineChart.data.datasets[2].data = data.map(x => x.humidity);
    lineChart.data.datasets[3].data = data.map(x => x.ldr);

    lineChart.update();
}

setInterval(function(){
    updateData();
    updateChart();
}, 2000);

window.onload = function(){
    updateData();
    updateChart();
};

</script>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
