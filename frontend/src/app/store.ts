// src/app/store.ts
import { configureStore } from "@reduxjs/toolkit";
import { datasetsApi } from "../features/datasets/datasetsApi";

export const store = configureStore({
  reducer: {
    [datasetsApi.reducerPath]: datasetsApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(datasetsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;