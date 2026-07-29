# Definición de producto de Alimenta Forma

## Propósito y alcance

Alimenta Forma es una plataforma para publicar, impartir y acreditar formación
para la hostelería y la alimentación. Esta definición describe el producto
objetivo y sirve como contrato funcional para diseño, desarrollo y aceptación.
No implica que todas las capacidades estén disponibles: las brechas entre este
objetivo y el prototipo se registran como tareas verificables en
[`AUDITORIA.md`](AUDITORIA.md).

## Públicos y responsabilidades

| Público | Necesidad principal | Capacidades objetivo |
|---|---|---|
| **Alumno** | Encontrar formación y acreditar lo aprendido. | Consultar el catálogo, comprobar requisitos, inscribirse, acceder al contenido, consultar su asistencia y evaluaciones, finalizar el curso y descargar sus certificados. |
| **Docente** | Impartir y evaluar una acción formativa. | Preparar el curso y sus contenidos, solicitar su publicación, consultar matrículas, registrar asistencia, evaluar al alumnado y cerrar el curso. |
| **Empresa** | Formar o incorporar profesionales. | Consultar formación, gestionar inscripciones de su plantilla y publicar oportunidades profesionales; solo puede consultar datos de aprendizaje con base legal y autorización adecuadas. |
| **Administración** | Gobernar el servicio y garantizar su trazabilidad. | Mantener catálogos, revisar y publicar cursos, gestionar usuarios e inscripciones, corregir incidencias con auditoría, supervisar resultados y emitir o revocar certificados. |

Una persona debe operar con los permisos del rol activo. El acceso a datos
personales, calificaciones y certificados se limita al interesado y a los roles
autorizados para impartir o administrar la formación.

## Catálogo formativo

Todo curso debe pertenecer al menos a una de estas áreas:

- **Manipulación de alimentos:** higiene personal, conservación, limpieza y
  prácticas seguras durante la manipulación.
- **Seguridad alimentaria:** APPCC, control de peligros, trazabilidad y normativa.
- **Nutrición:** fundamentos nutricionales, planificación y oferta equilibrada.
- **Cocina:** técnicas, procesos, producción y organización de cocina.
- **Sala:** servicio, atención al cliente, protocolo y operativa de sala.
- **Bar:** bebidas, cafetería, coctelería y gestión del servicio de barra.
- **Gestión hostelera:** costes, compras, equipos, operaciones y rentabilidad.
- **Alérgenos:** identificación, prevención de contaminación cruzada, información
  al consumidor y actuación segura.

Las áreas son un catálogo administrable: no deben almacenarse como texto libre y
una baja no debe borrar el histórico de cursos ya clasificados.

## Modalidades

| Modalidad | Definición | Evidencia de participación |
|---|---|---|
| **Presencial** | Docente y alumnado coinciden físicamente en las sesiones programadas. | Registro de asistencia por sesión presencial. |
| **Online** | Contenido y actividades se realizan a distancia, de forma síncrona o asíncrona. | Acceso/progreso de actividades y, si existen sesiones síncronas, asistencia. |
| **Mixta** | Combina sesiones presenciales y trabajo online obligatorio. | Evidencias de ambos componentes, evaluadas de manera conjunta. |

La ficha pública debe indicar modalidad, área, docente, fechas y horario, plazas,
duración, ubicación o mecanismo de acceso, requisitos previos, contenidos,
criterios de aprobación y, cuando corresponda, precio.

## Ciclo completo del curso

### 1. Publicación

1. El docente o la administración crea un borrador con la ficha completa.
2. El docente asocia contenidos y actividades en un orden definido.
3. La administración valida datos, permisos de los materiales, fechas,
   modalidad, plazas, requisitos y criterios de aprobación.
4. La administración publica el curso; desde ese momento aparece en el catálogo
   y admite inscripciones dentro del plazo configurado.

### 2. Inscripción

1. El alumno se identifica y solicita plaza, o una empresa autorizada inicia la
   solicitud para una persona de su plantilla.
2. El sistema comprueba plazo, plazas, ausencia de duplicados y requisitos
   previos.
3. Si todo se cumple, confirma la matrícula; si falta una validación manual, la
   deja pendiente; si no hay plazas, puede ofrecer lista de espera.
4. Toda confirmación, rechazo o cancelación se comunica al alumno y conserva su
   motivo y fecha.

### 3. Acceso a contenidos

1. Una matrícula confirmada permite acceder desde la fecha de inicio o desde la
   fecha expresamente configurada.
2. El alumno ve únicamente el contenido liberado para su edición del curso.
3. El sistema registra progreso y entregas necesarias para determinar la
   finalización, sin hacer públicos los datos individuales.
4. Al cancelar o rechazar una matrícula se retira el acceso, preservando el
   historial exigible.

### 4. Control de asistencia

1. El curso se descompone en sesiones fechadas; cada sesión indica si computa y
   el peso que tiene en la asistencia total.
2. El docente responsable o la administración registra presencia o ausencia y
   el sistema conserva autor, fecha y posteriores rectificaciones.
3. El alumno puede consultar sus registros y solicitar una revisión, pero no
   modificarlos directamente.
4. En modalidad mixta se combinan las sesiones computables con las evidencias
   online definidas en la ficha.

### 5. Evaluación

1. El docente registra las actividades y notas previstas en la ficha publicada.
2. El sistema calcula el resultado con la ponderación vigente y muestra al
   alumno notas, estado y retroalimentación publicadas.
3. Una rectificación posterior al cierre requiere motivo, actor autorizado y
   trazabilidad.

