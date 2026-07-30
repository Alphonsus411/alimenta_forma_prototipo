import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import App from "../../src/App";
import Courses from "../../src/routes/Courses";

const response = (data, { ok = true, status = 200 } = {}) => Promise.resolve({
  ok,
  status,
  json: () => Promise.resolve(data),
});

const renderRoute = (component) => render(
  <MemoryRouter>{component}</MemoryRouter>,
);

describe("rutas conectadas con la API", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => vi.unstubAllGlobals());

  it("muestra carga y representa una colección de cursos", async () => {
    fetch.mockReturnValue(response([{
      id: 1,
      title: "Cocina de temporada",
      detail: "Técnicas y productos locales.",
      classes: 6,
      teacher: 7,
      status: "i",
    }]));

    renderRoute(<Courses />);

    expect(screen.getByRole("status")).toHaveTextContent("Cargando");
    expect(await screen.findByRole("heading", { name: "Cocina de temporada" })).toBeInTheDocument();
    expect(screen.getByText("Técnicas y productos locales.")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/v1/course/", expect.objectContaining({ credentials: "include" }));
  });

  it("informa una colección vacía sin inventar cursos", async () => {
    fetch.mockReturnValue(response([]));

    renderRoute(<Courses />);

    expect(await screen.findByText("No hay cursos disponibles.")).toHaveAttribute("role", "status");
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
  });

  it("muestra el error HTTP y permite reintentar", async () => {
    fetch
      .mockReturnValueOnce(response({ detail: "Servicio temporalmente no disponible." }, { ok: false, status: 503 }))
      .mockReturnValueOnce(response([]));
    const user = userEvent.setup();

    renderRoute(<Courses />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Servicio temporalmente no disponible");
    await user.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(await screen.findByText("No hay cursos disponibles.")).toHaveAttribute("role", "status");
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("carga al usuario autenticado y actualiza su perfil", async () => {
    fetch
      .mockReturnValueOnce(response({
        id: 4,
        username: "ana",
        email: "ana@example.com",
        first_name: "Ana",
        last_name: "López",
        category: "s",
      }))
      .mockReturnValueOnce(response([{
        id: 9,
        location: "Rosario",
        phone: "111",
        description: "Estudiante",
        image: "/media/defaultUser.png",
        cv: null,
        userType: 1,
        user: 4,
      }]))
      .mockReturnValueOnce(response({
        id: 9,
        location: "Córdoba",
        phone: "111",
        description: "Estudiante",
        image: "/media/defaultUser.png",
        cv: null,
        userType: 1,
        user: 4,
      }));
    const user = userEvent.setup();

    render(<MemoryRouter initialEntries={["/profile"]}><App /></MemoryRouter>);

    expect(await screen.findByRole("heading", { name: "Ana López" })).toBeInTheDocument();
    const location = screen.getByLabelText("Ciudad");
    await user.clear(location);
    await user.type(location, "Córdoba");
    await user.click(screen.getByRole("button", { name: "Guardar perfil" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Perfil actualizado");
    expect(fetch).toHaveBeenLastCalledWith("/api/v1/profile/9/", expect.objectContaining({
      method: "PATCH",
      body: expect.stringContaining('"location":"Córdoba"'),
    }));
    await waitFor(() => expect(screen.getByLabelText("Ciudad")).toHaveValue("Córdoba"));
  });

  it("cierra la sesión desde el perfil y devuelve al formulario de acceso", async () => {
    fetch.mockImplementation((url, options = {}) => {
      if (url === "/api/v1/auth/me/") return response({
        id: 4, username: "ana", email: "ana@example.com", first_name: "Ana", last_name: "López", category: "s",
      });
      if (url === "/api/v1/profile/") return response([{
        id: 9, location: "Rosario", phone: "111", description: "Estudiante", userType: 1, user: 4,
      }]);
      if (url === "/api/v1/auth/logout/" && options.method === "POST") return response(null, { status: 204 });
      throw new Error(`Petición inesperada: ${url}`);
    });
    const user = userEvent.setup();

    render(<MemoryRouter initialEntries={["/profile"]}><App /></MemoryRouter>);
    await user.click(await screen.findByRole("button", { name: "Cerrar sesión" }));

    expect(await screen.findByRole("heading", { name: "Inicio de Sesión" })).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/v1/auth/logout/", expect.objectContaining({ method: "POST" }));
  });
});
