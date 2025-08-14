# 🚀 Despliegue en Railway - Finanzas Gatunas

## 📋 Requisitos Previos

- Cuenta en [Railway](https://railway.app/)
- Proyecto conectado a GitHub
- Base de datos PostgreSQL (proporcionada por Railway)

## 🔧 Configuración del Proyecto

### 1. Variables de Entorno en Railway

Configura las siguientes variables de entorno en tu proyecto de Railway:

```bash
# Base de datos (Railway la proporciona automáticamente)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Clave secreta para Flask
SECRET_KEY=tu-clave-secreta-super-segura-aqui

# URL del backend para el frontend
VITE_BACKEND_URL=/api

# Configuración de CORS
CORS_ORIGINS=*

# Entorno de producción
FLASK_ENV=production
FLASK_DEBUG=false
```

### 2. Configuración de Build

El proyecto ya está configurado para Railway con:
- `railway.json` - Configuración de Railway
- `railway_build.sh` - Script de build
- `railway_app.py` - Aplicación principal para Railway

## 🚀 Proceso de Despliegue

### 1. Conectar a GitHub

1. Ve a [Railway Dashboard](https://railway.app/dashboard)
2. Crea un nuevo proyecto
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio de Finanzas Gatunas

### 2. Configurar Variables de Entorno

1. En tu proyecto de Railway, ve a la pestaña "Variables"
2. Agrega las variables de entorno mencionadas arriba
3. **IMPORTANTE**: Railway proporciona `DATABASE_URL` automáticamente

### 3. Configurar Base de Datos

1. En Railway, ve a la pestaña "Data"
2. Crea una nueva base de datos PostgreSQL
3. Railway configurará automáticamente `DATABASE_URL`

### 4. Desplegar

1. Railway detectará automáticamente la configuración
2. El build se ejecutará usando `railway_build.sh`
3. La aplicación se iniciará con `railway_app.py`

## 🔍 Verificación del Despliegue

### 1. Health Check

Visita: `https://tu-app.railway.app/health`

Deberías ver:
```json
{
  "status": "healthy",
  "message": "Finanzas Gatunas está funcionando correctamente en Railway! 🐱",
  "environment": "Railway",
  "database": "PostgreSQL"
}
```

### 2. Frontend

- Visita la URL principal de tu aplicación
- Deberías ver la interfaz de Finanzas Gatunas
- No debería aparecer una página en blanco

### 3. API

- Visita: `https://tu-app.railway.app/api/hello`
- Deberías ver el mensaje de bienvenida

## 🐛 Solución de Problemas

### Página en Blanco

Si la página se ve en blanco:

1. **Verifica los logs de Railway**:
   - Ve a la pestaña "Deployments"
   - Revisa los logs del último despliegue

2. **Verifica que el build se completó**:
   - Los logs deben mostrar "✅ Build completado exitosamente!"
   - Debe existir el directorio `dist/`

3. **Verifica las variables de entorno**:
   - `DATABASE_URL` debe estar configurada
   - `VITE_BACKEND_URL` debe ser `/api`

### Error de Base de Datos

Si hay errores de base de datos:

1. **Verifica que PostgreSQL esté funcionando**:
   - Ve a la pestaña "Data" en Railway
   - La base de datos debe estar "Running"

2. **Verifica la conexión**:
   - Los logs deben mostrar "✅ Tablas de la base de datos creadas exitosamente!"

### Error de Build

Si el build falla:

1. **Verifica Node.js**:
   - Railway debe usar Node.js 20+
   - Verifica en `package.json`

2. **Verifica las dependencias**:
   - Los logs deben mostrar "📦 Instalando dependencias..."
   - No debe haber errores de npm install

## 📱 Configuración del Frontend

El frontend está configurado para:
- Usar rutas relativas (`/api` para el backend)
- Servir archivos estáticos desde `dist/`
- Manejar rutas del SPA correctamente

## 🔄 Actualizaciones

Para actualizar la aplicación:

1. Haz push a tu rama principal en GitHub
2. Railway detectará automáticamente los cambios
3. Ejecutará un nuevo build y despliegue

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs de Railway
2. Verifica las variables de entorno
3. Asegúrate de que la base de datos esté funcionando
4. Verifica que el build se complete exitosamente

---

**¡Con esta configuración, Finanzas Gatunas debería funcionar perfectamente en Railway! 🐱💰**

