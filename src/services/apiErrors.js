const flattenMessages = (value) => {
  if (Array.isArray(value)) return value.flatMap(flattenMessages);
  if (value && typeof value === "object") return Object.values(value).flatMap(flattenMessages);
  return value ? [String(value)] : [];
};

export const backendErrorMessage = (error) => {
  const messages = flattenMessages(error?.data);
  const text = messages.join(" ") || error?.message || "No se pudo completar la operación.";
  const normalized = text.toLowerCase();

  if (error?.status === 403 || normalized.includes("profesor del curso")) {
    return "Curso ajeno: solo puedes gestionar los cursos que tienes asignados.";
  }
  if (normalized.includes("no existe una matrícula") || normalized.includes("no matriculad")) {
    return "Alumno no matriculado: selecciona una matrícula válida del curso.";
  }
  if (normalized.includes("unique") || normalized.includes("único") || normalized.includes("ya existe")) {
    return normalized.includes("asistencia") || error?.operation === "attendance"
      ? "Asistencia duplicada: ya existe un registro para ese alumno y fecha."
      : text;
  }
  if (normalized.includes("10") || normalized.includes("mayor") || normalized.includes("menor")) {
    return "Nota fuera de la escala: introduce valores entre 0 y 10.";
  }
  return text;
};
