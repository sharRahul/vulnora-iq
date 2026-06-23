const { defineConfig } = require('vite');

module.exports = defineConfig({
  root: 'webui/static',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: 'index.html',
    },
  },
});
