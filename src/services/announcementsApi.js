import { collection, request } from "./httpClient";

export const getAnnouncements = async () => collection(await request("/Announcement/"));
