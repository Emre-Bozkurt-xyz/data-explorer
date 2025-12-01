import { createApi } from "@reduxjs/toolkit/query/react";
import { apiBaseQuery } from "../../app/apiClient";

export interface DatasetSummary {
  id: string;
  name: string;
  description: string;
  row_count: number;
  updated_at: string; // ISO string
}

export interface PaginatedDatasets {
  items: DatasetSummary[];
  page: number;
  limit: number;
  total: number;
}

export interface ListDatasetsArgs {
  search?: string;
  page?: number;
  limit?: number;
}

// NEW: detail + fields
export interface DatasetFieldSummary {
  id: number;
  name: string;
  type: string;
  null_frac: number;
  distinct_count?: number | null;
  example_value?: Record<string, unknown> | null;
}

export interface DatasetDetail extends DatasetSummary {
  fields: DatasetFieldSummary[];
}

// NEW: records
export interface RecordSummary {
  id: number;
  payload: Record<string, unknown>;
}

export interface PaginatedRecords {
  items: RecordSummary[];
  page: number;
  limit: number;
  total: number;
}

export interface ListDatasetRecordsArgs {
  datasetId: string;
  page: number;
  limit: number;
  search?: string;
  sort?: string;
  filter?: string;
}


export const datasetsApi = createApi({
  reducerPath: "datasetsApi",
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    listDatasets: builder.query<PaginatedDatasets, ListDatasetsArgs | void>({
      query: (args) => {
        const params = new URLSearchParams();

        const page = args?.page ?? 1;
        const limit = args?.limit ?? 20;
        if (args?.search) {
          params.set("search", args.search);
        }
        params.set("page", String(page));
        params.set("limit", String(limit));

        return {
          url: `/v1/datasets?${params.toString()}`,
        };
      },
    }),

    // NEW: GET /api/v1/datasets/{id}
    getDataset: builder.query<DatasetDetail, string>({
      query: (id) => `/v1/datasets/${id}`,
    }),

    // NEW: GET /api/v1/datasets/{id}/records
    listDatasetRecords: builder.query<PaginatedRecords, ListDatasetRecordsArgs>({
      query: ({ datasetId, page, limit, search, sort, filter }) => ({
        url: `/v1/datasets/${datasetId}/records`,
        params: {
          page,
          limit,
          search,
          sort,
          filter,
        },
      }),
    }),
  }),
});


export const {
  useListDatasetsQuery,
  useGetDatasetQuery,
  useListDatasetRecordsQuery,
} = datasetsApi;

