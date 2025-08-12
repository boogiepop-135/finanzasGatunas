import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'  // Global styles for your application
import { RouterProvider } from "react-router-dom";  // Import RouterProvider to use the router
import { router } from "./routes";  // Import the router configuration
import { StoreProvider } from './hooks/useGlobalReducer';  // Import the StoreProvider for global state management
import { BackendURL } from './components/BackendURL';

const Main = () => {
    // En Railway, definimos un valor predeterminado para asegurar que la aplicación funcione
    const backendUrl = import.meta.env.VITE_BACKEND_URL || '/api';
    console.log('VITE_BACKEND_URL:', backendUrl); // Debugging log

    // Solo mostrar el componente BackendURL en desarrollo cuando no hay URL configurada
    if (!backendUrl && process.env.NODE_ENV !== 'production') return (
        <React.StrictMode>
            <BackendURL />
        </React.StrictMode>
    );

    // Siempre renderizar la aplicación en producción
    return (
        <React.StrictMode>
            {/* Provide global state to all components */}
            <StoreProvider backendUrl={backendUrl}>
                {/* Set up routing for the application */}
                <RouterProvider router={router}>
                </RouterProvider>
            </StoreProvider>
        </React.StrictMode>
    );
}

// Render the Main component into the root DOM element.
ReactDOM.createRoot(document.getElementById('root')).render(<Main />)
