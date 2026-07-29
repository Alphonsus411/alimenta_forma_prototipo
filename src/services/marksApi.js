import { collection, request } from "./httpClient";

export const getMarks = async () => collection(await request("/mark/"));
