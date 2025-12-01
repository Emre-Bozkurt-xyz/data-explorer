import { useState } from "react";
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
  Pagination,
  Stack,
} from "@mui/material";

import {
  useGetDatasetQuery,
  useListDatasetRecordsQuery,
} from "./datasetsApi";

const RECORDS_PAGE_SIZE = 25;

export function DatasetDetailPage() {
  const { id } = useParams<{ id: string }>();

  const [recordsPage, setRecordsPage] = useState(1);
  const [recordsSearch, setRecordsSearch] = useState("");

  const {
    data: dataset,
    isLoading: isDatasetLoading,
    isError: isDatasetError,
  } = useGetDatasetQuery(id as string, {
    skip: !id,
  });

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
    },
    {
      skip: !id,
    }
  );

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

  const recordsTotal = records?.total ?? 0;
  const recordsPageCount = Math.max(
    1,
    Math.ceil(recordsTotal / RECORDS_PAGE_SIZE)
  );

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
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={3}>
                        <Typography variant="body2" color="textSecondary">
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
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              mb={2}
            >
              <Typography variant="h6">Records</Typography>
              <TextField
                size="small"
                label="Search payload"
                value={recordsSearch}
                onChange={(e) => {
                  setRecordsSearch(e.target.value);
                  setRecordsPage(1);
                }}
              />
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
              <>
                <Box sx={{ maxHeight: 400, overflow: "auto" }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Payload</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {records?.items?.length ? (
                        records.items.map((r) => (
                          <TableRow key={r.id}>
                            <TableCell>{r.id}</TableCell>
                            <TableCell>
                              <pre
                                style={{
                                  margin: 0,
                                  whiteSpace: "pre-wrap",
                                  wordBreak: "break-word",
                                  fontSize: "0.75rem",
                                }}
                              >
                                {JSON.stringify(r.payload, null, 2)}
                              </pre>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={2}>
                            <Typography
                              variant="body2"
                              color="textSecondary"
                            >
                              No records found.
                            </Typography>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </Box>

                <Box mt={2} display="flex" justifyContent="flex-end">
                  <Pagination
                    count={recordsPageCount}
                    page={recordsPage}
                    onChange={(_, value) => setRecordsPage(value)}
                    color="primary"
                    size="small"
                  />
                </Box>
              </>
            )}
          </Paper>
        </Box>
      </Box>

    </Box>
  );
}
