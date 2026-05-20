# Calibre Webapp Frontend

Next.js 15 frontend for Calibre library management.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

With `webapp\start.ps1`, open [http://localhost:10721](http://localhost:10721). For Docker, the mapped UI port is **10722** (see `webapp/SETUP.md`).

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:10720
```

## Build

```bash
npm run build
npm start
```
