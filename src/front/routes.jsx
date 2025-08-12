// Import necessary components and functions from react-router-dom.

import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";
import { Layout } from "./pages/Layout";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Categories from "./pages/Categories";
import RecurringPayments from "./pages/RecurringPayments";
import Reports from "./pages/Reports";

export const router = createBrowserRouter(
  createRoutesFromElements(
    // Root Route: All navigation will start from here.
    <Route path="/" element={<Layout />} errorElement={
      <div className="content-container text-center">
        <div style={{ fontSize: '4rem' }}>😿</div>
        <h1>¡Miau! Página no encontrada</h1>
        <p>Esta página se escondió como un gato travieso</p>
        <a href="/" className="btn btn-primary">
          🏠 Volver al inicio
        </a>
      </div>
    } >

      {/* Nested Routes: Defines sub-routes within the Layout component. */}
      <Route path="/" element={<Dashboard />} />
      <Route path="/transactions" element={<Transactions />} />
      <Route path="/categories" element={<Categories />} />
      <Route path="/recurring" element={<RecurringPayments />} />
      <Route path="/reports" element={<Reports />} />
    </Route>
  )
);