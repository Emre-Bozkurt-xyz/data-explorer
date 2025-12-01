import { configureStore } from "@reduxjs/toolkit";
import { datasetsApi } from "../features/datasets/datasetsApi";
import { bookmarksApi } from "../features/bookmarks/bookmarksApi";

export const store = configureStore({
  reducer: {
    [datasetsApi.reducerPath]: datasetsApi.reducer,
    [bookmarksApi.reducerPath]: bookmarksApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(datasetsApi.middleware)
      .concat(bookmarksApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
