import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Configuración optimizada para Railway
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  build: {
    outDir: "dist",
    // Asegurar que los assets se generen con rutas absolutas para Railway
    assetsDir: "assets",
    // Configuración específica para Railway
    rollupOptions: {
      input: path.resolve(__dirname, "index.html"),
      output: {
        // Asegurar nombres consistentes para los archivos
        entryFileNames: "assets/[name].[hash].js",
        chunkFileNames: "assets/[name].[hash].js",
        assetFileNames: "assets/[name].[hash].[ext]"
      }
    },
    // Generar sourcemaps para debugging en producción si es necesario
    sourcemap: false,
    // Optimización para Railway
    minify: 'terser',
    target: 'es2020'
  },
  // Configuración de archivos estáticos
  publicDir: "public",
  // Asegurar que las rutas funcionen en Railway
  base: "/",
});
