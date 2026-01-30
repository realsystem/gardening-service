# Frontend Architecture

## Overview

The UI is a minimal React + TypeScript SPA built with Vite. It communicates with the backend REST API over HTTP.

## Architecture Decisions

### 1. **Separate Container**
- **Why**: Decouples frontend from backend, allows independent scaling
- **How**: Frontend runs in nginx container, backend in Python container
- **Trade-off**: Additional network hop, but cleaner separation of concerns

### 2. **No State Persistence**
- **Why**: Simplicity, security (JWT in memory only)
- **How**: User must re-login on page refresh
- **Trade-off**: UX inconvenience, but avoids localStorage/cookie security concerns

### 3. **Fetch API (No Axios)**
- **Why**: Reduce dependencies, use native browser API
- **How**: Centralized `api.ts` service with typed responses
- **Trade-off**: Less convenient than Axios, but minimal and auditable

### 4. **Plain CSS (No Tailwind)**
- **Why**: Zero build overhead, explicit styling
- **How**: Single `App.css` with semantic class names
- **Trade-off**: More verbose, but clearer and no framework lock-in

### 5. **Runtime Environment Variables**
- **Why**: Single build works across environments
- **How**: Vite exposes `VITE_API_URL` at build time
- **Trade-off**: Requires rebuild for URL changes, but acceptable for MVP

### 6. **Static Build with Nginx**
- **Why**: Production-ready, minimal resource usage
- **How**: Multi-stage Docker build → nginx serves static files
- **Trade-off**: No SSR, but not needed for this use case

## Component Structure

```
src/
├── components/
│   ├── Auth.tsx              # Login/Register form
│   ├── Dashboard.tsx         # Main application view
│   ├── TaskList.tsx          # Task display component
│   ├── CreateSeedBatch.tsx   # Modal for seed batch creation
│   └── CreatePlantingEvent.tsx  # Modal for planting event creation
├── services/
│   └── api.ts                # Centralized API client
├── types/
│   └── index.ts              # TypeScript interfaces
├── App.tsx                   # Root component
└── main.tsx                  # Entry point
```

## API Client Design

The `api.ts` service:
- Stores JWT in memory (class property)
- Attaches `Authorization: Bearer <token>` to all requests
- Throws errors with user-friendly messages
- Typed responses using TypeScript interfaces

```typescript
class ApiClient {
  private token: string | null = null;

  setToken(token: string) { ... }
  clearToken() { ... }

  private async request<T>(...) { ... }

  async login(...) { ... }
  async getTasks(...) { ... }
}
```

## State Management

**No Redux** - Component-level state with `useState`:
- Auth state: JWT token (in-memory)
- User state: Current user object
- Task state: Task list
- Loading/error states: Per-component

**Why**: Simple data flow, minimal complexity for MVP.

## Error Handling

- API errors bubble up from `api.request()`
- Components catch and display inline error messages
- No global error boundary (not needed for MVP)
- Loading states shown during async operations

## Testing Strategy

**Minimal testing** (per requirements):
- 1 test file: `App.test.tsx`
- Tests basic logic (task filtering)
- Uses Vitest (lightweight, Vite-native)
- No component rendering tests (would require React Testing Library)

## Deployment

### Local Development
```
UI: :3000 → API: :8080 → DB: :5432
```

### Production (Fly.io)
Two options:

**Option 1: Separate Apps**
```
UI App (nginx) → API App (Python) → Postgres
```

**Option 2: Serve UI from Backend**
- Build frontend: `npm run build`
- Copy `dist/` to backend static folder
- FastAPI serves static files
- Single Fly.io app

**Current implementation**: Option 1 (separate apps for cleaner separation)

## Security

- JWT stored in memory only (not localStorage/cookies)
- CORS configured on backend
- No sensitive data in frontend build
- HTTPS enforced in production (Fly.io)

## Performance

- Minimal bundle size (~50KB gzipped)
- No heavy libraries (React only)
- Static assets cached by nginx
- Lazy loading not needed (small app)

## Future Considerations

If scaling beyond MVP:
- Add React Router for multi-page navigation
- Add form validation library (e.g., react-hook-form)
- Add proper state management (Context API or Zustand)
- Add component tests
- Add persistent auth (secure httpOnly cookies)
