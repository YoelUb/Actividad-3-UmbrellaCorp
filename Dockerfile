#Imagen oficial de Python 3.12
FROM python:3.12-slim

# Establece el directorio en el contenedor
WORKDIR /app


COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Expone el puerto
EXPOSE 8001