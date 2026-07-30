import { collection, request } from "./httpClient";

export const getCourses = async () => collection(await request("/course/"));

export const getCourse = (courseId) => request(`/course/${courseId}/`);

export const createCourse = (course) => request("/course/", {
  method: "POST",
  body: JSON.stringify(course),
});

export const updateCourse = (courseId, course) => request(`/course/${courseId}/`, {
  method: "PATCH",
  body: JSON.stringify(course),
});
