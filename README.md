# 🍽️ Alimenta Forma

Aplicación web para gestionar cursos, membresías, anuncios, matrículas, asistencia,
notas y perfiles. El frontend es una SPA de React y Vite; el backend expone una
API REST con Django y Django REST Framework (DRF).

La visión funcional, los públicos, el catálogo formativo, las modalidades y el
ciclo completo de una acción formativa se detallan en la
**[definición de producto](docs/PRODUCTO.md)**. Las capacidades pendientes y sus
criterios de verificación se mantienen en la [auditoría](docs/AUDITORIA.md).

## Tecnologías y versiones

Las versiones que fija actualmente el repositorio son:

- **Frontend:** Node.js 20 (versión usada por CI), React 18.2, React Router 6.23,
  Vite 5.2, Vitest 2.1 y ESLint 8.57.
- **Backend:** Python 3.12 (versión usada por CI), Django 5.0.6, DRF 3.15.2,
  django-cors-headers 4.4.0 y Pillow 10.3.0.
- **Desarrollo:** npm con instalación reproducible desde `package-lock.json` y
  SQLite por defecto. Las dependencias Python están fijadas en
  `api/apialimentaforma/requirements.txt`.

## Requisitos del sistema

- Git.
- Node.js 20 y npm 10 o una versión compatible con el `package-lock.json` v3.
- Python 3.12, `pip` y el módulo `venv`.
- Las bibliotecas del sistema que requiera Pillow en la plataforma utilizada.
- Para producción, una base de datos soportada por Django y un servidor/proxy
  HTTPS; SQLite se reserva para desarrollo local y pruebas.

## Instalación

Desde la raíz del repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd alimenta_forma_prototipo

npm ci

python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r api/apialimentaforma/requirements.txt
```

No se deben versionar `.env`, bases de datos SQLite, `media/`, `node_modules/`,
`dist/`, `coverage/` ni otros artefactos generados.

## Variables de entorno

El backend lee primero las variables del proceso y después, para las variables
que aún no estén definidas, el archivo `.env` de la raíz. Para desarrollo:

```bash
cp .env.example .env
```

Las listas se separan por comas, los booleanos aceptan `true/false`, `1/0`,
`yes/no` u `on/off`, y las opciones avanzadas son objetos JSON.

| Variable | Predeterminado / requisito | Uso |
|---|---|---|
| `APP_ENV` | `development` | Uno de `development`, `test` o `production`. |
| `SECRET_KEY` | Valor inseguro solo en desarrollo; obligatoria en producción | Clave de Django, con al menos 50 caracteres en producción. |
| `DEBUG` | Activo fuera de producción | Django rechaza `DEBUG=true` en producción. |
| `ALLOWED_HOSTS` | Vacía; obligatoria en producción | Hosts permitidos, separados por comas. |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Motor de base de datos. |
| `DB_NAME` | `api/apialimentaforma/db.sqlite3`; obligatoria en producción | Nombre o ruta de la base de datos. |
| `DB_USER` | Vacía | Usuario de la base de datos. |
| `DB_PASSWORD` | Vacía; obligatoria en producción no SQLite | Contraseña de la base de datos. |
| `DB_HOST`, `DB_PORT` | Vacías | Servidor y puerto de la base de datos. |
| `DB_CONN_MAX_AGE` | `0` | Persistencia de conexiones en segundos. |
| `DB_OPTIONS` | `{}` | Opciones JSON del motor. |
| `CORS_ALLOWED_ORIGINS` | Vacía | Orígenes del frontend autorizados, separados por comas. |
| `CORS_ALLOW_CREDENTIALS` | `true` | Autoriza el envío de la cookie de sesión mediante CORS. |
| `CSRF_TRUSTED_ORIGINS` | Vacía | Orígenes completos de confianza para CSRF. |
| `MEDIA_URL`, `MEDIA_ROOT` | `/media/`, directorio `media` | URL y ubicación de archivos subidos. |
| `STATIC_URL`, `STATIC_ROOT` | `/static/`, directorio `staticfiles` | URL y ubicación de estáticos recopilados. |
| `STORAGE_BACKEND` | `FileSystemStorage` | Clase de almacenamiento de archivos. |
| `STORAGE_OPTIONS` | `{}` | Opciones JSON del almacenamiento de archivos. |
| `STATIC_STORAGE_BACKEND` | `StaticFilesStorage` | Clase de almacenamiento de estáticos. |
| `STATIC_STORAGE_OPTIONS` | `{}` | Opciones JSON del almacenamiento de estáticos. |
| `SECURE_HSTS_SECONDS` | `31536000` | Duración de HSTS en producción. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` | `true` | Opciones de HSTS en producción. |
| `TRUST_X_FORWARDED_PROTO` | `false` | Confía en el HTTPS indicado por un proxy controlado. |
| `VITE_API_BASE_URL` | `/api/v1` | URL base que usa el cliente web para llamar a la API. |

