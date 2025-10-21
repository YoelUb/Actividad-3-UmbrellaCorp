document.addEventListener("DOMContentLoaded", () => {

    const alertBox = document.getElementById('alert-box');
    const systemStatus = document.getElementById('system-status');
    const noAlertsMsg = document.querySelector('.no-alerts');

    /**
     * @param {string} title Título del error
     * @param {string} message Mensaje del error
     */
    function showErrorAlert(title, message) {
        if (noAlertsMsg && noAlertsMsg.style.display !== 'none') {
            noAlertsMsg.style.display = 'none';
        }
        const alertElement = document.createElement('div');
        alertElement.className = 'alert-item alert-error';
        alertElement.innerHTML = `
            <strong>${title.toUpperCase()}</strong>
            <p>${message}</p>
        `;
        alertBox.prepend(alertElement);
    }

    const ctx = document.getElementById('latencyChart').getContext('2d');
    const latencyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Latencia Media (ms)',
                data: [],
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { /* ... */ }
        }
    });

    // --- 2. CONEXIÓN AL WEBSOCKET DE ALERTAS ---
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
            const alerta = JSON.parse(event.data);
            if (noAlertsMsg && noAlertsMsg.style.display !== 'none') {
                noAlertsMsg.style.display = 'none';
            }
            const alertElement = document.createElement('div');
            alertElement.className = `alert-item alert-${alerta.level}`;
            alertElement.innerHTML = `
                <strong>${alerta.title.toUpperCase()}</strong>
                <p>${alerta.message}</p>
            `;
            alertBox.prepend(alertElement);
        };

        ws.onclose = () => {
            console.log("WebSocket desconectado. Intentando reconectar...");
            systemStatus.textContent = "OFFLINE";
            systemStatus.className = "status-error";
            showErrorAlert("CONEXIÓN PERDIDA", "Se perdió la conexión WebSocket. Intentando reconectar...");
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error("Error de WebSocket:", error);
            systemStatus.textContent = "ERROR";
            systemStatus.className = "status-error";
            showErrorAlert("ERROR DE WEBSOCKET", "No se pudo establecer la conexión de alertas en tiempo real.");
            ws.close();
        };
    }

    connectWebSocket();



    async function updateLatencyChart() {
        try {
            const response = await fetch('/api/metrics/latency');
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            const chart = latencyChart.data;
            chart.labels.push(data.time);
            chart.datasets[0].data.push(data.latency);
            if (chart.labels.length > 20) {
                chart.labels.shift();
                chart.datasets[0].data.shift();
            }
            latencyChart.update();

        } catch (error) {
            console.error("Error actualizando gráfico:", error);
            if (systemStatus.textContent !== "ERROR_METRICS") {
                systemStatus.textContent = "ERROR_METRICS";
                showErrorAlert("ERROR DE API", "No se pudieron cargar las métricas de latencia.");
            }
        }
    }

    async function updateEventsTable() {
        try {
            const response = await fetch('/api/events/recent');
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const events = await response.json();
            const tableBody = document.getElementById('events-table-body');

            if (events.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="no-data">No hay eventos recientes.</td></tr>';
                return;
            }
            tableBody.innerHTML = '';
            events.reverse().forEach(event => {
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
            if (systemStatus.textContent !== "ERROR_EVENTS") {
                systemStatus.textContent = "ERROR_EVENTS";
                showErrorAlert("ERROR DE API", "No se pudieron cargar los eventos recientes.");
            }
        }
    }

    setInterval(updateLatencyChart, 2000);
    setInterval(updateEventsTable, 2000);
    updateLatencyChart();
    updateEventsTable();


    const ingestForm = document.getElementById('ingest-form');
    const batchButton = document.getElementById('batch-ingest-button');

    ingestForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        console.log("Iniciando envío de lote concurrente...");
        batchButton.disabled = true;
        batchButton.textContent = "Procesando...";

        const datos = [
            {
                id: document.getElementById('id-genetico').value,
                tipo: 'genetico',
                payload: document.getElementById('payload-genetico').value
            },
            {
                id: document.getElementById('id-bioquimico').value,
                tipo: 'bioquimico',
                payload: document.getElementById('payload-bioquimico').value
            },
            {
                id: document.getElementById('id-fisico').value,
                tipo: 'fisico',
                payload: document.getElementById('payload-fisico').value
            }
        ];

        const promesasDeEnvio = datos.map(dato => {
            return fetch('/api/ingest/manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dato)
            });
        });

        try {
            const responses = await Promise.all(promesasDeEnvio);

            let allOk = true;
            for (const res of responses) {
                if (!res.ok) {
                    allOk = false;
                    const errorData = await res.json().catch(() => ({}));
                    console.error(`Fallo en el lote: ${res.status}`, errorData);
                    showErrorAlert(
                        `FALLO EN LOTE (${res.status})`,
                        `No se pudo procesar la petición. ${errorData.message || ''}`
                    );
                }
            }

            if (allOk) {
                console.log("Lote procesado exitosamente por el backend.");
            }

        } catch (error) {
            console.error("Error al enviar el lote concurrente:", error);
            showErrorAlert("ERROR DE RED", "No se pudo enviar el lote de ingesta. Revisa la conexión.");
        } finally {
            batchButton.disabled = false;
            batchButton.textContent = "Procesar Lote Concurrente";
        }
    });

});