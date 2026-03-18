# Stock y Facturación Multiplataforma

Monorepo: Frontend (React + Vite + Tailwind) y Backend (FastAPI + PostgreSQL).

## Estructura

- `backend/` — API FastAPI, modelos SQLAlchemy, esquemas separados (auth, stock, facturación)
- `frontend/` — SPA React con componentes por módulo (Auth, Stock, Factura)

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

## Desarrollo

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Base de datos

PostgreSQL con tres esquemas:

- **auth**: usuarios y sesiones (separado del negocio)
- **stock**: productos e inventario (`stock_items`: id, sku, nombre, cantidad, precio_base)
- **invoicing**: facturas y configuración de impuestos (Strategy por país)

Levantar PostgreSQL con Docker:

```bash
docker compose up -d
```

Luego en `backend`: copiar `.env.example` a `.env` y ejecutar la API. En el arranque se crean esquemas, tablas y el seed de impuestos (Chile 19%, Argentina con estructura para múltiples alícuotas y percepciones).
