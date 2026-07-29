# Auditoría inicial y tareas del proyecto

Fecha de inicio: 29 de julio de 2026.

## Estado comprobado

- **Frontend:** la compilación estaba bloqueada porque `Home.jsx` importaba `Announcement`, pero el archivo se llamaba `Anouncement.jsx`. ESLint también detectó 26 errores (principalmente imports de `React` innecesarios).
- **Tests frontend:** Vitest, React Testing Library y `user-event` se ejecutan sobre jsdom desde `tests/frontend/`, con scripts para suite y cobertura.
- **Backend:** la configuración obsoleta de CoreAPI se retiró y Django arranca correctamente. DRF resuelve ahora su clase OpenAPI mantenida por defecto; publicar el esquema y su documentación continúa pendiente en AF-207.
- **Modelo de usuario:** la señal que crea `Profile` no aportaba los campos obligatorios ni una categoría, por lo que crear cualquier usuario producía un error de integridad.
- **Calidad y seguridad:** `SECRET_KEY`, `DEBUG` y hosts están codificados para desarrollo; la API expone todos los `ModelViewSet` sin permisos explícitos.

## Tareas estructuradas

### P0 — Bloqueos básicos

- [x] **AF-001:** corregir el nombre del componente `Announcement` para que el frontend compile.
- [x] **AF-002:** retirar la configuración obsoleta/incompleta de CoreAPI y permitir que Django arranque. Comprobado con `manage.py check`; la recuperación de una ruta de documentación queda separada en AF-207.
- [x] **AF-003:** crear una suite backend real, separada por dominio.
- [x] **AF-004:** hacer que la creación automática de perfiles sea válida y cubrirla con tests.
- [x] **AF-005:** corregir los errores actuales de ESLint.

### P1 — Producto mínimo funcional

- [x] **AF-101:** conectar formularios de registro e inicio de sesión con una API autenticada. Se eligió sesión de Django con protección CSRF y se añadieron registro, inicio/cierre de sesión y usuario actual.
- [x] **AF-102:** definir permisos por rol para cada endpoint, filtrar los objetos visibles y evitar acceso anónimo de escritura.
- [x] **AF-103:** conectar cursos, membresías, anuncios y perfil con datos reales del backend; incluir estados accesibles de carga/error/vacío, reintento y edición del perfil autenticado mediante un cliente HTTP configurable.
- [x] **AF-104:** validar reglas de negocio (escala de notas, clases y precios, identidad de asistencias, duplicidad de matrícula/notas y rol profesor/alumno) mediante validadores, validación de modelos y restricciones de base de datos.
- [x] **AF-107:** definir la asistencia como presente/ausente y recalcular automáticamente la regularidad de la matrícula al crear, editar o eliminar asistencias.
- [x] **AF-108:** centralizar los roles y sincronizar cada perfil con un único grupo de rol canónico, incluso ante bases vacías, grupos parciales y cambios de categoría.
- [x] **AF-105:** añadir tests de API para autenticación, autorización, serializadores y respuestas CRUD, separados por autenticación, permisos, cursos, matrículas, asistencia, notas, archivos y roles.
- [x] **AF-106:** incorporar Vitest y React Testing Library en `tests/frontend/` y probar rutas, navegación, formularios, estados de carga/error/vacío y accesibilidad básica.

### P2 — Producción y mantenimiento

- [ ] **AF-201:** mover secretos y configuración (`SECRET_KEY`, `DEBUG`, hosts, base de datos y CORS) a variables de entorno.
- [ ] **AF-202:** definir almacenamiento y límites seguros para imágenes, CV, documentos y vídeos.
- [ ] **AF-203:** añadir CI para lint, build, tests, migraciones pendientes y auditoría de dependencias.
- [ ] **AF-204:** documentar instalación completa, variables de entorno, datos iniciales, API y despliegue.
- [ ] **AF-205:** añadir páginas 404, gestión global de errores, SEO básico y revisión responsive/accesible.
- [ ] **AF-206:** revisar dependencias (incluido el paquete redundante `django-rest-framework`) y fijar una política de actualizaciones.
- [ ] **AF-207:** elegir OpenAPI (por ejemplo, una integración mantenida) y restaurar una ruta de documentación de la API; la antigua vista CoreAPI fue retirada por estar obsoleta e incompleta.

## Criterio de acabado

El prototipo no se considerará terminado hasta que los flujos de usuario P1 funcionen de extremo a extremo, los endpoints estén protegidos, la configuración sensible sea externa, no haya migraciones pendientes y CI ejecute correctamente lint, build y todas las suites.

> La suite backend se ejecuta desde la raíz con `python api/apialimentaforma/manage.py test api.test_suite`; indicar el paquete evita que el directorio contenedor no empaquetado interfiera con el descubrimiento estándar de `unittest`.
