# Guía de trabajo para Alimenta Forma

## Alcance

Estas instrucciones se aplican a todo el repositorio.

## Flujo obligatorio

1. Antes de modificar código, revisar `docs/AUDITORIA.md` y mantener sus tareas al día.
2. Separar los cambios de frontend (`src/`) y backend (`api/`) siempre que sea posible.
3. Añadir o actualizar tests para cada corrección de lógica.
4. Ejecutar antes de entregar:
   - `npm run lint`
   - `npm run build`
   - `python api/apialimentaforma/manage.py test api.test_suite`
   - `python api/apialimentaforma/manage.py check`
5. No versionar secretos, bases de datos, archivos subidos, `node_modules` ni artefactos de compilación.

## Convenciones

- Documentar decisiones y tareas en español.
- Usar nombres de componentes React en PascalCase y hacer coincidir exactamente el nombre del archivo y sus imports.
- Mantener la lógica de dominio de Django cubierta por tests unitarios dentro de `api/apialimentaforma/api/test_suite/`.
- Crear migraciones al cambiar modelos y comprobarlas con `makemigrations --check --dry-run`.
