# Tweet Extractor Microservice

Un microservicio en Python para extraer datos de tweets usando Selenium con Chrome Headless. Optimizado para despliegue en Railway.

## Características

- Extrae información de tweets a partir de URLs usando Selenium
- Navegación automatizada con Chrome Headless
- Manejo robusto de errores y timeouts
- Optimizado para entornos de producción
- Reintentos automáticos con backoff exponencial

## Datos extraídos

- Autor del tweet
- Texto del tweet
- Métricas (likes, retweets, respuestas, vistas)
- Imágenes
- Fecha de publicación

## Estructura del proyecto

- `tweet_extractor.py`: Módulo principal de extracción con Selenium
- `railway_app.py`: Aplicación Flask para Railway
- `Procfile`: Configuración para despliegue
- `railway.json`: Configuración específica de Railway
- `render.yaml`: Configuración para Render (frontend)
- `requirements.txt`: Dependencias del proyecto
- `test_selenium_extractor.py`: Script para probar la extracción

## Endpoints API

### POST /extract

Extrae datos de un solo tweet.

**Payload:**
```json
{
  "url": "https://x.com/usuario/status/123456789"
}
```

### POST /extract-batch

Extrae datos de múltiples tweets.

**Payload:**
```json
{
  "urls": [
    "https://x.com/usuario1/status/123456789",
    "https://x.com/usuario2/status/987654321"
  ]
}
```

### GET /health

Endpoint para verificar el estado del servicio.

## Despliegue

### Railway

1. Crea un nuevo proyecto en Railway
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente la configuración en `railway.json` y `Procfile`
4. El servicio se desplegará automáticamente con Chrome instalado

### Docker

También puedes desplegar el servicio usando Docker:

1. Construye la imagen: `docker build -t tweet-extractor .`
2. Ejecuta el contenedor: `docker run -p 8080:8080 tweet-extractor`

O usando Docker Compose:

```bash
docker-compose up
```

### Render (Frontend)

1. Crea un nuevo servicio web en Render
2. Conecta tu repositorio de GitHub
3. Render detectará automáticamente la configuración en `render.yaml`
4. Configura la variable de entorno `TWEET_EXTRACTOR_URL` con la URL de tu servicio en Railway

## Desarrollo local

### Método 1: Script de ayuda

El proyecto incluye un script de ayuda para facilitar la ejecución:

1. Clona el repositorio
2. Haz el script ejecutable: `chmod +x run.sh`
3. Instala las dependencias: `./run.sh install`
4. Ejecuta el servidor: `./run.sh server`
5. Para probar la extracción: `./run.sh test`
6. Para ejecutar con Docker: `./run.sh docker` o `./run.sh docker-compose`

### Método 2: Python directo

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Asegúrate de tener Chrome instalado en tu sistema
4. Ejecuta el servidor: `python railway_app.py`
5. El servidor estará disponible en `http://localhost:8080`
6. Para probar la extracción: `python test_selenium_extractor.py`

### Método 3: Docker

1. Clona el repositorio
2. Ejecuta con Docker Compose: `docker-compose up`
3. El servidor estará disponible en `http://localhost:8080`

## Notas técnicas

- El servicio utiliza Selenium con Chrome Headless para extraer datos de tweets
- Implementa reintentos con backoff exponencial para manejar errores temporales
- Optimizado para minimizar el uso de recursos en contenedores
- Maneja automáticamente diálogos y popups que puedan aparecer
- Utiliza selectores CSS robustos para adaptarse a cambios en la interfaz de X.com

## Requisitos

- Python 3.9+
- Chrome (instalado automáticamente en Railway)
- Dependencias listadas en requirements.txt:
  - flask
  - gunicorn
  - requests
  - beautifulsoup4
  - selenium
  - webdriver-manager