### 6. Finalización

1. Al llegar la fecha de fin, el docente revisa las evidencias y propone el
   cierre del alumnado.
2. El sistema aplica los criterios de aprobación y asigna **aprobado**, **no
   aprobado** o **no evaluable** a cada matrícula.
3. La administración cierra el curso cuando no quedan resultados pendientes.
   El cierre congela la edición ordinaria, pero no elimina contenidos ni
   evidencias históricas.

### 7. Emisión de certificado

1. El cierre con resultado aprobado genera un certificado único.
2. El documento identifica alumno, curso, área, modalidad, duración, fechas,
   fecha de emisión y entidad emisora, e incluye un código de verificación.
3. El alumno puede descargarlo y un tercero puede comprobar únicamente su
   autenticidad y vigencia mediante el código, sin acceder a otros datos.
4. La administración puede revocarlo indicando motivo y fecha; una revocación
   permanece auditable y la verificación pública informa de que ya no es válido.

## Estados

### Estados del curso

| Estado | Significado | Transiciones ordinarias |
|---|---|---|
| **Borrador** | Ficha editable y no visible en catálogo. | A revisión o cancelado. |
| **En revisión** | Pendiente de validación administrativa. | Publicado, borrador para subsanar o cancelado. |
| **Publicado** | Visible; acepta solicitudes durante el plazo. | Inscripción cerrada o cancelado. |
| **Inscripción cerrada** | Ya no admite nuevas solicitudes ordinarias. | En desarrollo o cancelado. |
| **En desarrollo** | La impartición está activa. | Finalizado o cancelado. |
| **Finalizado** | Terminó la docencia; pueden cerrarse resultados. | Cerrado. |
| **Cerrado** | Resultados consolidados y certificados emitibles. | Sin transición ordinaria. |
| **Cancelado** | No se impartirá o se interrumpió justificadamente. | Sin transición ordinaria; requiere motivo. |

Los estados actuales `inscripción`, `desarrollo` y `finalizado` del prototipo son
un subconjunto provisional. La implementación debe migrar los datos sin perder
su significado.

### Estados de matrícula

Una solicitud puede estar **pendiente**, **en lista de espera**, **confirmada**,
**rechazada** o **cancelada**. Tras la evaluación, una matrícula confirmada
queda **aprobada**, **no aprobada** o **no evaluable**. El estado de regularidad
por asistencia es un atributo calculado y no sustituye al estado de matrícula.

## Requisitos previos

- Cada curso declara requisitos estructurados o declara expresamente que no
  tiene ninguno antes de publicarse.
- Pueden incluir edad mínima, certificados o cursos previos, experiencia,
  documentación habilitante y necesidades técnicas o de presencialidad.
- Cada requisito indica si se valida automáticamente o por administración, qué
  evidencia admite y cuándo vence.
- No se confirma una matrícula mientras falte un requisito obligatorio. Un
  rechazo debe explicar el requisito incumplido y permitir subsanar durante el
  plazo cuando proceda.
- Los requisitos y evidencias se congelan al confirmar la matrícula para poder
  reconstruir la decisión, aunque cambie después la ficha del curso.

## Criterios de aprobación

Antes de publicar, cada curso debe fijar y mostrar:

- nota mínima final entre 0 y 10;
- porcentaje mínimo de asistencia computable, entre 0 % y 100 %;
- actividades obligatorias que deben completarse;
- ponderación de cada evaluación, cuya suma debe ser 100 %; y
- regla aplicable cuando una actividad no se entrega o una asistencia todavía
  no está registrada.

El resultado es **aprobado** solo si se cumplen simultáneamente la nota mínima,
la asistencia mínima, todas las actividades obligatorias y los requisitos que
deban seguir vigentes. Es **no evaluable** si faltan evidencias necesarias y la
política publicada así lo establece; en los demás incumplimientos es **no
aprobado**. No se emite certificado sin matrícula confirmada, curso cerrado y
resultado aprobado.

## Reglas de negocio transversales

1. Solo administración publica, cancela o cierra cursos; el docente solo actúa
   sobre cursos que tiene asignados.
2. Un alumno no puede tener dos matrículas activas en la misma edición.
3. Las plazas confirmadas nunca superan el cupo; una liberación ofrece la plaza
   siguiendo el orden de la lista de espera.
4. Fechas y transiciones deben ser coherentes: inscripción antes del inicio,
   inicio no posterior al fin y cierre únicamente después de finalizar.
5. Contenidos, asistencia, evaluaciones y certificados requieren una matrícula
   autorizada y respetan el principio de mínima información.
6. Notas válidas están entre 0 y 10; porcentajes entre 0 y 100 y ponderaciones
   completas suman 100 %.
7. Cambios sensibles (publicación, matrícula, asistencia, nota, cierre,
   certificado y revocación) conservan actor, instante, valor anterior, valor
   nuevo y motivo cuando corresponda.
8. Cancelar no equivale a borrar: cursos y matrículas con actividad conservan el
   histórico conforme a la política de retención.
9. Las decisiones y cambios relevantes se notifican a las personas afectadas.
10. Toda emisión es idempotente: un mismo resultado genera un solo certificado
    vigente, aunque se reintente la operación.

## Indicadores de aceptación del producto

El ciclo se considera completo cuando puede recorrerse de extremo a extremo con
cada modalidad, los permisos impiden accesos cruzados, las reglas se validan en
API y base de datos cuando corresponda, y pruebas automatizadas demuestran las
transiciones, cálculos, errores y trazabilidad descritos.
