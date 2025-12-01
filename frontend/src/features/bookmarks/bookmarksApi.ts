// src/features/bookmarks/bookmarksApi.ts
import { createApi } from "@reduxjs/toolkit/query/react";
import { apiBaseQuery } from "../../app/apiClient";

export interface Bookmark {
  id: number;
  user_id: string;
  dataset_id: string;
  record_id: number;
  note: string;
  created_at: string;
}

export interface PaginatedBookmarks {
  items: Bookmark[];
  page: number;
  limit: number;
  total: number;
}

export interface ListBookmarksArgs {
  datasetId?: string;
  page?: number;
  limit?: number;
}

export interface BookmarkCreate {
  dataset_id: string;
  record_id: number;
  note?: string;
}

export const bookmarksApi = createApi({
  reducerPath: "bookmarksApi",
  baseQuery: apiBaseQuery,
  tagTypes: ["Bookmarks"],
  endpoints: (builder) => ({
    listBookmarks: builder.query<PaginatedBookmarks, ListBookmarksArgs | void>({
      query: (args) => {
        const params = new URLSearchParams();
        const page = args?.page ?? 1;
        const limit = args?.limit ?? 50;

        params.set("page", String(page));
        params.set("limit", String(limit));

        if (args?.datasetId) {
          params.set("dataset_id", args.datasetId);
        }

        return {
          url: `/v1/bookmarks?${params.toString()}`,
        };
      },
      providesTags: (result) =>
        result
          ? [
              ...result.items.map((b) => ({ type: "Bookmarks" as const, id: b.id })),
              { type: "Bookmarks" as const, id: "LIST" },
            ]
          : [{ type: "Bookmarks" as const, id: "LIST" }],
    }),

    createBookmark: builder.mutation<Bookmark, BookmarkCreate>({
      query: (body) => ({
        url: "/v1/bookmarks",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Bookmarks", id: "LIST" }],
    }),

    deleteBookmark: builder.mutation<void, number>({
      query: (bookmarkId) => ({
        url: `/v1/bookmarks/${bookmarkId}`,
        method: "DELETE",
      }),
      invalidatesTags: [{ type: "Bookmarks", id: "LIST" }],
    }),
  }),
});

export const {
  useListBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,
} = bookmarksApi;
