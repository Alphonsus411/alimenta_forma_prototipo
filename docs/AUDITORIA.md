# Auditoría inicial y tareas del proyecto

Fecha de inicio: 29 de julio de 2026.

## Estado comprobado

- **Frontend:** la compilación estaba bloqueada porque `Home.jsx` importaba `Announcement`, pero el archivo se llamaba `Anouncement.jsx`. ESLint también detectó 26 errores (principalmente imports de `React` innecesarios).
- **Tests frontend:** Vitest, React Testing Library y `user-event` se ejecutan sobre jsdom desde `tests/frontend/`, con scripts para suite y cobertura.
- **Backend:** la configuración obsoleta de CoreAPI se retiró y Django arranca correctamente. DRF resuelve ahora su clase OpenAPI mantenida por defecto; publicar el esquema y su documentación continúa pendiente en AF-207.
- **Modelo de usuario:** la señal que crea `Profile` no aportaba los campos obligatorios ni una categoría, por lo que crear cualquier usuario producía un error de integridad.
- **Calidad y seguridad:** `SECRET_KEY`, `DEBUG` y hosts están codificados para desarrollo; la API expone todos los `ModelViewSet` sin permisos explícitos.

## Matriz de rutas, operaciones y roles

La matriz describe lo que la interfaz ofrece actualmente, no capacidades futuras.
**Público** significa que no requiere sesión, **propio** limita los datos a la
persona autenticada y **asignado** limita la gestión a cursos del docente. Un
guion indica que la operación no debe mostrarse ni poder ejecutarse desde esa
ruta.

| Ruta / operación observable | Anónimo | Alumno | Profesor | Empresa | Administración |
| --- | --- | --- | --- | --- | --- |
| `/`, `/about`, `/faqs`, `/jobs`, `/coorp`: consultar información | Público | Permitido | Permitido | Permitido | Permitido |
| `/courses`, `/courses/:courseId`: consultar catálogo y ficha | Público | Permitido | Permitido | Permitido | Permitido |
| `/login`, `/register`: iniciar sesión / crear cuenta pública | Permitido | No necesario | No necesario | No necesario | Registro no público |
| `/profile`: consultar y editar el perfil propio | Identificación requerida | Propio | Propio | Propio | Propio o gestión mediante API administrativa |
| `/profile`: cerrar sesión | — | Permitido | Permitido | Permitido | Permitido |
| `/courses/:courseId/registration`: solicitar matrícula individual | Identificación requerida | Propio | — | — | — |
| `/student`: consultar progreso, asistencia y notas | Identificación requerida | Propio | — | — | Consulta administrativa mediante API |
| `/courses/:courseId/classroom`: consultar el aula | Identificación requerida | Con matrícula propia | Según asignación en API | — | Permitido por API |
| `/teacher`: crear o editar cursos | Identificación requerida | — | Asignado | — | Gestión administrativa mediante API |
| `/teacher`: consultar matrículas y registrar asistencia o notas | Identificación requerida | — | Asignado | — | Gestión administrativa mediante API |
| `/admin/`: operaciones administrativas de Django | Identificación requerida | — | — | — | Permitido |
| Cualquier ruta web desconocida: recuperar navegación | Página 404 | Página 404 | Página 404 | Página 404 | Página 404 |

