# 🍽️ Alimenta Forma

**Alimenta Forma** es una aplicación web moderna que combina un backend robusto en **Django** con un frontend rápido y elegante construido en **React** + **Vite**.  
Ideal para gestionar cursos, membresías y perfiles de usuario de manera eficiente y atractiva.

---

## 🚀 Tecnologías Utilizadas

| Backend                  | Frontend                      | Herramientas Adicionales       |
|--------------------------|-------------------------------|-------------------------------|
| 🐍 Python 3.x            | ⚛️ React 18+                   | 🛠️ ESLint (calidad de código)  |
| 🕸️ Django 4.x             | ⚡ Vite (bundler + servidor)  | 🎨 CSS Modules (estilos scoped) |
| 🧩 Django REST Framework | React Router (gestión rutas)  | 📦 npm (gestión frontend)       |

---

## 🗂️ Estructura del Proyecto

```plaintext
/
├── api/                       # Backend Django
│   └── apialimentaforma/
│       ├── api/               # App Django (modelos, vistas, migraciones...)
│       ├── apialimentaforma/  # Configuración general (settings, urls, wsgi)
│       └── manage.py          # Script de gestión Django
├── src/                       # Frontend React
│   ├── components/            # Componentes reutilizables (botones, tarjetas, formularios)
│   ├── routes/                # Páginas principales (Home, Login, Courses, etc.)
│   ├── assets/                # Imágenes y recursos estáticos
│   ├── App.jsx                # Componente raíz React
│   ├── main.jsx               # Punto de entrada React + Vite
│   └── estilos CSS y módulos  # CSS global y módulos CSS
├── index.html                 # Entrada HTML para Vite
├── package.json               # Dependencias frontend
├── requirements.txt           # Dependencias backend
├── vite.config.js             # Configuración de Vite
├── .eslintrc.cjs             # Configuración ESLint
└── .gitignore                 # Archivos ignorados por Git
```

## ⚙️ Configuración por entorno

El backend lee primero las variables exportadas por el proceso y, si existe, el
archivo `.env` de la raíz. Este archivo está ignorado por Git: copia la plantilla
sin secretos y adapta sus valores para trabajar localmente.

```bash
cp .env.example .env
```

Los valores definidos en el sistema tienen prioridad sobre `.env`. Las listas se
escriben separadas por comas, los booleanos aceptan `true/false`, `1/0`,
`yes/no` u `on/off`, y las opciones avanzadas usan objetos JSON.

| Variable | Obligatoria / valor predeterminado | Descripción |
|---|---|---|
| `APP_ENV` | `development` | Entorno validado: `development`, `test` o `production`. |
| `SECRET_KEY` | Obligatoria en producción | Secreto criptográfico de Django; en producción debe tener al menos 50 caracteres. |
| `DEBUG` | Activo salvo en producción | Modo de depuración; se rechaza explícitamente si está activo en producción. |
| `ALLOWED_HOSTS` | Obligatoria en producción | Hosts HTTP permitidos, separados por comas. |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Backend Django de base de datos (por ejemplo, `django.db.backends.postgresql`). |
| `DB_NAME` | SQLite local; obligatoria en producción | Nombre o ruta de la base de datos. |
| `DB_USER` | Vacía | Usuario de base de datos. |
| `DB_PASSWORD` | Obligatoria en producción no SQLite | Contraseña de base de datos. |
| `DB_HOST` / `DB_PORT` | Vacías | Servidor y puerto de base de datos. |
| `DB_CONN_MAX_AGE` | `0` | Segundos de persistencia de conexiones. |
| `DB_OPTIONS` | `{}` | Opciones del backend de base de datos como objeto JSON. |
| `CORS_ALLOWED_ORIGINS` | Vacía | Orígenes completos autorizados para CORS, separados por comas. |
| `CORS_ALLOW_CREDENTIALS` | `true` | Permite enviar la cookie de sesión en peticiones CORS. |
| `CSRF_TRUSTED_ORIGINS` | Vacía | Orígenes completos de confianza para CSRF, separados por comas. |
| `MEDIA_URL` / `MEDIA_ROOT` | `/media/` / directorio `media` | URL pública y ruta de archivos subidos. |
| `STATIC_URL` / `STATIC_ROOT` | `/static/` / directorio `staticfiles` | URL pública y ruta de archivos estáticos recopilados. |
| `STORAGE_BACKEND` | `FileSystemStorage` | Clase de almacenamiento para archivos subidos. |
| `STORAGE_OPTIONS` | `{}` | Opciones del almacenamiento principal como objeto JSON; los secretos deben residir solo en el entorno. |
| `STATIC_STORAGE_BACKEND` | `StaticFilesStorage` | Clase de almacenamiento para estáticos. |
| `STATIC_STORAGE_OPTIONS` | `{}` | Opciones JSON del almacenamiento de estáticos. |
| `SECURE_HSTS_SECONDS` | `31536000` | Duración de HSTS, aplicada únicamente en producción. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `true` | Incluye subdominios en HSTS en producción. |
| `SECURE_HSTS_PRELOAD` | `true` | Activa la directiva de precarga HSTS en producción. |
| `TRUST_X_FORWARDED_PROTO` | `false` | Confía en `X-Forwarded-Proto: https` solo en producción; activar únicamente tras un proxy que reescriba la cabecera. |

En producción también se activan automáticamente cookies `Secure` para sesión y
CSRF y la redirección a HTTPS. El arranque falla de forma explícita si falta
`SECRET_KEY`, si es demasiado corta, si faltan hosts o base de datos, si una base
no SQLite carece de contraseña o si `DEBUG` está activo. Antes de habilitar HSTS
o la cabecera de proxy, confirma que todo el dominio sirve HTTPS y que el proxy
elimina cualquier cabecera aportada por el cliente.

## 🧪 Ejecución de pruebas

### Frontend

Instala las dependencias y ejecuta la suite de Vitest con React Testing Library:

```bash
npm install
npm test
```

Los tests viven en `tests/frontend/`, usan `jsdom` como entorno DOM y cargan sus
matchers y limpieza común desde `tests/frontend/setup.js`. Para generar el informe
de cobertura en `coverage/`:

```bash
npm run test:coverage
```

### Backend Django

Instala los requisitos de Python y ejecuta el paquete de pruebas por dominio:

```bash
python -m pip install -r api/apialimentaforma/requirements.txt
python api/apialimentaforma/manage.py test api.test_suite
```

La suite se mantiene en `api/apialimentaforma/api/test_suite/` y separa los casos
de autenticación, permisos, serializadores, cursos, matrículas, asistencia, notas,
archivos y roles. La comprobación de configuración de Django se ejecuta aparte:

```bash
python api/apialimentaforma/manage.py check
```
