import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { tokenStorage } from "../services/api";

export const ProtectedRoute: React.FC = () => {
  const token = tokenStorage.getAccessToken();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
