#!/bin/bash
echo "Running Frontend Tests..."

if ! grep -q "vitest" package.json; then
  echo "Installing test dependencies..."
  npm install -D vitest @testing-library/react @testing-library/dom jsdom @testing-library/jest-dom
  
  cat << 'VITE_EOF' > vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
  },
})
VITE_EOF
fi

npx vitest run
