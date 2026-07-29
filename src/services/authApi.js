const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export class ApiError extends Error {
  constructor(message, fields = {}) {
    super(message);
    this.name = "ApiError";
    this.fields = fields;
  }
}

const getCookie = (name) => {
  const cookie = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split("=").slice(1).join("=")) : "";
};

const request = async (path, options = {}) => {
  const headers = { ...options.headers };
  if (options.body) headers["Content-Type"] = "application/json";
  const csrfToken = getCookie("csrftoken");
  if (csrfToken) headers["X-CSRFToken"] = csrfToken;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  const data = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.detail || data.non_field_errors?.[0] || "No se pudo completar la solicitud.";
    throw new ApiError(message, data);
  }
  return data;
};

export const login = (credentials) => request("/auth/login/", {
  method: "POST",
  body: JSON.stringify(credentials),
});

export const register = (userData) => request("/auth/register/", {
  method: "POST",
  body: JSON.stringify(userData),
});

export const logout = () => request("/auth/logout/", { method: "POST" });
export const getCurrentUser = () => request("/auth/me/");
