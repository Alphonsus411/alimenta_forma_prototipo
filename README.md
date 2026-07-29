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
