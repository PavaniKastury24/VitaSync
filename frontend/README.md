# VitaSync Next.js Frontend

The user-facing presentation tier of VitaSync, built with Next.js 15, TypeScript, and Tailwind CSS.

## Features
- **App Router**: Dynamic, performant page routing.
- **TypeScript**: Strict type definitions for lifestyle metrics, logs, and AI recommendations.
- **Tailwind CSS**: Dark-mode-first aesthetic with ergonomic color palettes.
- **Lucide Icons**: Crisp iconography for all 9 wellness categories.
- **Backend API Integration**: Connects seamlessly with the Python FastAPI backend at `/api/v1`.

## Local Development

### 1. Install Dependencies
```powershell
cd frontend
npm.cmd install
```

### 2. Environment Variables
Copy `.env.example` to `.env.local`:
```powershell
cp .env.example .env.local
```

### 3. Run Development Server
```powershell
npm.cmd run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.
