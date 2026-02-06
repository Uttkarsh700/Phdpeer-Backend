# Frontend Structure Analysis

## Current State

### Two Frontend Folders Detected

1. **`Frontend/`** (capital F) - Located at root level
2. **`frontend/`** (lowercase f) - Located at root level

Both folders appear to have **identical structure and content** based on file comparison.

---

## Entry Point Analysis

### Primary Entry Point
- **File**: `src/main.tsx`
- **Location**: Both `Frontend/src/main.tsx` and `frontend/src/main.tsx`
- **Content**:
  ```typescript
  import { createRoot } from "react-dom/client";
  import App from "./App.tsx";
  import "./index.css";
  
  createRoot(document.getElementById("root")!).render(<App />);
  ```

### HTML Entry Point
- **File**: `index.html`
- **Location**: Root of both frontend folders
- **Script Reference**: `<script type="module" src="/src/main.tsx"></script>`
- **Root Element**: `<div id="root"></div>`

---

## Routing Setup Analysis

### Router Configuration
- **Library**: `react-router-dom` v6.30.1
- **Location**: `src/App.tsx`
- **Router Type**: `BrowserRouter`

### Route Structure

#### Public Routes (No Layout)
- `/` → `GatewayLanding` component
- `/auth` → `Auth` component

#### Protected Routes (With Layout)
All routes below are wrapped in `<Layout />` component:

- `/home` → `Index` component
- `/profile-strength` → `ProfileStrength` component
- `/wellbeing` → `WellBeingCheckIn` component
- `/timeline` → `ResearchTimeline` component
- `/network` → `PeerNetwork` component
- `/university-dashboard` → `UniversityDashboard` component
- `/dashboard` → `Dashboard` component
- `/collaboration-ledger` → `CollaborationLedger` component
- `/writing-evolution` → `WritingEvolution` component
- `/writing-evolution/baseline` → `WritingEvolutionBaseline` component
- `/writing-evolution/checkpoint` → `WritingEvolutionCheckpoint` component
- `/writing-evolution/report/:id` → `WritingEvolutionReport` component (dynamic route)
- `/writing-evolution/certificate` → `WritingEvolutionCertificate` component

#### Catch-All Route
- `*` → `NotFound` component (404 page)

### Route Protection
- **Location**: `src/components/layout/Layout.tsx`
- **Mechanism**: 
  - Checks `sessionStorage.getItem("frensei_access")` for gateway access
  - Checks `sessionStorage.getItem("isAuthenticated")` for protected routes
  - Redirects to `/auth` if not authenticated
  - Protected routes: `/wellbeing`, `/timeline`, `/network`, `/university-dashboard`, `/collaboration-ledger`, `/dashboard`, `/writing-evolution`

---

## Build System Analysis

### Build Tool
- **Tool**: Vite v5.4.19
- **Config File**: `vite.config.ts`

### Vite Configuration
```typescript
{
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(), // @vitejs/plugin-react-swc
    componentTagger() // lovable-tagger (dev only)
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}
```

### Build Scripts (from package.json)
- `dev`: Start development server (`vite`)
- `build`: Production build (`vite build`)
- `build:dev`: Development build (`vite build --mode development`)
- `lint`: Run ESLint (`eslint .`)
- `preview`: Preview production build (`vite preview`)

### Development Server
- **Host**: `::` (all interfaces)
- **Port**: `8080`
- **Auto-reload**: Enabled via Vite HMR

---

## Technology Stack

### Core Framework
- **React**: v18.3.1
- **TypeScript**: v5.8.3
- **Vite**: v5.4.19

### UI Libraries
- **shadcn/ui**: Component library (Radix UI primitives)
- **Tailwind CSS**: v3.4.17 (utility-first CSS)
- **Radix UI**: Multiple component primitives
- **Lucide React**: Icon library v0.462.0

### State Management & Data Fetching
- **TanStack Query (React Query)**: v5.83.0
- **React Hook Form**: v7.61.1
- **Zod**: v3.25.76 (schema validation)

### Routing
- **React Router DOM**: v6.30.1

### Additional Libraries
- **Recharts**: v2.15.4 (charts)
- **date-fns**: v3.6.0 (date utilities)
- **canvas-confetti**: v1.9.3
- **@huggingface/transformers**: v3.7.5

---

## Project Structure

