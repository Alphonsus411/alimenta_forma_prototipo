import { collection, request } from "./httpClient";

export const getMarks = async () => collection(await request("/mark/"));

export const createMark = (mark) => request("/mark/", {
  method: "POST",
  body: JSON.stringify(mark),
});

export const updateMark = (markId, mark) => request(`/mark/${markId}/`, {
  method: "PATCH",
  body: JSON.stringify(mark),
});
