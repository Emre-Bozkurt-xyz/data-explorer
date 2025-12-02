import { useState, useMemo } from "react";
import {
  Box,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  CircularProgress,
  Pagination,
  IconButton,
  Tooltip,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import {
  useListBookmarksQuery,
  useDeleteBookmarkMutation,
} from "./bookmarksApi";
import DeleteIcon from "@mui/icons-material/Delete";
import { useListDatasetsQuery } from "../datasets/datasetsApi";

const PAGE_SIZE = 20;

export function BookmarksPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, refetch } = useListBookmarksQuery({
    page,
    limit: PAGE_SIZE,
  });
  const [deleteBookmark] = useDeleteBookmarkMutation();
  const navigate = useNavigate();

  const total = data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const { data: datasetsData } = useListDatasetsQuery({ page: 1, limit: 100 });
  const datasetNameById = useMemo(() => {
    const map = new Map<string, string>();
    datasetsData?.items.forEach((ds) => map.set(ds.id, ds.name));
    return map;
  }, [datasetsData]);


  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Bookmarks
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Records you’ve bookmarked across datasets.
      </Typography>

      {isLoading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Box py={2}>
          <Typography color="error" mb={1}>
            Failed to load bookmarks.
          </Typography>
          <Typography
            variant="body2"
            sx={{ cursor: "pointer", textDecoration: "underline" }}
            onClick={() => refetch()}
          >
            Retry
          </Typography>
        </Box>
      )}

      {!isLoading && !isError && (
        <>
          <Paper sx={{ mt: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Dataset</TableCell>
                  <TableCell>Record ID</TableCell>
                  <TableCell>Note</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.items?.length ? (
                  data.items.map((b) => (
                    <TableRow key={b.id}>
                      <TableCell>{datasetNameById.get(b.dataset_id) ?? b.dataset_id}</TableCell>
                      <TableCell
                        sx={{ cursor: "pointer", color: "primary.main", textDecoration: "underline" }}
                        onClick={() => navigate(`/datasets/${b.dataset_id}`)}
                      >
                        {b.record_id}
                      </TableCell>
                      <TableCell>{b.note}</TableCell>
                      <TableCell>
                        {new Date(b.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="Delete bookmark">
                          <IconButton
                            size="small"
                            onClick={() => deleteBookmark(b.id)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5}>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                      >
                        No bookmarks yet.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Paper>

          <Box mt={2} display="flex" justifyContent="flex-end">
            <Pagination
              count={pageCount}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
              size="small"
            />
          </Box>
        </>
      )}
    </Box>
  );
}
