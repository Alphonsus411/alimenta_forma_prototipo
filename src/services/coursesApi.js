import { collection, request } from "./httpClient";

export const getCourses = async () => collection(await request("/course/"));

export const getCourse = (courseId) => request(`/course/${courseId}/`);
