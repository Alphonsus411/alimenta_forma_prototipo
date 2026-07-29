import { collection, request } from "./httpClient";

export const getCourses = async () => collection(await request("/course/"));
