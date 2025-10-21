// Espera a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {

    // --- 1. CONFIGURACIÓN DEL GRÁFICO (Chart.js) ---
    const ctx = document.getElementById('latencyChart').getContext('2d');
    const latencyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Se llenará dinámicamente
            datasets: [{
                label: 'Latencia Media (ms)',
                data: [], // Se llenará dinámicamente
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3 // Líneas curvas
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Tiempo' }
                },
                y: {
                    title: { display: true, text: 'Latencia (ms)' },
                    beginAtZero: true
                }
            },
            animation: {
                duration: 400
            }
        }
    });

    // --- 2. CONEXIÓN AL WEBSOCKET DE ALERTAS ---
    const alertBox = document.getElementById('alert-box');
    const systemStatus = document.getElementById('system-status');
    const noAlertsMsg = document.querySelector('.no-alerts');

    // Cambia la URL si tu endpoint de WebSocket es diferente
    const wsUrl = `ws://${window.location.host}/ws/alerts`;

    function connectWebSocket() {
        console.log("Intentando conectar al WebSocket en " + wsUrl);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("Conectado al WebSocket de alertas");
            systemStatus.textContent = "ONLINE";
            systemStatus.className = "status-ok";
        };

        ws.onmessage = (event) => {
            // Asumimos que la alerta es un JSON: { "level": "critical", "title": "...", "message": "..." }
            const alerta = JSON.parse(event.data);

            // Quitar el mensaje "sin alertas"
            if (noAlertsMsg) {
                noAlertsMsg.style.display = 'none';
            }

            // Crear el elemento de alerta
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item alert-${alerta.level}`; // ej: alert-critical
            alertElement.innerHTML = `
                <strong>${alerta.title.toUpperCase()}</strong>
                <p>${alerta.message}</p>
            `;

            // Añadir al principio del contenedor
            alertBox.prepend(alertElement);
        };

        ws.onclose = () => {
            console.log("WebSocket desconectado. Intentando reconectar...");
            systemStatus.textContent = "OFFLINE";
            systemStatus.className = "status-error";
            // Intenta reconectar después de 3 segundos
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error("Error de WebSocket:", error);
            systemStatus.textContent = "ERROR";
            systemStatus.className = "status-error";
            ws.close();
        };
    }

    // Iniciar la conexión WebSocket
    connectWebSocket();


    // --- 3. ACTUALIZACIÓN DE MÉTRICAS Y TABLAS (Polling) ---

    // Función para actualizar el gráfico de latencia
    async function updateLatencyChart() {
        try {
            // Cambia la URL si tu endpoint de API es diferente
            const response = await fetch('/api/metrics/latency');
            if (!response.ok) return;

            const data = await response.json(); // Asume: { "time": "14:30:05", "latency": 120 }

            const chart = latencyChart.data;
            chart.labels.push(data.time);
            chart.datasets[0].data.push(data.latency);

            // Limitar el gráfico a los últimos 20 puntos
            if (chart.labels.length > 20) {
                chart.labels.shift();
                chart.datasets[0].data.shift();
            }

            latencyChart.update();

        } catch (error) {
            console.error("Error actualizando gráfico:", error);
        }
    }

    // Función para actualizar la tabla de eventos
    async function updateEventsTable() {
        try {
            // Cambia la URL si tu endpoint de API es diferente
            const response = await fetch('/api/events/recent');
            if (!response.ok) return;

            const events = await response.json(); // Asume: [ { "id": "...", "type": "...", "worker": "...", "status": "..." } ]
            const tableBody = document.getElementById('events-table-body');

            if (events.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="no-data">No hay eventos recientes.</td></tr>';
                return;
            }

            // Limpiar tabla
            tableBody.innerHTML = '';

            // Poblar tabla
            events.forEach(event => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${event.id}</td>
                    <td>${event.type}</td>
                    <td>${event.worker}</td>
                    <td>${event.status}</td>
                `;
                tableBody.appendChild(row);
            });

        } catch (error) {
            console.error("Error actualizando tabla de eventos:", error);
        }
    }

    // Iniciar el polling para métricas y eventos
    // Actualiza el gráfico cada 2 segundos
    setInterval(updateLatencyChart, 2000);

    // Actualiza la tabla cada 5 segundos
    setInterval(updateEventsTable, 5000);

    // Cargar los datos iniciales al cargar la página
    updateLatencyChart();
    updateEventsTable();

});