Las pruebas frontend ejercitan las restricciones en términos visibles: destino
de la navegación, encabezados, mensajes, controles disponibles y resultados de
las acciones. Las comprobaciones de permisos definitivas permanecen además en
la suite API, ya que ocultar un control no constituye una barrera de seguridad.

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
- [x] **AF-121:** sustituir los textos provisionales y definir las páginas públicas de empresas, empleo y área docente conforme a `PRODUCTO.md`, con navegación y pruebas de renderizado y accesibilidad.
- [x] **AF-122:** incorporar el recorrido web inicial del alumno: ficha y aula del curso, matrícula protegida y panel de progreso con contenidos, asistencia, regularidad, notas y finalización. La interfaz contempla carga, error, ausencia de datos, sesión anónima, duplicados y permisos insuficientes mediante pruebas con API simulada. Las reglas avanzadas de AF-109 y AF-111 a AF-116 continúan pendientes.
- [x] **AF-123:** implementar el panel restringido del docente para gestionar cursos propios, matrículas, asistencias y calificaciones, representando los errores de dominio de la API y cubriendo el recorrido con pruebas frontend. El panel valida la categoría de la sesión antes de solicitar datos, filtra visualmente los cursos asignados, permite altas y correcciones y anticipa el promedio; la API limita al docente la consulta de matrículas de sus cursos y rechaza notas de alumnos no matriculados.
- [x] **AF-124:** consolidar pruebas frontend observables para navegación principal, cierre de sesión, rutas protegidas, restricciones por rol, enlaces del perfil, 404, formularios docentes y recorridos de matrícula; fijar una línea base de cobertura global del 90 % en sentencias/líneas, 80 % en funciones y 70 % en ramas.
- [ ] **AF-125:** elevar gradualmente los umbrales de Vitest sin rebajarlos: primero ramas al 75 % al completar autenticación y errores HTTP, después al 80 % al cubrir permisos por rol; revisar en cada incremento que las aserciones sigan describiendo resultados visibles y no detalles internos.

### P1 — Ciclo formativo definido en producto

Las siguientes capacidades de [`PRODUCTO.md`](PRODUCTO.md) todavía no están
implementadas. Cada tarea incluye un criterio observable para poder cerrarla sin
interpretaciones subjetivas.

