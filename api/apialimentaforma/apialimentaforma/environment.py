"""Utilidades pequeñas para leer y validar la configuración del entorno."""

import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def load_dotenv(path: Path) -> None:
    """Carga un ``.env`` local sin sobrescribir variables ya exportadas."""
    if not path.is_file():
        return

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            raise ImproperlyConfigured(
                f"Línea {line_number} inválida en {path}: se esperaba NOMBRE=valor."
            )
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            raise ImproperlyConfigured(f"Nombre vacío en la línea {line_number} de {path}.")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(name, value)


def env(name: str, default=None, *, required: bool = False):
    value = os.environ.get(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ImproperlyConfigured(f"Falta la variable de entorno obligatoria {name}.")
    return value


def env_bool(name: str, default: bool = False) -> bool:
    value = str(env(name, str(default))).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(
        f"{name} debe ser un booleano: true/false, 1/0, yes/no u on/off."
    )


def env_int(name: str, default: int) -> int:
    try:
        return int(env(name, default))
    except (TypeError, ValueError) as error:
        raise ImproperlyConfigured(f"{name} debe ser un número entero.") from error


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in str(env(name, default)).split(",") if item.strip()]


def env_json(name: str, default=None) -> dict:
    raw_value = env(name)
    if raw_value in (None, ""):
        return {} if default is None else default
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as error:
        raise ImproperlyConfigured(f"{name} debe contener JSON válido.") from error
    if not isinstance(value, dict):
        raise ImproperlyConfigured(f"{name} debe contener un objeto JSON.")
    return value
