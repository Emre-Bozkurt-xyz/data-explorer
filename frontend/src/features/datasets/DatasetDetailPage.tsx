// src/features/datasets/DatasetDetailPage.tsx

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Box,
  Typography,
  CircularProgress,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Divider,
  TextField,
  Stack,
  IconButton,
  Tooltip,
  Button,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import type {
  GridColDef,
  GridSortModel,
  GridSortDirection,
} from "@mui/x-data-grid";
import BookmarkIcon from "@mui/icons-material/Bookmark";
import BookmarkBorderIcon from "@mui/icons-material/BookmarkBorder";

import {
  useGetDatasetQuery,
  useListDatasetRecordsQuery,
} from "./datasetsApi";
import type { RecordSummary } from "./datasetsApi";

import {
  useListBookmarksQuery,
  useCreateBookmarkMutation,
  useDeleteBookmarkMutation,
} from "../bookmarks/bookmarksApi";
import type { Bookmark } from "../bookmarks/bookmarksApi";

import { useUrlState } from "../../hooks/useUrlState";

const RECORDS_PAGE_SIZE = 25;

// Base URL for direct backend calls (CSV export).
// Set VITE_API_URL in env to something like "http://localhost:8000/api/v1"
const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();

  // URL-backed state for records view
  const [urlState, setUrlState] = useUrlState({
    page: 1,
    search: "",
    filter: "",
    sort: "", // "field:dir", e.g. "id:asc"
  });

  const recordsPage = urlState.page;
  const recordsSearch = urlState.search;
  const filterRaw = urlState.filter;
  const sortParam = urlState.sort || undefined;

  // DataGrid sort model derived from sortParam
  const [sortModel, setSortModel] = useState<GridSortModel>(() => {
    if (!sortParam) return [];
    const [field, dir] = sortParam.split(":");
    return [
      {
        field,
        sort: dir as GridSortDirection,
      },
    ];
  });

  useEffect(() => {
    if (!sortParam) {
      setSortModel([]);
      return;
    }
    const [field, dir] = sortParam.split(":");
    setSortModel([
      {
        field,
        sort: dir as GridSortDirection,
      },
    ]);
  }, [sortParam]);

  const [localBookmarkedIds, setLocalBookmarkedIds] = useState<Set<number>>(
    () => new Set(),
  );

  // Dataset + schema
  const {
    data: dataset,
    isLoading: isDatasetLoading,
    isError: isDatasetError,
  } = useGetDatasetQuery(id as string, {
    skip: !id,
  });

  // Records (server-side pagination + search + sort + filter)
  const {
    data: records,
    isLoading: isRecordsLoading,
    isError: isRecordsError,
    refetch: refetchRecords,
  } = useListDatasetRecordsQuery(
    {
      datasetId: id as string,
      page: recordsPage,
      limit: RECORDS_PAGE_SIZE,
      search: recordsSearch || undefined,
      sort: sortParam,
      filter: filterRaw || undefined,
    },
    {
      skip: !id,
    },
  );

  const recordsTotal = records?.total ?? 0;

  // Bookmarks – load ALL and filter client-side by dataset
  const { data: bookmarksData } = useListBookmarksQuery(undefined);
  const [createBookmark] = useCreateBookmarkMutation();
  const [deleteBookmark] = useDeleteBookmarkMutation();

  // Map record_id -> Bookmark (only for this dataset)
  const bookmarkByRecordId = new Map<number, Bookmark>();
  if (bookmarksData && id) {
    bookmarksData.items.forEach((b) => {
      if (b.dataset_id === id) {
        bookmarkByRecordId.set(b.record_id, b);
      }
    });
  }

  // Sync local set from server whenever bookmarks change
  useEffect(() => {
    if (!bookmarksData || !id) return;
    setLocalBookmarkedIds(
      new Set(
        bookmarksData.items
          .filter((b) => b.dataset_id === id)
          .map((b) => b.record_id),
      ),
    );
  }, [bookmarksData, id]);

  if (!id) {
    return (
      <Typography color="error">
        Missing dataset id in route.
      </Typography>
    );
  }

  if (isDatasetLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (isDatasetError || !dataset) {
    return (
      <Box>
        <Typography variant="h5" color="error" gutterBottom>
          Failed to load dataset.
        </Typography>
        <Typography variant="body2">
          Check the URL or try again later.
        </Typography>
      </Box>
    );
  }

  // Toggle bookmark for a given record id (optimistic)
  const handleToggleBookmark = async (recordId: number) => {
    if (!id) return;

    const existing = bookmarkByRecordId.get(recordId);
    const isBookmarked = localBookmarkedIds.has(recordId);

    if (isBookmarked) {
      // Optimistic un-bookmark
      setLocalBookmarkedIds((prev) => {
        const next = new Set(prev);
        next.delete(recordId);
        return next;
      });
      if (existing) {
        try {
          await deleteBookmark(existing.id).unwrap();
        } catch {
          // Revert on error
          setLocalBookmarkedIds((prev) => {
            const next = new Set(prev);
            next.add(recordId);
            return next;
          });
        }
      }
    } else {
      // Optimistic bookmark
      setLocalBookmarkedIds((prev) => {
        const next = new Set(prev);
        next.add(recordId);
        return next;
      });
      try {
        await createBookmark({
          dataset_id: id,
          record_id: recordId,
          note: "",
        }).unwrap();
      } catch {
        // Revert on error
        setLocalBookmarkedIds((prev) => {
          const next = new Set(prev);
          next.delete(recordId);
          return next;
        });
      }
    }
  };

  const handleExportCsv = () => {
    if (!id) return;

    const params = new URLSearchParams();
    params.set("page", recordsPage.toString());
    params.set("limit", RECORDS_PAGE_SIZE.toString());
    if (recordsSearch) params.set("search", recordsSearch);
    if (sortParam) params.set("sort", sortParam);
    if (filterRaw) params.set("filter", filterRaw);

    const url = `${API_BASE_URL}/datasets/${id}/records/export?${params.toString()}`;
    window.location.href = url;
  };

  // DataGrid columns
  const columns: GridColDef[] = [
    {
      field: "id",
      headerName: "ID",
      width: 80,
      sortable: true,
    },
    {
      field: "payload",
      headerName: "Payload",
      flex: 1,
      sortable: false,
      renderCell: (params) => (
        <pre
          style={{
            margin: 0,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            fontSize: "0.75rem",
          }}
        >
          {JSON.stringify(params.value, null, 2)}
        </pre>
      ),
    },
    {
      field: "bookmark",
      headerName: "",
      width: 80,
      sortable: false,
      filterable: false,
      renderCell: (params) => {
        const row = params.row as RecordSummary;
        const recordId = row.id;
        const isBookmarked = localBookmarkedIds.has(recordId);

        return (
          <Tooltip
            title={isBookmarked ? "Remove bookmark" : "Add bookmark"}
          >
            <IconButton
              size="small"
              onClick={() => handleToggleBookmark(recordId)}
              color={isBookmarked ? "primary" : "default"}
            >
              {isBookmarked ? (
                <BookmarkIcon fontSize="small" />
              ) : (
                <BookmarkBorderIcon fontSize="small" />
              )}
            </IconButton>
          </Tooltip>
        );
      },
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          {dataset.name}
        </Typography>
        <Typography variant="body1" gutterBottom>
          {dataset.description || "No description"}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Rows: {dataset.row_count.toLocaleString()} • Updated:{" "}
          {new Date(dataset.updated_at).toLocaleString()}
        </Typography>
      </Box>

      <Box
        sx={{
          display: "flex",
          flexDirection: { xs: "column", md: "row" },
          gap: 3,
        }}
      >
        {/* Schema panel */}
        <Box sx={{ flexBasis: { md: "33%" }, flexGrow: 1 }}>
          <Paper sx={{ p: 2, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              Schema
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Field types, null %, distinct counts, example values.
            </Typography>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ maxHeight: 400, overflow: "auto" }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Null %</TableCell>
                    <TableCell align="right">Distinct</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dataset.fields.length ? (
                    dataset.fields.map((f) => (
                      <TableRow key={f.id}>
                        <TableCell>{f.name}</TableCell>
                        <TableCell>{f.type}</TableCell>
                        <TableCell align="right">
                          {(f.null_frac * 100).toFixed(1)}%
                        </TableCell>
                        <TableCell align="right">
                          {f.distinct_count ?? "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4}>
                        <Typography
                          variant="body2"
                          color="textSecondary"
                        >
                          No schema information yet.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </Box>
          </Paper>
        </Box>

        {/* Records panel */}
        <Box sx={{ flexBasis: { md: "67%" }, flexGrow: 1 }}>
          <Paper sx={{ p: 2 }}>
            <Stack
              direction={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", sm: "center" }}
              spacing={1}
              mb={2}
            >
              <Typography variant="h6">Records</Typography>

              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={1}
                alignItems={{ xs: "stretch", sm: "center" }}
                sx={{ width: { xs: "100%", sm: "auto" } }}
              >
                <TextField
                  size="small"
                  label="Search payload"
                  value={recordsSearch}
                  onChange={(e) => {
                    setUrlState({ search: e.target.value, page: 1 });
                  }}
                />
                <TextField
                  size="small"
                  label="Filter (e.g. length:gt:1000)"
                  value={filterRaw}
                  onChange={(e) => {
                    setUrlState({ filter: e.target.value, page: 1 });
                  }}
                />
                <Button
                  size="small"
                  variant="outlined"
                  onClick={handleExportCsv}
                >
                  Export CSV
                </Button>
              </Stack>
            </Stack>

            {isRecordsLoading && (
              <Box display="flex" justifyContent="center" py={3}>
                <CircularProgress size={24} />
              </Box>
            )}

            {isRecordsError && (
              <Box py={2}>
                <Typography color="error" mb={1}>
                  Failed to load records.
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    cursor: "pointer",
                    textDecoration: "underline",
                  }}
                  onClick={() => refetchRecords()}
                >
                  Retry
                </Typography>
              </Box>
            )}

            {!isRecordsLoading && !isRecordsError && (
              <Box
                sx={{
                  height: 500,
                  width: "100%",
                  "& .MuiDataGrid-cell": {
                    alignItems: "flex-start",
                    py: 1,
                  },
                }}
              >
                <DataGrid
                  rows={records?.items ?? []}
                  getRowId={(row) => row.id}
                  columns={columns}
                  paginationMode="server"
                  rowCount={recordsTotal}
                  pageSizeOptions={[RECORDS_PAGE_SIZE]}
                  paginationModel={{
                    page: recordsPage - 1, // DataGrid is 0-based
                    pageSize: RECORDS_PAGE_SIZE,
                  }}
                  onPaginationModelChange={(model) => {
                    setUrlState({ page: model.page + 1 });
                  }}
                  sortingMode="server"
                  sortModel={sortModel}
                  onSortModelChange={(model) => {
                    setSortModel(model);
                    const first = model[0];
                    const newSort =
                      first && first.sort
                        ? `${first.field}:${first.sort}`
                        : "";
                    setUrlState({ sort: newSort, page: 1 });
                  }}
                  loading={isRecordsLoading}
                  disableRowSelectionOnClick
                  getRowHeight={() => "auto"}
                />
              </Box>
            )}
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