- [ ] **AF-109 — Catálogo, modalidades y ficha del curso:** modelar las ocho áreas formativas y las modalidades presencial, online y mixta, junto con fechas, horario, plazas, duración, ubicación/acceso y precio de cada edición. **Verificación:** la API rechaza valores fuera de catálogo y fechas o cupos incoherentes; el catálogo web permite filtrar por área y modalidad y muestra la ficha completa; existen tests de modelo, API y UI para cada modalidad.
- [ ] **AF-110 — Flujo de publicación y estados:** sustituir el estado provisional por borrador, en revisión, publicado, inscripción cerrada, en desarrollo, finalizado, cerrado y cancelado, con permisos y transiciones de `PRODUCTO.md`. **Verificación:** una migración conserva los cursos existentes; una matriz automatizada acepta todas las transiciones permitidas y rechaza las restantes; solo administración puede publicar, cancelar y cerrar, y el catálogo anónimo solo muestra cursos publicados que corresponda mostrar.
- [ ] **AF-111 — Inscripción completa y cupos:** incorporar plazo, cupo, solicitudes pendientes, lista de espera, confirmación, rechazo, cancelación y resultados finales sin confundirlos con la regularidad. **Verificación:** pruebas transaccionales demuestran que no hay duplicados ni sobrecupo ante solicitudes concurrentes, que una baja promociona a la primera persona en espera y que cada decisión conserva fecha y motivo y se muestra al alumno.
- [ ] **AF-112 — Requisitos previos:** permitir requisitos estructurados, evidencias, caducidad y validación automática o administrativa, congelando la decisión al confirmar. **Verificación:** no se confirma una solicitud con requisitos obligatorios pendientes o vencidos; se puede subsanar dentro del plazo; un test demuestra que editar el requisito del curso no altera la evidencia histórica de una matrícula confirmada.
- [ ] **AF-113 — Acceso y progreso de contenidos:** ordenar y programar la liberación de materiales y actividades, restringirlos a matrículas confirmadas y registrar progreso y entregas. **Verificación:** tests de permisos niegan acceso anónimo, ajeno, anticipado o posterior a cancelación; un alumno autorizado puede completar una actividad y consultar su progreso, y el progreso alimenta la finalización.
- [ ] **AF-114 — Sesiones y asistencia por modalidad:** crear sesiones computables con fecha y peso, registrar rectificaciones auditadas e integrar evidencias online para cursos mixtos. **Verificación:** la API impide registros fuera del curso o por actores no autorizados, calcula el porcentaje ponderado para presencial, online y mixta, permite consulta y solicitud de revisión del alumno y conserva autor, instante y valores de cada corrección.
- [ ] **AF-115 — Plan y cálculo de evaluación:** definir actividades obligatorias, notas de 0 a 10, ponderaciones que sumen 100 %, nota mínima y política de evidencias ausentes. **Verificación:** la publicación falla con un plan inválido; pruebas parametrizadas calculan aprobado, no aprobado y no evaluable en casos límite; solo el docente asignado o administración registra notas y el alumno recibe nota y retroalimentación publicadas.
- [ ] **AF-116 — Finalización y cierre:** automatizar la propuesta de resultado combinando nota, asistencia, actividades y requisitos, y congelar la edición ordinaria al cerrar. **Verificación:** el curso no cierra si quedan resultados pendientes ni antes de finalizar; los tres resultados se obtienen conforme a los criterios publicados; una corrección posterior requiere privilegio, motivo y registro de auditoría.
- [ ] **AF-117 — Certificados verificables:** emitir un certificado único al aprobar, permitir su descarga, verificación pública mínima y revocación motivada. **Verificación:** no se emite sin matrícula confirmada, curso cerrado y resultado aprobado; reintentar no duplica el certificado; el documento contiene todos los campos definidos en producto y el código público diferencia vigente, revocado e inexistente sin revelar otros datos.
- [ ] **AF-118 — Gestión de formación por empresa:** permitir a una empresa autorizada iniciar y seguir inscripciones de su plantilla sin obtener por defecto datos académicos privados. **Verificación:** pruebas de autorización acreditan consentimiento o base habilitante, impiden consultar notas, asistencia o certificados no autorizados y garantizan que una empresa nunca accede a personas vinculadas a otra.
- [ ] **AF-119 — Auditoría y notificaciones de dominio:** registrar actor, instante y cambios de publicación, matrícula, asistencia, evaluación, cierre y certificado, y notificar las decisiones relevantes. **Verificación:** cada operación genera una entrada inmutable consultable solo por administración y una notificación idempotente para la persona afectada; las pruebas comprueban valor anterior/nuevo, motivo obligatorio y ausencia de duplicados al reintentar.
- [ ] **AF-120 — Recorrido web por rol:** construir las vistas de alumno, docente, empresa y administración necesarias para ejecutar el ciclo completo, con acciones limitadas por rol. **Verificación:** pruebas end-to-end recorren publicación, inscripción, contenidos, asistencia, evaluación, cierre y certificado; además, una prueba negativa por rol confirma que no aparecen acciones ni datos no autorizados.

> **Avance 30/07/2026:** se definieron e implementaron los metadatos base de
> AF-109, el catálogo de categorías, las lecciones ordenadas y los estados y
> transiciones de AF-110, incluida la conservación explícita de datos legados.
> Permanecen abiertos los filtros del catálogo, el flujo completo de revisión y
> las verificaciones integrales indicadas en ambos criterios de aceptación.

> **Avance de AF-116 y AF-117 (30/07/2026):** se incorporaron reglas de
> aprobación configurables por curso, cálculo idempotente de finalización con
> revisiones históricas, emisión única al aprobar un curso cerrado y consulta,
> descarga y verificación pública mínima de certificados. Permanecen abiertas
> ambas tareas porque el cierre transaccional del curso, la matrícula confirmada
> de AF-111 y el flujo administrativo de revocación motivada aún no están
> implementados de extremo a extremo.

### P2 — Producción y mantenimiento

