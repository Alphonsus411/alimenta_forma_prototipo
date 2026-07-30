import { collection, request } from "./httpClient";

export const getAttendance = async () => collection(await request("/attendance/"));

export const createAttendance = (attendance) => request("/attendance/", {
  method: "POST",
  body: JSON.stringify(attendance),
});

export const updateAttendance = (attendanceId, attendance) => request(`/attendance/${attendanceId}/`, {
  method: "PATCH",
  body: JSON.stringify(attendance),
});
