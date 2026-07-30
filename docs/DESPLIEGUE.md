# Despliegue de referencia

Este documento define una arquitectura de producción y un procedimiento operable
para Alimenta Forma. Los nombres de servicios son ejemplos y no obligan a un
proveedor concreto.

## Arquitectura

```text
Internet
   |
   v
Proxy/balanceador HTTPS (TLS, HSTS, límites y logs de acceso)
   |-- /, recursos de la SPA --------> almacenamiento/CDN de `dist/`
   |-- /api/, /admin/ y /static/ ----> Django WSGI/ASGI (2 o más réplicas)
   |                                      |-- PostgreSQL gestionado
   |                                      `-- almacenamiento de objetos (medios)
   `-- /media/ ----------------------> almacenamiento de objetos/CDN (lectura)

Django y tareas operativas ---> logs, seguimiento de errores y métricas
PostgreSQL + objetos ---------> copias cifradas en otra cuenta o región
```

- **SPA:** se genera una vez con `npm ci && npm run build`. El directorio
  `dist/` se publica como contenido inmutable en almacenamiento estático o CDN;
  las rutas desconocidas se reescriben a `index.html`, pero `/api`, `/admin`,
  `/static` y `/media` nunca deben caer en esa regla. `VITE_API_BASE_URL` se fija
  durante la compilación, preferiblemente a `/api/v1` en el mismo origen.
- **Django:** se ejecuta con un servidor WSGI/ASGI de producción, nunca con
  `runserver`, en una red privada y con réplicas sin estado. Las sesiones y los
  datos compartidos residen en la base de datos; las subidas no se guardan en el
  disco efímero de una réplica.
- **Base de datos:** PostgreSQL gestionado, con cifrado, alta disponibilidad,
  conexiones TLS y credenciales de mínimo privilegio. SQLite queda limitado a
  desarrollo y tests.
- **Archivos:** `STORAGE_BACKEND` y `STORAGE_OPTIONS` apuntan a un almacén de
  objetos duradero con versionado y cifrado. Deben separarse los medios privados
  de los recursos públicos; los primeros se entregan mediante autorización y
  URL temporal, no haciendo público el contenedor completo.
- **Proxy HTTPS:** termina TLS, redirige HTTP a HTTPS, conserva host y dirección
  de cliente, elimina cualquier `X-Forwarded-Proto` recibido y lo vuelve a fijar.
  Solo en ese caso se activa `TRUST_X_FORWARDED_PROTO=true`. Se limitan cuerpo,
  tiempo y tasa de petición de acuerdo con los límites de subida de la API.

Los secretos se inyectan desde un gestor de secretos y no desde la imagen ni el
repositorio. Se configura `APP_ENV=production`, `DEBUG=false`, `SECRET_KEY`,
`ALLOWED_HOSTS`, base de datos, orígenes CORS/CSRF y almacenamiento según
`.env.example`. Django debe estar aislado de Internet salvo a través del proxy;
la base de datos y el almacén aceptan únicamente las identidades de servicio.

## Preparación y orden de publicación

Cada versión recibe un identificador inmutable (etiqueta o SHA) compartido por
la imagen de Django y los artefactos de la SPA. Antes de producción, CI debe
superar lint, build, tests, `manage.py check --deploy` con configuración de
producción y `makemigrations --check --dry-run`.

1. Registrar versión, responsable, ventana, migraciones y plan de reversión.
2. Crear y verificar una copia de seguridad previa de base de datos y medios.
3. Construir artefactos una sola vez, analizarlos y desplegar primero en un
   entorno de preproducción equivalente.
4. Aplicar las migraciones desde una única tarea de lanzamiento, no desde cada
   réplica: `python api/apialimentaforma/manage.py migrate --noinput`.
5. Recopilar estáticos de Django en un destino versionado:
   `python api/apialimentaforma/manage.py collectstatic --noinput`. No se debe
   confundir `staticfiles/` con los medios subidos ni incluirlo en Git.
6. Publicar las réplicas Django nuevas, comprobar salud y ejecutar una prueba
   funcional de sesión, CSRF, lectura y una operación reversible.
7. Publicar `dist/` y cambiar el puntero/origen del CDN de forma atómica. Purgar
   únicamente `index.html`; los recursos con hash se conservan en caché.
8. Vigilar errores, latencia y saturación durante toda la ventana y anotar el
   resultado.

## Migraciones sin pérdida de datos

Las migraciones siguen el patrón **expandir, migrar y contraer** y deben ser
compatibles al menos con la versión anterior mientras conviven réplicas:

1. **Expandir:** añadir tablas o columnas inicialmente anulables, índices sin
   bloquear cuando el motor lo permita y escrituras compatibles. No renombrar,
   eliminar ni convertir destructivamente en esta fase.
2. **Migrar datos:** ejecutar una migración de datos reversible o un trabajo por
   lotes, idempotente y reanudable. Medir filas pendientes y evitar una única
   transacción o bloqueo prolongado.
