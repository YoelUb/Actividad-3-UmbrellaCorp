# Umbrella Corporation - Panel de Análisis Concurrente

Este proyecto es una aplicación web FastAPI diseñada para demostrar el procesamiento concurrente de datos, la monitorización en tiempo real y un sistema de alertas. La aplicación simula la ingesta y análisis de tres tipos diferentes de datos biológicos: genéticos (CPU-bound), bioquímicos (I/O-bound) y físicos (I/O-bound).

El panel de control frontend permite a los usuarios enviar lotes de estos tres tipos de datos simultáneamente, observar las alertas de procesamiento en tiempo real a través de WebSockets y monitorizar la latencia del sistema en un gráfico.

## 🚀 Características Principales

* **API REST (FastAPI):** Un backend robusto construido con FastAPI que proporciona endpoints para la ingesta de datos, métricas y eventos.
* **Procesamiento Concurrente:**
    * **CPU-bound:** Los datos "genéticos" se procesan en un `ThreadPoolExecutor` (`loop.run_in_executor`) para no bloquear el bucle de eventos de asyncio.
    * **I/O-bound:** Los datos "bioquímicos" y "físicos" se procesan de forma asíncrona (`async/await`) simulando llamadas a APIs externas o lecturas de sensores.
* **Dashboard en Tiempo Real:** Una interfaz de usuario en HTML, CSS y JavaScript vainilla que incluye:
    * Un formulario para la ingesta concurrente de datos.
    * Un panel de alertas que se actualiza instantáneamente a través de **WebSockets**.
    * Un gráfico de latencia (usando Chart.js) que sondea el endpoint `/api/metrics/latency`.
    * Una tabla de eventos recientes que sondea el endpoint `/api/events/recent`.
* **Alertas Críticas por Email:**
    * Si un evento se considera "crítico" (como los genéticos) o resulta en un "error", el sistema genera un informe completo.
    * El informe incluye detalles de la alerta, métricas de latencia recientes y los últimos 5 eventos del sistema consultados desde la base de datos.
    * Este informe se envía como un archivo `.txt` adjunto por correo electrónico (usando `smtplib` y Gmail) al destinatario especificado en la ingesta.
* **Persistencia de Datos:**
    * Todos los eventos procesados se guardan en una base de datos **PostgreSQL**.
    * La interacción con la base de datos es asíncrona, utilizando **SQLAlchemy** y **SQLModel**.
* **Monitorización de Métricas:** Un monitor de métricas singleton (`MetricsMonitor`) rastrea la latencia de procesamiento para cada tipo de dato usando colecciones `deque`.

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.12, FastAPI, Uvicorn
* **Base de Datos:** PostgreSQL, SQLAlchemy (Async), SQLModel
* **Comunicaciones:** WebSockets, SMTPLib (para emails)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Chart.js
* **Contenerización:** Docker, Docker Compose (para la base de datos)
* **Testing:** Pytest, HTTPX (AsyncClient)

## Arquitectura

1.  **Diagrama de Clases**



![class_diagram.png](docs/architecture/class_diagram.png)



2. **Diagrama de Objetos**



![object_diagram.png](docs/architecture/object_diagram.png)



3. **Diagrama de Secuencia**



![sequence_diagram.png](docs/architecture/sequence_diagram.png)





## ⚙️ Instalación y Ejecución

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/YoelUb/Actividad-3-UmbrellaCorp.git
    cd Actividad-3-UmbrellaCorp
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # En Windows: .\.venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    *(Nota: Se asume que existe un `requirements.txt`. Si no, instálalas manualmente: `pip install fastapi uvicorn[standard] sqlmodel sqlalchemy[asyncpg] python-dotenv chart.js httpx pytest pytest-asyncio`)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Iniciar la Base de Datos (Docker):**
    Asegúrate de tener Docker Desktop en ejecución.
    ```bash
    docker-compose up -d
    ```
    Esto iniciará un contenedor de PostgreSQL basado en la configuración de `docker-compose.yml`.

5.  **Configurar Variables de Entorno:**
    Copia el archivo de ejemplo y rellena los valores. El archivo debe estar en `src/.env`.
    ```bash
    cp env.example src/.env
    ```
    Edita `src/.env` con tus credenciales:
    ```ini
    # Asegúrate de que esto coincida con tu docker-compose.yml
    DB_USER=umbrella_user
    DB_PASSWORD=secret_password_aqui
    DB_NAME=umbrella_db
    DB_HOST=localhost
    DB_PORT=5432
    DATABASE_URL=postgresql+asyncpg://umbrella_user:secret_password_aqui@localhost:5432/umbrella_db
    
    # Configuración de Email (requiere una "Contraseña de Aplicación" de Google)
    EMAIL_SENDER=tu-email@gmail.com
    EMAIL_APP_PASSWORD=tu-clave-de-aplicacion-de-google
    ```

6.  **Ejecutar la Aplicación:**
    ```bash
    cd src
    uvicorn main:app --reload
    ```

7.  **Acceder al Panel:**
    Abre tu navegador y ve a `http://127.0.0.1:8000`.

## 🧪 Ejecutar Pruebas

El conjunto de pruebas está configurado para usar una base de datos SQLite en memoria, por lo que no afectará a tu base de datos de desarrollo.

```bash
pytest
```

## Contacto

Escribir un correo a "yurqubar@myuax.com" o "yoelurquijo13@gmail.com"
