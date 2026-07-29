import { request } from "./httpClient";

export { HttpError as ApiError } from "./httpClient";

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
