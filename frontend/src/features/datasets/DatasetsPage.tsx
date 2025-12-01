// src/features/datasets/DatasetsPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  TextField,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  CircularProgress,
  TableContainer,
  Pagination,
  Stack,
} from "@mui/material";
import { useListDatasetsQuery } from "./datasetsApi";

const PAGE_SIZE = 10;

export function DatasetsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const { data, isLoading, isError, refetch } = useListDatasetsQuery({
    page,
    limit: PAGE_SIZE,
    search: search || undefined,
  });

  const total = data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Datasets
        </Typography>
        <TextField
          size="small"
          label="Search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
      </Stack>

      {isLoading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Box py={2}>
          <Typography color="error" mb={1}>
            Failed to load datasets.
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
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Rows</TableCell>
                  <TableCell>Updated at</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.items?.length ? (
                  data.items.map((ds) => (
                    <TableRow
                      key={ds.id}
                      hover
                      sx={{ cursor: "pointer" }}
                      onClick={() => navigate(`/datasets/${ds.id}`)}
                    >
                      <TableCell>{ds.name}</TableCell>
                      <TableCell>{ds.description}</TableCell>
                      <TableCell align="right">{ds.row_count}</TableCell>
                      <TableCell>
                        {new Date(ds.updated_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4}>
                      <Typography variant="body2" color="textSecondary">
                        No datasets found.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <Box mt={2} display="flex" justifyContent="flex-end">
            <Pagination
              count={pageCount}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
            />
          </Box>
        </>
      )}
    </Container>
  );
}