```
frontend/
├── index.html                 # HTML entry point
├── package.json               # Dependencies and scripts
├── vite.config.ts            # Vite build configuration
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── eslint.config.js          # ESLint configuration
├── components.json           # shadcn/ui configuration
├── public/                   # Static assets
│   ├── favicon.ico
│   ├── favicon.png
│   ├── placeholder.svg
│   └── robots.txt
└── src/
    ├── main.tsx              # React entry point
    ├── App.tsx               # Main app component (routing)
    ├── App.css               # Global app styles
    ├── index.css             # Global CSS imports
    ├── vite-env.d.ts         # Vite type definitions
    ├── assets/               # Static assets
    │   └── penguin-mascot.png
    ├── components/           # React components
    │   ├── auth/             # Authentication components
    │   ├── layout/           # Layout components (Header, Layout)
    │   ├── ledger/           # Collaboration ledger components
    │   ├── profile/          # Profile-related components
    │   ├── ui/               # shadcn/ui components (49 files)
    │   └── wellness/         # Wellness check-in components
    ├── pages/                # Page components (16 files)
    ├── hooks/                # Custom React hooks
    ├── lib/                  # Utility libraries
    ├── data/                 # Static data
    └── integrations/         # Third-party integrations
```

---

## Key Features Identified

### Pages (16 total)
1. `GatewayLanding` - Landing/gateway page
2. `Auth` - Authentication page
3. `Index` - Home page
4. `Dashboard` - Main dashboard
5. `ProfileStrength` - Profile strength page
6. `WellBeingCheckIn` - Wellness check-in
7. `ResearchTimeline` - Research timeline view
8. `PeerNetwork` - Peer network page
9. `UniversityDashboard` - University dashboard
10. `CollaborationLedger` - Collaboration ledger
11. `WritingEvolution` - Writing evolution main
12. `WritingEvolutionBaseline` - Baseline creation
13. `WritingEvolutionCheckpoint` - Checkpoint creation
14. `WritingEvolutionReport` - Report view (dynamic route)
15. `WritingEvolutionCertificate` - Certificate view
16. `NotFound` - 404 page

### Component Categories
- **Auth**: Login modals, institutional access
- **Layout**: Header, Layout wrapper
- **Ledger**: Collaboration event tracking
- **Profile**: Profile strength, goals, timeline, stats
- **Wellness**: Wellness check-in components
- **UI**: 49 shadcn/ui components

---

## TypeScript Configuration

### Path Aliases
- `@/*` → `./src/*` (configured in both `tsconfig.json` and `vite.config.ts`)

### TypeScript Settings
- `noImplicitAny`: false
- `strictNullChecks`: false
- `skipLibCheck`: true
- `allowJs`: true

---

## Styling Configuration

### Tailwind CSS
- **Mode**: Class-based dark mode
- **Content**: Scans `./src/**/*.{ts,tsx}`, `./pages/**/*.{ts,tsx}`, `./components/**/*.{ts,tsx}`
- **Custom Colors**: Wellness colors, sidebar colors, gradient colors
- **Font**: Inter (from Google Fonts)

### CSS Variables
Uses CSS custom properties for theming (HSL color values)

---

## Dependencies Summary

### Production Dependencies: 30+
- React ecosystem
- Radix UI components
- TanStack Query
- React Router
- Form handling
- Charts and visualization
- Date utilities
- UI utilities

### Development Dependencies: 12+
- Vite and plugins
- TypeScript
- ESLint
- Tailwind CSS
- PostCSS
- Type definitions

---

## Observations

1. **Identical Folders**: Both `Frontend/` and `frontend/` appear to be identical
2. **No Separate Router File**: Routing is defined directly in `App.tsx`
3. **Session-Based Auth**: Uses `sessionStorage` for authentication state
4. **Layout Wrapper**: Most routes are wrapped in a `Layout` component
5. **Dynamic Routes**: One dynamic route (`/writing-evolution/report/:id`)
6. **Port Configuration**: Dev server runs on port 8080 (not standard 3000)
7. **Path Alias**: Uses `@/` for `src/` directory imports
8. **Lovable Integration**: Built with Lovable.dev (based on README)

---

## Next Steps Recommendation

Since both folders are identical, determine:
1. Which folder is the "prebuilt" frontend?
2. Should `Frontend/` be moved to `frontend/` (replacing existing)?
3. Or should contents be merged/compared for differences?

**Current Status**: Analysis complete. No code changes made. Ready for move/merge decision.
