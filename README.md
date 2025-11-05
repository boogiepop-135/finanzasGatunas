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

### Variables de Entorno

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

### Configuración de Email (Gmail)

Para enviar emails de verificación e invitaciones, necesitas configurar Gmail:

1. **Activar verificación en 2 pasos** en tu cuenta de Google
2. **Generar una contraseña de aplicación**:
   - Ve a https://myaccount.google.com/apppasswords
   - Selecciona "Aplicación" → "Correo"
   - Selecciona "Dispositivo" → "Otro (nombre personalizado)" → escribe "Finanzas Gatunas"
   - Haz clic en "Generar"
   - Copia la contraseña de 16 caracteres generada

3. **Configurar en `.env` o `docker-compose.yml`**:
   ```
   MAIL_USERNAME=tu_email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # La contraseña de aplicación de 16 caracteres
   MAIL_DEFAULT_SENDER=tu_email@gmail.com
   ```

**Nota**: Si no configuras el email, los códigos de verificación se mostrarán en los logs del servidor (modo desarrollo).

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

