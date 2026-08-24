# React/Vite Frontend

TurkDemy includes a separate frontend under:

```text
frontend/
```

It uses:
- React
- TypeScript
- Vite
- ESLint
- nginx for production serving

Development:

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` and `/media` to Django on `127.0.0.1:8000`.

The frontend currently provides a minimal catalogue shell and is intended to
grow independently from the server-rendered Django pages.