En producción se exigen secreto, hosts y base de datos válidos, se desactiva la
depuración y se habilitan redirección HTTPS, cookies seguras y HSTS. Solo se debe
activar `TRUST_X_FORWARDED_PROTO` si el proxy elimina la cabecera aportada por el
cliente. Los secretos de base de datos o almacenamiento deben existir únicamente
en el entorno.

## Base de datos y migraciones

Aplica las migraciones después de configurar el entorno y antes de iniciar el
backend. El superusuario es opcional:

```bash
python api/apialimentaforma/manage.py migrate
python api/apialimentaforma/manage.py createsuperuser
```

Los tipos y grupos de rol canónicos se sincronizan desde la propia aplicación al
crear o actualizar perfiles; no se necesita cargar un fixture inicial. Tras
cambiar modelos, crea y revisa la migración y confirma que no falte ninguna:

```bash
python api/apialimentaforma/manage.py makemigrations
python api/apialimentaforma/manage.py makemigrations --check --dry-run
```

## Arranque en desarrollo

Ejecuta cada servicio en un terminal distinto desde la raíz:

```bash
# Terminal 1: API en http://127.0.0.1:8000/api/v1/
python api/apialimentaforma/manage.py runserver

# Terminal 2: SPA en http://127.0.0.1:5173/
npm run dev
```

Si ambos servicios están en orígenes distintos, configura `VITE_API_BASE_URL`,
`CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS` con los orígenes completos. Para
un despliegue, compila el frontend con `npm run build`, sirve `dist/` desde un
servidor web y ejecuta Django mediante un servidor WSGI/ASGI de producción detrás
de HTTPS; `runserver` y el servidor de Vite no son servidores de producción.

## API y autenticación

Todas las rutas parten de `/api/v1/` y terminan en `/`. La autenticación usa la
**sesión de Django**: al iniciar sesión el backend entrega una cookie de sesión,
que el navegador debe enviar con `credentials: "include"`. Las operaciones no
seguras (`POST`, `PUT`, `PATCH`, `DELETE`) autenticadas requieren además el token
CSRF en la cabecera `X-CSRFToken`. `GET /api/v1/auth/me/` establece la cookie CSRF
y devuelve el usuario si ya existe una sesión.

| Método y endpoint | Descripción | Acceso principal |
|---|---|---|
| `POST /api/v1/auth/register/` | Registra un usuario y su perfil. | Público. |
| `POST /api/v1/auth/login/` | Recibe `username` y `password`; inicia la sesión. | Público. |
| `POST /api/v1/auth/logout/` | Cierra la sesión actual. | Usuario autenticado + CSRF. |
| `GET /api/v1/auth/me/` | Devuelve el usuario actual y prepara CSRF. | Usuario autenticado. |
| `/api/v1/usertype/` | Catálogo de tipos de usuario. | Lectura pública; escritura de administración. |
| `/api/v1/profile/` | Perfiles. | Propietario; administración ve y gestiona todos. |
| `/api/v1/offer/` | Membresías/ofertas. | Lectura pública; escritura de administración. |
| `/api/v1/Announcement/` | Anuncios. | Lectura pública; empresa propietaria o administración escribe. |
| `/api/v1/content/` | Contenidos. | Lectura pública; escritura de administración. |
| `/api/v1/course/` | Cursos. | Lectura pública; profesor propietario o administración escribe. |
| `/api/v1/registration/` | Matrículas. | Alumno propietario o administración. |
| `/api/v1/attendance/` | Asistencias de cursos. | Profesor del curso, alumno implicado o administración; la escritura corresponde al profesor/administración. |
| `/api/v1/mark/` | Notas de cursos. | Profesor del curso, alumno implicado o administración; la escritura corresponde al profesor/administración. |

Las rutas de recursos son `ModelViewSet`: la colección admite las operaciones
permitidas en `/<recurso>/` y el detalle en `/<recurso>/<id>/`. Los filtros de
consulta impiden que alumnos, profesores y empresas obtengan objetos privados
ajenos aunque conozcan su identificador. Actualmente no hay una ruta OpenAPI ni
una interfaz navegable de documentación; su incorporación se sigue en AF-207.

## Calidad y pruebas

Los mismos comandos se ejecutan en `.github/workflows/ci.yml` para cada `push` y
pull request, en trabajos independientes de frontend y backend:

```bash
# Frontend
npm run lint
npm test
npm run build
npm run test:coverage       # cobertura local opcional

# Backend
python api/apialimentaforma/manage.py test api.test_suite
python api/apialimentaforma/manage.py check
python api/apialimentaforma/manage.py makemigrations --check --dry-run
```

La suite frontend vive en `tests/frontend/`; la suite de dominio Django está en
`api/apialimentaforma/api/test_suite/`.
