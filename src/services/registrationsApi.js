import { collection, request } from "./httpClient";

export const getRegistrations = async () => collection(await request("/registration/"));

export const registerForCourse = (courseId) => request("/registration/", {
  method: "POST",
  body: JSON.stringify({ course: Number(courseId) }),
});

export const getCourseRegistrations = async (courseId) => (
  (await getRegistrations()).filter((registration) => registration.course === Number(courseId))
);
