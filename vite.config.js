const { resolve } = require('node:path');
const { defineConfig } = require('vite');

module.exports = defineConfig({
  build: {
    outDir: 'webui/static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: resolve(__dirname, 'webui/static/webui-build-entry.js'),
    },
  },
});
