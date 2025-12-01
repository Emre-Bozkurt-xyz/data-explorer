// src/routes.tsx
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppLayout } from "./shell/AppLayout";
import { DatasetsPage } from "./features/datasets/DatasetsPage";
import { DatasetDetailPage } from "./features/datasets/DatasetDetailPage.tsx";
import { BookmarksPage } from "./features/bookmarks/BookmarksPage.tsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DatasetsPage /> },
      { path: "datasets/:id", element: <DatasetDetailPage /> },
      { path: "bookmarks", element: <BookmarksPage /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
