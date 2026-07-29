import { collection, request } from "./httpClient";

export const getAttendance = async () => collection(await request("/attendance/"));
