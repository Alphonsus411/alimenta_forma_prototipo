import { describe, expect, it } from "vitest";
import { backendErrorMessage } from "../../src/services/apiErrors";

describe("errores de dominio del panel docente", () => {
  it.each([
    [{ data: { non_field_errors: ["No existe una matrícula del alumno para este curso."] } }, "Alumno no matriculado"],
    [{ data: { non_field_errors: ["Los campos course, student, date deben formar un conjunto único." ] }, operation: "attendance" }, "Asistencia duplicada"],
    [{ data: { mark_1: ["Asegúrese de que este valor sea menor o igual a 10."] } }, "Nota fuera de la escala"],
    [{ status: 403, data: { detail: "Solo el profesor del curso puede gestionar este registro." } }, "Curso ajeno"],
  ])("traduce %o a un mensaje accionable", (error, expected) => {
    expect(backendErrorMessage(error)).toContain(expected);
  });
});
