// src/app/apiClient.ts
import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const apiBaseQuery = fetchBaseQuery({
  baseUrl: "http://localhost:8000/api",
  prepareHeaders: (headers) => {
    // MVP user identity; later this can come from real auth
    headers.set("X-User-Id", "dev-local");
    return headers;
  },
});
