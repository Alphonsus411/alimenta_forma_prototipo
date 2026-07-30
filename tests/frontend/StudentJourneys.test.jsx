import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import App from "../../src/App";

const response = (data, { ok = true, status = 200 } = {}) => Promise.resolve({
  ok, status, json: () => Promise.resolve(data),
});

const course = { id: 3, title: "Panadería", detail: "Masas, fermentos y horneado.", classes: 8, teacher: 4, teacher_name: "Ada", status: "d", status_display: "Desarrollo", content: 9 };
const user = { id: 7, username: "leo", first_name: "Leo", category: "s" };
const renderRoute = (route) => render(<MemoryRouter initialEntries={[route]}><App /></MemoryRouter>);

describe("recorridos del alumno", () => {
  beforeEach(() => vi.stubGlobal("fetch", vi.fn()));
  afterEach(() => vi.unstubAllGlobals());

  it("enlaza el catálogo con una ficha que expone los datos del curso", async () => {
    fetch.mockReturnValueOnce(response([course])).mockReturnValueOnce(response(course));
    const interaction = userEvent.setup();
    renderRoute("/courses");

    await interaction.click(await screen.findByRole("link", { name: "Ver detalle de Panadería" }));

    expect(await screen.findByRole("heading", { name: "Panadería", level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/Masas, fermentos y horneado/)).toBeInTheDocument();
    expect(screen.getByText("Profesor: Ada")).toBeInTheDocument();
    expect(screen.getByText("Número de clases: 8")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Matricularme" })).toHaveAttribute("href", "/courses/3/registration");
  });

  it("permite confirmar una matrícula satisfactoria", async () => {
    fetch.mockReturnValueOnce(response(user)).mockReturnValueOnce(response(course)).mockReturnValueOnce(response({ id: 12, course: 3, student: 7 }, { status: 201 }));
    const interaction = userEvent.setup();
    renderRoute("/courses/3/registration");

    await interaction.click(await screen.findByRole("button", { name: "Confirmar matrícula" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Matrícula realizada correctamente");
    expect(fetch).toHaveBeenLastCalledWith("/api/v1/registration/", expect.objectContaining({ method: "POST", body: '{"course":3}' }));
  });

  it("presenta la matrícula duplicada como estado esperado", async () => {
    fetch.mockReturnValueOnce(response(user)).mockReturnValueOnce(response(course)).mockReturnValueOnce(response({ course: ["Ya existe una matrícula de este estudiante para el curso."] }, { ok: false, status: 400 }));
    const interaction = userEvent.setup();
    renderRoute("/courses/3/registration");

    await interaction.click(await screen.findByRole("button", { name: "Confirmar matrícula" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Ya estás matriculado");
  });

  it("protege la matrícula frente a un usuario anónimo", async () => {
    fetch.mockReturnValue(response({ detail: "Las credenciales de autenticación no se proveyeron." }, { ok: false, status: 403 }));
    renderRoute("/courses/3/registration");

    expect(await screen.findByRole("alert")).toHaveTextContent("Debes iniciar sesión");
    expect(screen.getByRole("link", { name: "Iniciar sesión" })).toHaveAttribute("href", "/login");
    expect(screen.queryByRole("button", { name: "Confirmar matrícula" })).not.toBeInTheDocument();
  });

  it.each([
    ["p", "profesor"],
    ["c", "empresa"],
    ["a", "administración"],
  ])("oculta la matrícula individual al rol %s (%s)", async (category) => {
    fetch.mockReturnValueOnce(response({ ...user, category })).mockReturnValueOnce(response(course));
    renderRoute("/courses/3/registration");

    expect(await screen.findByRole("alert")).toHaveTextContent("únicamente para el rol alumno");
    expect(screen.queryByRole("button", { name: "Confirmar matrícula" })).not.toBeInTheDocument();
  });

  it("explica un error HTTP al intentar confirmar la matrícula", async () => {
    fetch.mockReturnValueOnce(response(user)).mockReturnValueOnce(response(course)).mockReturnValueOnce(
      response({ detail: "El servicio de matrículas no está disponible." }, { ok: false, status: 503 }),
    );
    const interaction = userEvent.setup();
    renderRoute("/courses/3/registration");

    await interaction.click(await screen.findByRole("button", { name: "Confirmar matrícula" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El servicio de matrículas no está disponible");
  });

  it("consulta y resume el progreso académico del alumno", async () => {
    fetch.mockImplementation((url) => {
      const payloads = {
        "/api/v1/auth/me/": user,
        "/api/v1/registration/": [{ id: 12, course: 3, student: 7, enabled: true }],
        "/api/v1/course/": [course],
        "/api/v1/content/": [{ id: 9, title: "Unidad 1", comment: "Introducción" }],
        "/api/v1/attendance/": [{ id: 1, course: 3, present: true }, { id: 2, course: 3, present: false }],
        "/api/v1/mark/": [{ id: 2, course: 3, mark_1: 8, mark_2: 9, mark_3: null, average: "8.5" }],
      };
      return response(payloads[url]);
    });
    renderRoute("/student");

    expect(await screen.findByRole("heading", { name: "Panadería", level: 3 })).toBeInTheDocument();
    expect(screen.getByText("Contenidos disponibles: Unidad 1")).toBeInTheDocument();
    expect(screen.getByText("Asistencia: 50%")).toBeInTheDocument();
    expect(screen.getByText("Regularidad: Regular")).toBeInTheDocument();
    expect(screen.getByText("Notas: 8, 9")).toBeInTheDocument();
    expect(screen.getByText("Promedio: 8.5")).toBeInTheDocument();
    expect(screen.getByText("Finalización: En curso")).toBeInTheDocument();
  });

  it("rechaza el acceso al aula de un curso ajeno", async () => {
    fetch.mockReturnValueOnce(response(user)).mockReturnValueOnce(response(course)).mockReturnValueOnce(response([]));
    renderRoute("/courses/3/classroom");

    expect(await screen.findByRole("alert")).toHaveTextContent("No tienes permisos para acceder al aula");
  });
});
