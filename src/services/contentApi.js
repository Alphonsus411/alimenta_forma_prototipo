import { collection, request } from "./httpClient";

export const getContents = async () => collection(await request("/content/"));

export const getContent = (contentId) => request(`/content/${contentId}/`);
