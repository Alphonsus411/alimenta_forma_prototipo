# Política de dependencias

Esta política cubre npm, Python, acciones de CI, imágenes base y paquetes del
sistema usados para construir o ejecutar Alimenta Forma.

## Frecuencia y flujo de actualización

| Tipo | Frecuencia mínima | Plazo objetivo |
| --- | --- | --- |
| Vulnerabilidad crítica explotable | Al recibir la alerta | Mitigar o actualizar en 24 horas |
| Vulnerabilidad alta | Revisión semanal | Resolver en 7 días |
| Vulnerabilidad media o baja | Revisión mensual | Incluir en el siguiente ciclo planificado |
| Parches y versiones menores | Lote mensual | Tras superar CI y preproducción |
| Versiones mayores y runtimes | Revisión trimestral | Plan específico antes de fin de soporte |

Se agrupan actualizaciones compatibles para evitar ruido, pero seguridad puede
abrir un cambio individual urgente. Cada pull request debe explicar motivo,
notas de versión, cambios transitivos, vulnerabilidades, compatibilidad y plan
de reversión; debe regenerar el archivo de bloqueo que corresponda y superar
lint, build, suites backend/frontend, comprobación de Django y migraciones.

## Revisión de vulnerabilidades y procedencia

- Ejecutar semanalmente y en CI `npm audit` sobre `package-lock.json` y
  `python -m pip_audit -r api/apialimentaforma/requirements.txt` (instalando
  `pip-audit` como herramienta de CI, no como dependencia de ejecución).
- Activar alertas automáticas del repositorio y análisis de imágenes y sistema
  operativo. Revisar también las acciones de CI y fijarlas por versión confiable.
- No aceptar un hallazgo solo por su puntuación: confirmar si alcanza código de
  producción, exposición, versión corregida y controles compensatorios.
- Una excepción requiere identificador, justificación, alcance, mitigación,
  responsable y fecha de caducidad; se revisa cada semana hasta cerrarla. No se
  usa `--force` ni se ignora un aviso sin esta evidencia.
- Generar y conservar con cada versión un inventario/SBOM y los resultados del
  análisis para poder localizar rápidamente una dependencia afectada.

## Compatibilidad soportada

- **Frontend y herramientas:** Node.js 20 LTS y npm compatible con lockfile v3;
  navegadores con soporte vigente en sus dos últimas versiones estables. La SPA
  debe probarse al menos en motores Chromium, Firefox y WebKit antes de cambiar
  el objetivo soportado.
- **Backend:** Python 3.12, Django 5.0.x y Django REST Framework 3.15.x según las
  versiones fijadas en `requirements.txt`. Producción usa PostgreSQL en una
  versión aún soportada por su fabricante y por la versión de Django; SQLite
  solo se soporta para desarrollo y tests.
- No se mezcla en una misma actualización un salto de runtime, framework mayor
  y base de datos mayor. Primero se confirma en documentación oficial la matriz
  de compatibilidad, después se ejecutan suites y migraciones sobre una copia de
  producción anonimizada y finalmente se prueba una reversión en preproducción.
- Una versión al final de soporte abre una actualización prioritaria. Cambiar
  esta matriz exige decisión documentada y actualización simultánea de README,
  CI, imágenes y este documento.

Las versiones Python están fijadas de forma directa para instalaciones
reproducibles. `djangorestframework==3.15.2` es la distribución oficial que
proporciona el módulo `rest_framework`. Se elimina `django-rest-framework==0.1.0`
porque es un paquete distinto y redundante que solo dependía de la distribución
oficial; conservar ambos añadía una instalación indirecta sin aportar
funcionalidad.

## Responsabilidades y aprobación

| Rol | Responsabilidad |
| --- | --- |
| Mantenimiento técnico | Revisa alertas, prepara el cambio, comprueba compatibilidad y adjunta resultados de CI. |
| Responsable de seguridad | Evalúa vulnerabilidades, mitigaciones y excepciones con caducidad. |
| Responsable de operaciones | Valida imágenes, migraciones, observabilidad, copia y reversión. |
| Responsable técnico del proyecto | **Aprueba** la incorporación, actualización o retirada antes de fusionar. |

El autor no aprueba su propio cambio: se requiere al menos la revisión del
responsable técnico. Seguridad también debe aprobar vulnerabilidades altas o
críticas y sus excepciones; operaciones debe aprobar cambios de runtime, base de
datos, almacenamiento o infraestructura. Si una misma persona ocupa varios
roles, otra persona mantenedora realiza la segunda revisión.

