import { Outlet, Link, useLocation } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  Stack,
} from "@mui/material";

export function AppLayout() {
  const location = useLocation();

  return (
    <Box sx={{ minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Data Explorer
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              color="inherit"
              component={Link}
              to="/"
              variant={location.pathname === "/" ? "outlined" : "text"}
            >
              Datasets
            </Button>
            <Button
              color="inherit"
              component={Link}
              to="/bookmarks"
              variant={
                location.pathname.startsWith("/bookmarks")
                  ? "outlined"
                  : "text"
              }
            >
              Bookmarks
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