3. **Cambiar lectura:** desplegar código que lea el nuevo formato y validar
   conteos, restricciones y una muestra de datos contra el formato anterior.
4. **Contraer:** solo en otra versión y tras terminar la reversibilidad, imponer
   `NOT NULL` o retirar el campo antiguo. Conservar copia y autorización expresa
   para cualquier eliminación.

Toda migración se ensaya sobre una restauración anonimizada de tamaño real y se
revisa con `showmigrations`, `sqlmigrate` y `migrate --plan`. Si no es reversible,
debe declararse antes de la ventana: su reversión será restaurar la copia y no
ejecutar `migrate <anterior>` a ciegas.

## Persistencia, copias y restauración

- **Medios:** habilitar versionado y reglas de ciclo de vida en el almacén de
  objetos. Una publicación nunca borra ni sobrescribe el prefijo actual. Probar
  periódicamente carga, descarga autorizada y caducidad de URL. `MEDIA_ROOT`
  local solo se admite en desarrollo; si se usa excepcionalmente en una
  instalación única, debe ser un volumen persistente montado en todas las
  réplicas y respaldado junto con la base de datos.
- **Base de datos:** mantener recuperación a un instante (PITR) y una copia
  completa diaria; **medios:** copia incremental/versionada diaria. Cifrar en
  tránsito y reposo, separar credenciales de borrado y replicar fuera del dominio
  de fallo. Política inicial: 7 copias diarias, 5 semanales y 12 mensuales; el
  responsable de operaciones debe ajustarla a los requisitos legales.
- Registrar duración, tamaño, checksum, versión de esquema y resultado de cada
  copia. Alertar si una ejecución falta o falla. Definir con negocio RPO y RTO;
  hasta aprobarlos, el despliegue no puede prometer objetivos concretos.

### Ensayo de restauración

Al menos trimestralmente, y antes de cambios destructivos: aislar un entorno,
restaurar primero PostgreSQL al instante elegido y luego la versión coherente de
medios; desplegar el mismo SHA, ejecutar `manage.py migrate`, `manage.py check`,
conteos e integridad de claves, abrir una muestra de archivos y completar una
prueba funcional. Documentar tiempos reales, pérdida observada y diferencias;
una copia no se considera válida hasta superar este ensayo. Nunca se prueba una
restauración sobrescribiendo producción.

## Observabilidad y salud

- **Registro:** proxy y Django escriben JSON a stdout con fecha UTC, nivel,
  servicio, versión, entorno, identificador de petición, ruta normalizada,
  estado, duración y usuario interno seudonimizado cuando proceda. No registrar
  contraseñas, cookies, CSRF, cabeceras de autorización, cuerpos ni datos
  personales. Centralizar con acceso restringido, retención definida y alertas
  ante picos de 5xx.
- **Errores:** integrar un recolector que agrupe excepciones de frontend y
  backend por versión, incluya trazas y request ID y elimine datos sensibles.
  Las versiones y mapas de fuentes se cargan de forma privada. Alertar por error
  nuevo, regresión o aumento de frecuencia.
- **Métricas:** exportar tasa de peticiones, 4xx/5xx, percentiles de latencia,
  réplicas, CPU/memoria, conexiones y bloqueos de PostgreSQL, espacio, duración
  y fallo de copias, uso/errores del almacén y resultados de migraciones. Los
  paneles y alertas deben vincularse al procedimiento operativo.
- **Salud:** antes de automatizar sondas se debe implementar y probar un endpoint
  no autenticado y sin datos sensibles. `/health/live` confirma únicamente que
  el proceso responde; `/health/ready` comprueba con límites breves la base de
  datos y demás dependencias indispensables. El balanceador retira una réplica
  solo por *readiness*; un fallo externo no debe provocar reinicios en cascada
  mediante *liveness*. Hasta disponer de esos endpoints, la comprobación HTTP
  manual de `/api/schema/` es solo una prueba de humo y **no** una sonda de salud
  contractual.

## Reversión

1. Detener el avance y registrar el incidente; no aplicar nuevas migraciones.
2. Si el esquema sigue siendo compatible, devolver proxy/CDN al SHA anterior,
   conservar los recursos estáticos con hash y verificar *readiness*, errores y
   el recorrido funcional. La base de datos y los medios no se reemplazan.
3. Si la migración reversible es la causa, drenar escrituras, obtener otra copia
   y ejecutar de forma controlada `manage.py migrate <app> <migración_anterior>`;
   validar antes de reabrir tráfico.
4. Si hubo una transformación destructiva o corrupción, declarar mantenimiento,
   aislar las escrituras y restaurar base y medios al mismo punto conforme al
   ensayo anterior. Comunicar la pérdida hasta el RPO real.
5. Confirmar métricas y pruebas, cerrar o escalar el incidente y documentar
   cronología, impacto, decisión y acciones preventivas. Nunca se fuerza una
   migración falsa ni se edita manualmente el historial en producción.