- [x] **AF-201:** mover secretos y configuración (`SECRET_KEY`, `DEBUG`, hosts, base de datos, CORS/CSRF y almacenamiento) a variables de entorno validadas; producción rechaza secretos ausentes, `DEBUG` y hosts vacíos, y activa su endurecimiento HTTPS.
- [x] **AF-202:** definir límites reutilizables de tamaño, extensión y tipo MIME para imágenes, CV, documentos, vídeos y anuncios; usar rutas normalizadas con nombres UUID y representar la imagen de perfil ausente sin depender de un archivo predeterminado inexistente.
- [x] **AF-203:** añadir CI con trabajos separados para frontend y backend que ejecutan lint, build, ambas suites, comprobación de Django y migraciones pendientes. La auditoría automática de dependencias se pospone hasta definir la política de AF-206.
- [x] **AF-204:** documentar versiones, requisitos, instalación, variables de entorno, migraciones y datos iniciales, arranque/despliegue, comandos de calidad, API y autenticación por sesión con CSRF.
- [x] **AF-205A — Página 404:** mostrar una ruta de página no encontrada con un mensaje comprensible y una acción para volver al inicio; cubrir la ruta desconocida con una prueba de navegación.
- [x] **AF-205B — Límite global de errores:** aislar fallos inesperados de renderizado mediante una recuperación segura y comprobada, sin interferir con los estados HTTP locales de `AsyncState`.
- [ ] **AF-205C — SEO básico:** definir metadatos generales y específicos por página, URL canónica y datos sociales, y comprobar el resultado generado.
- [ ] **AF-205D — Auditoría responsive y accesible:** revisar con criterios y anchos reproducibles la navegación, formularios, contraste, foco, landmarks y ausencia de desbordamiento; documentar y corregir los hallazgos.
- [x] **AF-206:** revisar dependencias (incluido el paquete redundante `django-rest-framework`) y fijar una política de actualizaciones. Se retiró `django-rest-framework==0.1.0`: era un paquete contenedor distinto y redundante que dependía de la distribución oficial ya fijada, `djangorestframework==3.15.2`, que proporciona `rest_framework`. La frecuencia, revisión de vulnerabilidades, matriz compatible y responsables de aprobación quedan definidas en [`DEPENDENCIAS.md`](DEPENDENCIAS.md).
- [x] **AF-207:** integrar drf-spectacular, compatible con las versiones fijadas de Django y DRF, y publicar el esquema OpenAPI y Swagger UI en rutas estables. El contrato documenta sesión, CSRF, parámetros, archivos, validación y permisos; se cerró después de que la prueba validase el esquema y confirmase los endpoints principales.

## Criterio de acabado

El prototipo no se considerará terminado hasta que los flujos de usuario P1 funcionen de extremo a extremo, los endpoints estén protegidos, la configuración sensible sea externa y CI confirme lint, build, ambas suites, configuración de Django y ausencia de migraciones pendientes.

> La suite backend se ejecuta desde la raíz con `python api/apialimentaforma/manage.py test api.test_suite`; indicar el paquete evita que el directorio contenedor no empaquetado interfiera con el descubrimiento estándar de `unittest`.

> **Avance de AF-205D (30/07/2026):** la cabecera usa landmarks semánticos,
> identifica la página activa y expone el control del menú móvil con nombre,
> estado y relación accesibles. El menú cerrado deja de incluir enlaces fuera de
> pantalla en el orden de tabulación y el botón dispone de foco visible. La
> auditoría integral de las demás vistas y anchos continúa pendiente.

> **Avance de AF-205D (30/07/2026):** la navegación secundaria del perfil se
> limita a destinos implementados (inicio, identificación, progreso y perfil),
> usa un landmark con nombre y aporta un nombre accesible a cada icono. Se
> retiraron búsqueda, listas y favoritos porque el prototipo no implementa aún
> esas funciones, y una prueba impide reintroducir enlaces sin destino o nombre.
