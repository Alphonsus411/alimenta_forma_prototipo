import { collection, request } from "./httpClient";
import { getCurrentUser } from "./authApi";

export const getProfile = async () => {
  const [user, profiles] = await Promise.all([
    getCurrentUser(),
    request("/profile/").then(collection),
  ]);
  return { user, profile: profiles[0] || null };
};

export const updateProfile = (id, values) => request(`/profile/${id}/`, {
  method: "PATCH",
  body: JSON.stringify(values),
});
