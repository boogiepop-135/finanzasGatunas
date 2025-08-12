export const initialStore = (backendUrl) => {
  // Establecer la URL del backend, con valor predeterminado '/api' para producción
  const apiUrl = backendUrl || import.meta.env.VITE_BACKEND_URL || "/api";

  return {
    message: null,
    backendUrl: apiUrl, // Guardar la URL del backend en el estado global
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      },
    ],
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    case "set_hello":
      return {
        ...store,
        message: action.payload,
      };

    case "add_task":
      const { id, color } = action.payload;

      return {
        ...store,
        todos: store.todos.map((todo) =>
          todo.id === id ? { ...todo, background: color } : todo
        ),
      };
    default:
      throw Error("Unknown action.");
  }
}
