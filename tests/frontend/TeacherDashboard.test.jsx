import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import App from "../../src/App";

const response = (data, { ok = true, status = 200 } = {}) => Promise.resolve({ ok, status, json: () => Promise.resolve(data) });
const teacher = { id: 4, username: "ada", category: "p" };
const course = { id: 3, title: "Panadería", detail: "Masas", classes: 4, status: "d", teacher: 4 };
const registration = { id: 8, course: 3, student: 7, student_username: "Leo", enabled: true };

const payloads = (overrides = {}) => ({
  "/api/v1/auth/me/": teacher, "/api/v1/course/": [course], "/api/v1/registration/": [registration],
  "/api/v1/attendance/": [], "/api/v1/mark/": [], ...overrides,
});
const mockApi = (overrides) => {
  const data = payloads(overrides);
  fetch.mockImplementation((url, options = {}) => {
    if (options.method) return response({ id: 20, ...JSON.parse(options.body || "{}") }, { status: options.method === "POST" ? 201 : 200 });
    return response(data[url]);
  });
};
const renderPanel = () => render(<MemoryRouter initialEntries={["/teacher"]}><App /></MemoryRouter>);

describe("panel docente", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it("restringe el panel cuando la sesión no tiene rol docente", async () => {
    fetch.mockReturnValue(response({ id: 7, username: "leo", category: "s" })); renderPanel();
    expect(await screen.findByRole("alert")).toHaveTextContent("únicamente para el rol docente");
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("button", { name: "Crear curso" })).not.toBeInTheDocument();
  });

  it("crea y edita únicamente un curso propio", async () => {
    mockApi(); const user = userEvent.setup(); renderPanel();
    await user.type(await screen.findByLabelText("Título"), "Cocina saludable");
    await user.type(screen.getByLabelText("Descripción"), "Técnicas prácticas");
    await user.click(screen.getByRole("button", { name: "Crear curso" }));
    expect(fetch).toHaveBeenCalledWith("/api/v1/course/", expect.objectContaining({ method: "POST", body: expect.stringContaining("Cocina saludable") }));
    await user.click(await screen.findByRole("button", { name: "Editar" }));
    await user.clear(screen.getByLabelText("Título")); await user.type(screen.getByLabelText("Título"), "Panadería avanzada");
    await user.click(screen.getByRole("button", { name: "Guardar curso" }));
    expect(fetch).toHaveBeenCalledWith("/api/v1/course/3/", expect.objectContaining({ method: "PATCH", body: expect.stringContaining("Panadería avanzada") }));
  });

  it("representa explícitamente el rechazo de un curso ajeno", async () => {
    mockApi(); fetch.mockImplementationOnce(() => response(teacher));
    const original = fetch.getMockImplementation();
    fetch.mockImplementation((url, options = {}) => options.method === "PATCH"
      ? response({ detail: "Solo el profesor del curso puede gestionar este registro." }, { ok: false, status: 403 })
      : original(url, options));
    const user = userEvent.setup(); renderPanel(); await user.click(await screen.findByRole("button", { name: "Editar" }));
    await user.click(screen.getByRole("button", { name: "Guardar curso" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Curso ajeno");
  });

  it("consulta matrículas, registra asistencia y permite corregirla", async () => {
    mockApi({ "/api/v1/attendance/": [{ id: 11, course: 3, student: 7, student_username: "Leo", date: "2026-07-29", present: false }] });
    const user = userEvent.setup(); renderPanel(); await user.click(await screen.findByRole("button", { name: "Gestionar alumnado" }));
    expect(screen.getAllByRole("cell", { name: "Leo" })).not.toHaveLength(0);
    await user.selectOptions(screen.getByLabelText("Alumno"), "7"); await user.type(screen.getByLabelText("Fecha"), "2026-07-30");
    await user.click(screen.getByRole("button", { name: "Registrar asistencia" }));
    expect(fetch).toHaveBeenCalledWith("/api/v1/attendance/", expect.objectContaining({ method: "POST", body: expect.stringContaining('"student":7') }));
    await user.click(await screen.findByRole("button", { name: "Marcar presencia" }));
    expect(fetch).toHaveBeenCalledWith("/api/v1/attendance/11/", expect.objectContaining({ method: "PATCH", body: '{"present":true}' }));
  });

  it("recalcula visualmente el promedio antes de guardar las calificaciones", async () => {
    mockApi(); const user = userEvent.setup(); renderPanel(); await user.click(await screen.findByRole("button", { name: "Gestionar alumnado" }));
    const marks = screen.getByRole("heading", { name: "Calificaciones" }).closest("section");
    await user.type(within(marks).getByLabelText("Nota 1 de Leo"), "8"); await user.type(within(marks).getByLabelText("Nota 2 de Leo"), "10");
    expect(within(marks).getByLabelText("Promedio provisional")).toHaveTextContent("9.0");
    await user.click(within(marks).getByRole("button", { name: "Guardar notas" }));
    expect(fetch).toHaveBeenCalledWith("/api/v1/mark/", expect.objectContaining({ method: "POST", body: expect.stringContaining('"mark_1":8') }));
  });
});
