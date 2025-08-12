import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Configuración simplificada que funciona en la mayoría de entornos
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  build: {
    outDir: "dist",
    // Asegurarse de que los assets se generen con rutas relativas correctas
    assetsDir: "assets",
    // Establecer la base URL como relativa
    base: "./",
    // Configuración explícita para Railway
    rollupOptions: {
      input: path.resolve(__dirname, "index.html"), // Usar index.html como entrada principal
    },
  },
  // Configuración de archivos estáticos
  publicDir: "public",
});
