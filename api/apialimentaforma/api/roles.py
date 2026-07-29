"""Definiciones canónicas de los roles de usuario de la aplicación."""

ADMIN = 'a'
COMPANY = 'c'
TEACHER = 'p'
STUDENT = 's'

ROLE_NAMES = {
    COMPANY: 'empresa',
    TEACHER: 'profesor',
    STUDENT: 'estudiante',
    ADMIN: 'administrador',
}

ROLE_CHOICES = tuple(ROLE_NAMES.items())
PUBLIC_REGISTRATION_ROLES = (STUDENT, TEACHER, COMPANY)

