import { collection, request } from "./httpClient";

export const getMemberships = async () => collection(await request("/offer/"));
