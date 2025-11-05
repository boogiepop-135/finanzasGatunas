# Guía de uso con Docker

## Construcción y ejecución

### Opción 1: Solo la aplicación (MongoDB externo)

```bash
# Construir la imagen
docker build -t finanzas-gatunas .

# Ejecutar el contenedor
docker run -d \
  --name finanzas-app \
  -p 3000:3000 \
  -e MONGODB_URI=mongodb://tu-mongodb-host:27017/ \
  -e MONGODB_DB_NAME=finanzas_gatunas \
  -e SECRET_KEY=tu-secret-key-segura \
  -e MAIL_USERNAME=tu_email@gmail.com \
  -e MAIL_PASSWORD=tu_password \
  -e MAIL_DEFAULT_SENDER=tu_email@gmail.com \
  finanzas-gatunas
```

### Opción 2: Con docker-compose (incluye MongoDB)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (cuidado: borra datos)
docker-compose down -v
```

## Variables de entorno requeridas

- `MONGODB_URI`: URI de conexión a MongoDB
- `MONGODB_DB_NAME`: Nombre de la base de datos
- `SECRET_KEY`: Clave secreta para Flask (cambiar en producción)
- `PORT`: Puerto donde corre la aplicación (default: 3000)

## Variables opcionales para email

- `MAIL_SERVER`: Servidor SMTP (default: smtp.gmail.com)
- `MAIL_PORT`: Puerto SMTP (default: 587)
- `MAIL_USE_TLS`: Usar TLS (default: True)
- `MAIL_USERNAME`: Usuario del servidor SMTP
- `MAIL_PASSWORD`: Contraseña del servidor SMTP
- `MAIL_DEFAULT_SENDER`: Email del remitente

## Producción en VPS

1. Construir la imagen:
```bash
docker build -t finanzas-gatunas .
```

2. Ejecutar con variables de entorno desde archivo:
```bash
docker run -d \
  --name finanzas-app \
  --restart unless-stopped \
  -p 3000:3000 \
  --env-file .env \
  finanzas-gatunas
```

3. O usar docker-compose en producción:
```bash
docker-compose -f docker-compose.yml up -d
```

## Comandos útiles

```bash
# Ver logs
docker logs -f finanzas-app

# Entrar al contenedor
docker exec -it finanzas-app bash

# Detener contenedor
docker stop finanzas-app

# Eliminar contenedor
docker rm finanzas-app

# Reconstruir imagen
docker build -t finanzas-gatunas . --no-cache
```

