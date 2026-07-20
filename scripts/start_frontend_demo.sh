#!/bin/bash
echo "Starting JobHunterAI Frontend Demo..."

if ! grep -q "react-beautiful-dnd" package.json; then
  echo "Installing missing dependencies (react-beautiful-dnd)..."
  npm install react-beautiful-dnd @types/react-beautiful-dnd
fi

npm ci || npm install

if [ ! -f src/App.bak.tsx ]; then
  cp src/App.tsx src/App.bak.tsx
  cat << 'APP_EOF' > src/App.tsx
import React from 'react';
import { Dashboard } from './pages/Dashboard';
export default function App() { return <Dashboard />; }
APP_EOF
fi

echo "Starting dev server..."
npm run dev
