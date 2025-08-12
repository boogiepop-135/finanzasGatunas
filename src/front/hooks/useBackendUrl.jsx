import useGlobalReducer from "./useGlobalReducer";

/**
 * Hook personalizado para obtener la URL del backend
 * Siempre devuelve una URL válida, usando '/api' como fallback
 */
export const useBackendUrl = () => {
    const { store } = useGlobalReducer();
    return store.backendUrl || '/api';
};

/**
 * Función utilitaria para crear una URL completa del API
 * @param {string} endpoint - El endpoint a llamar (ej: '/dashboard/summary')
 * @returns {string} URL completa del API
 */
export const useApiUrl = () => {
    const backendUrl = useBackendUrl();

    return (endpoint) => {
        // Asegurar que el endpoint comience con /
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return `${backendUrl}${cleanEndpoint}`;
    };
};
