# Finanzas Gatunas 🐱

Aplicación web para gestión de finanzas personales y domésticas.

## Características

- Registro y autenticación de usuarios con verificación de email
- Gestión de transacciones (ingresos y gastos)
- Tarjetas de crédito/débito
- Membresías y suscripciones
- Presupuestos mensuales
- Recordatorios de pagos
- Compartir finanzas con otros usuarios
- Gráficos y estadísticas

## Requisitos

- Python 3.11+ o Docker
- MongoDB

## Instalación

### Opción 1: Sin Docker

```bash
pip install -r requirements.txt
```

### Opción 2: Con Docker

```bash
docker build -t finanzas-gatunas .
```

## Configuración

Crear archivo `.env` con:

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=finanzas_gatunas
SECRET_KEY=tu-secret-key-segura
PORT=3000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

## Ejecución

### Desarrollo local (sin Docker)
```bash
cd src
python app.py
```

### Producción (con gunicorn)
```bash
gunicorn --bind 0.0.0.0:3000 wsgi:application
```

### Con Docker
```bash
# Opción 1: Solo aplicación
docker run -d -p 3000:3000 --env-file .env finanzas-gatunas

# Opción 2: Con docker-compose (incluye MongoDB)
docker-compose up -d
```

Ver `DOCKER.md` para más detalles sobre Docker.

## Despliegue en VPS

1. Instalar Docker y Docker Compose
2. Clonar el repositorio
3. Configurar variables de entorno en `.env`
4. Ejecutar: `docker-compose up -d`

## Licencia

Propiedad de Levi Eduardo Villarreal Argueta

