# 🐱 Finanzas Gatunas

Sistema de gestión financiera del hogar con temática gatuna. Controla tus ingresos, gastos y ahorros de manera divertida y organizada.

![Finanzas Gatunas](https://img.shields.io/badge/Finanzas-Gatunas-FF69B4?style=for-the-badge&logo=cat)

## ✨ Características Principales

### 🏠 Dashboard Interactivo

- Resumen financiero mensual en tiempo real
- Gráficos de tendencias y distribución de gastos
- Indicadores visuales del estado financiero
- Consejos financieros gatunos personalizados

### 💰 Gestión de Transacciones

- Registro de ingresos y gastos
- Categorización automática con iconos y colores
- Filtros por fecha, tipo y categoría
- Historial completo de movimientos

### 📂 Categorías Personalizables

- Creación de categorías con iconos emoji
- Paleta de colores personalizable
- Categorías predeterminadas para comenzar rápido
- Organización visual de gastos

### 🔄 Pagos Recurrentes

- Gestión de suscripciones y membresías
- Configuración de frecuencias (diario, semanal, mensual, anual)
- Recordatorios de próximos pagos
- Control de pagos activos/inactivos

### 📊 Reportes Avanzados

- Análisis mensual y anual
- Gráficos de tendencias financieras
- Comparación de ingresos vs gastos
- Insights y recomendaciones automáticas

## 🎨 Diseño y Temática

- **Colores**: Paleta rosa gatuna (#FF69B4, #FFB6C1, #DDA0DD)
- **Tipografía**: Comic Sans MS para un toque divertido
- **Iconos**: Emojis de gatos y temática financiera
- **Animaciones**: Transiciones suaves y efectos hover
- **Responsivo**: Adaptado para móviles y escritorio

## 🛠️ Tecnologías Utilizadas

### Frontend

- **React 18** - Interfaz de usuario moderna
- **React Router** - Navegación entre páginas
- **Recharts** - Gráficos interactivos
- **Date-fns** - Manejo de fechas
- **CSS Custom Properties** - Tema personalizado

### Backend

- **Flask** - API REST
- **SQLAlchemy** - ORM para base de datos
- **Flask-CORS** - Manejo de CORS
- **Python** - Lógica del servidor

### Base de Datos

- **PostgreSQL/SQLite** - Almacenamiento de datos
- **Migraciones Alembic** - Control de versiones de BD

## 🚀 Instalación y Configuración

### Prerrequisitos

- Node.js 20+
- Python 3.8+
- pip y npm

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd finanzasGatunas-1
```

### 2. Configurar el Backend

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Inicializar base de datos
flask db upgrade

# Crear datos de ejemplo
flask insert-test-data
```

### 3. Configurar el Frontend

```bash
# Instalar dependencias Node.js
npm install

# Configurar variables de entorno
# Crear archivo .env con VITE_BACKEND_URL=http://localhost:3001
```

### 4. Ejecutar la aplicación

```bash
# Terminal 1: Backend
npm run start

# Terminal 2: Frontend
npm run dev
```

## 📱 Uso de la Aplicación

### Primeros Pasos

1. **Dashboard**: Ve el resumen de tus finanzas actuales
2. **Categorías**: Crea categorías personalizadas para organizar gastos
3. **Transacciones**: Registra ingresos y gastos diarios
4. **Pagos Recurrentes**: Configura suscripciones y membresías
5. **Reportes**: Analiza tendencias y toma decisiones informadas

### Datos de Ejemplo

La aplicación incluye datos de ejemplo para probar todas las funcionalidades:

- **Email**: demo@finanzasgatunas.com
- **Password**: 123456

### Consejos Gatunos 🐱

- Mantén un presupuesto como un gato organizado
- Ahorra consistentemente como si fuera tu comida favorita
- Revisa tus gastos regularmente
- ¡Disfruta del proceso financiero!

## 🎯 Funcionalidades Destacadas

### 📈 Gráficos Interactivos

- **Gráfico de Torta**: Distribución de gastos por categoría
- **Gráfico de Líneas**: Tendencia mensual de ingresos/gastos
- **Gráfico de Barras**: Comparación de ahorros mensuales
- **Gráfico de Área**: Evolución financiera anual

### 💡 Insights Automáticos

- Cálculo automático de tasa de ahorro
- Identificación de mejores/peores meses
- Recomendaciones personalizadas
- Alertas de gastos elevados

### 🎨 Personalización

- Colores personalizables por categoría
- Iconos emoji para identificación visual
- Temas responsivos
- Animaciones gatunos

## 🔧 Comandos Útiles

```bash
# Desarrollo
npm run dev          # Ejecutar en modo desarrollo
npm run build        # Construir para producción
npm run preview      # Vista previa de producción

# Base de datos
flask db migrate     # Crear nueva migración
flask db upgrade     # Aplicar migraciones
flask insert-test-data  # Crear datos de ejemplo

# Linting y formato
npm run lint         # Verificar código
```

## 📁 Estructura del Proyecto

```
finanzasGatunas-1/
├── src/
│   ├── api/                 # Backend Flask
│   │   ├── models.py        # Modelos de base de datos
│   │   ├── routes.py        # Rutas de API
│   │   ├── commands.py      # Comandos CLI
│   │   └── utils.py         # Utilidades
│   └── front/               # Frontend React
│       ├── components/      # Componentes reutilizables
│       ├── pages/           # Páginas principales
│       ├── hooks/           # Hooks personalizados
│       ├── assets/          # Recursos estáticos
│       └── index.css        # Estilos globales
├── migrations/              # Migraciones de BD
├── public/                  # Archivos públicos
└── package.json            # Dependencias y scripts
```

## 🌟 Próximas Funcionalidades

- [ ] Exportación de reportes PDF
- [ ] Notificaciones push para pagos
- [ ] Integración con bancos
- [ ] Modo oscuro
- [ ] Múltiples usuarios
- [ ] Presupuestos por categoría
- [ ] Metas de ahorro

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🐱 Créditos

Hecho con 💖 y mucho ☕ por desarrolladores que aman a los gatos.

---

**¡Miau! 🐱** ¿Tienes preguntas? ¡Abre un issue y te ayudaremos como buenos gatos domésticos!
