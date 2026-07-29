const DEFAULT_API_BASE_URL = "/api/v1";

const normalizeBaseUrl = (url) => url.replace(/\/$/, "");

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL,
);

export class HttpError extends Error {
  constructor(message, { status = 0, data = null } = {}) {
    super(message);
    this.name = "HttpError";
    this.status = status;
    this.data = data;
    this.fields = data && typeof data === "object" ? data : {};
  }
}

const getCookie = (name) => {
  const cookie = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split("=").slice(1).join("=")) : "";
};

const errorMessage = (data) => (
  data?.detail
  || data?.non_field_errors?.[0]
  || "No se pudo completar la solicitud."
);

export const request = async (path, options = {}) => {
  const headers = { Accept: "application/json", ...options.headers };
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const csrfToken = getCookie("csrftoken");
  if (csrfToken) headers["X-CSRFToken"] = csrfToken;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      credentials: "include",
    });
  } catch (error) {
    const connectionError = new HttpError("No se pudo conectar con el servidor.");
    connectionError.cause = error;
    throw connectionError;
  }

  const data = response.status === 204
    ? null
    : await response.json().catch(() => null);
  if (!response.ok) {
    throw new HttpError(errorMessage(data), { status: response.status, data });
  }
  return data;
};

export const collection = (data) => (Array.isArray(data) ? data : data?.results || []);
