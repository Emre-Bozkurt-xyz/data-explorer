// src/app/apiClient.ts
import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";

// Read from Vite env, with a sane local default
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const apiBaseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers) => {
    // MVP user identity; later this can come from real auth
    headers.set("X-User-Id", "dev-local");
    return headers;
  },
});
