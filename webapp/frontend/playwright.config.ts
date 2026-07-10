import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  retries: 1,
  use: { baseURL: 'http://localhost:10721', headless: true, screenshot: 'only-on-failure' },
  webServer: {
    command: 'uv run python -m calibre_mcp.server --port 10720',
    port: 10720,
    timeout: 30000,
    reuseExistingServer: false,
  },
});
