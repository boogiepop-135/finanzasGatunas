# Configuración de Email para Finanzas Gatunas 🐱

La aplicación necesita configuración de email para enviar:
- Códigos de verificación de usuarios
- Invitaciones para compartir finanzas

## Opción 1: Gmail (Recomendado)

### Paso 1: Activar verificación en 2 pasos
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a "Seguridad" → "Verificación en 2 pasos"
3. Actívala si no está activada

### Paso 2: Generar contraseña de aplicación
1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona:
   - **Aplicación**: Correo
   - **Dispositivo**: Otro (nombre personalizado) → escribe "Finanzas Gatunas"
3. Haz clic en "Generar"
4. Copia la contraseña de 16 caracteres (sin espacios)

### Paso 3: Configurar en Docker Compose

Edita el archivo `docker-compose.yml` y agrega las variables de entorno:

```yaml
environment:
  - MAIL_SERVER=smtp.gmail.com
  - MAIL_PORT=587
  - MAIL_USE_TLS=True
  - MAIL_USERNAME=tu_email@gmail.com
  - MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # La contraseña de aplicación sin espacios
  - MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

O crea un archivo `.env` en la raíz del proyecto:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

Y en `docker-compose.yml` usa:

```yaml
env_file:
  - .env
```

### Paso 4: Reiniciar el contenedor

```bash
docker compose down
docker compose up -d
```

## Opción 2: Otros proveedores SMTP

### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@outlook.com
MAIL_PASSWORD=tu_contraseña
MAIL_DEFAULT_SENDER=tu_email@outlook.com
```

### Yahoo
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@yahoo.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@yahoo.com
```

### Servidor SMTP personalizado
```env
MAIL_SERVER=tu_servidor_smtp.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_usuario
MAIL_PASSWORD=tu_contraseña
MAIL_DEFAULT_SENDER=noreply@tu_dominio.com
```

## Verificación

Para verificar que el email está configurado correctamente:

1. Revisa los logs del contenedor:
```bash
docker logs finanzas_app
```

Deberías ver mensajes como:
```
[OK] Código de verificación enviado a usuario@ejemplo.com desde tu_email@gmail.com
```

2. Si no está configurado, verás:
```
[INFO] Email no configurado. Código de verificación para usuario@ejemplo.com: 123456
```

## Modo Desarrollo (Sin Email)

Si no configuras el email, la aplicación funcionará en modo desarrollo:
- Los códigos de verificación se mostrarán en los logs del servidor
- Los usuarios verán el código directamente en la página de verificación
- Las invitaciones no se enviarán por email (pero se pueden aceptar manualmente)

## Solución de Problemas

### Error: "Authentication failed"
- Verifica que la contraseña de aplicación sea correcta (sin espacios)
- Asegúrate de que la verificación en 2 pasos esté activada

### Error: "Connection refused"
- Verifica que el puerto 587 esté abierto
- Algunos proveedores requieren conexión desde IPs específicas

### Los emails no llegan
- Revisa la carpeta de spam
- Verifica que el email del destinatario sea correcto
- Revisa los logs del contenedor para ver errores específicos

