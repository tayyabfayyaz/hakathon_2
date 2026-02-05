# Implementation Plan: TodoList Pro Complete UI

**Branch**: `002-todolist-pro-ui` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todolist-pro-ui/spec.md`

## Summary

Build a complete TodoList Pro web application UI featuring:
- Landing page with interactive benefit demonstrations
- User registration and login forms with real-time validation
- Task dashboard with full CRUD operations (create, read, update, delete, toggle)
- Responsive navbar with authentication state awareness
- Footer with copyright attribution to Tayyab Fayyaz

Technical approach: Next.js 14+ App Router with TypeScript, Tailwind CSS for styling, Shadcn/UI for accessible components, React Hook Form + Zod for form handling, and Framer Motion for animations.

## Technical Context

**Language/Version**: TypeScript 5.x / Node.js 18.17+
**Primary Dependencies**: Next.js 14+, React 18, Tailwind CSS 3.4+, Shadcn/UI, React Hook Form, Zod, Framer Motion
**Storage**: localStorage for mock data (UI-only implementation); structured for backend integration
**Testing**: Jest + React Testing Library (optional per spec); Playwright for E2E (optional)
**Target Platform**: Web (Modern browsers: Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web application (Next.js App Router)
**Performance Goals**: FCP <1.5s, TTI <3s, Bundle <200KB gzipped (per constitution)
**Constraints**: WCAG 2.1 AA accessibility, <100ms UI response, mobile-first responsive (320px-1920px)
**Scale/Scope**: Single-user task management, ~6 pages, ~20 components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Implementation |
|-----------|--------|----------------|
| I. Data Integrity First | ✅ PASS | Optimistic updates with rollback, soft-delete with undo, atomic operations via mock API |
| II. Offline-First Architecture | ⚠️ PARTIAL | localStorage caching implemented; full offline sync deferred to future phase |
| III. User Experience Excellence | ✅ PASS | <100ms UI response via optimistic updates, keyboard navigation, WCAG 2.1 AA via Shadcn, undo for deletes |
| IV. Test-Driven Development | ⏸️ DEFERRED | Tests optional per spec; structure supports TDD when enabled |
| V. Security & Privacy by Design | ✅ PASS | No third-party tracking, secure form handling, generic auth errors, input sanitization |
| VI. Performance Budget | ✅ PASS | Next.js SSR/SSG, code splitting, optimized images, Shadcn tree-shaking |

**Constitution Compliance**: PASS (with documented deferral of full offline sync to future phase)

## Project Structure

### Documentation (this feature)

```text
specs/002-todolist-pro-ui/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technology decisions and rationale
├── data-model.md        # TypeScript interfaces and validation schemas
├── quickstart.md        # Setup instructions
├── contracts/
│   └── api-schema.yaml  # OpenAPI 3.0 specification
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── app/
│   ├── (marketing)/
│   │   ├── page.tsx           # Landing page (/)
│   │   └── layout.tsx         # Marketing layout
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx       # Login page (/login)
│   │   ├── register/
│   │   │   └── page.tsx       # Registration page (/register)
│   │   └── layout.tsx         # Auth layout (centered)
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Task dashboard (/dashboard)
│   │   └── layout.tsx         # Dashboard layout
│   ├── api/
│   │   ├── auth/
│   │   │   ├── login/route.ts
│   │   │   ├── register/route.ts
│   │   │   ├── logout/route.ts
│   │   │   └── me/route.ts
│   │   └── tasks/
│   │       ├── route.ts       # GET all, POST create
│   │       └── [taskId]/
│   │           ├── route.ts   # GET, PATCH, DELETE
│   │           ├── toggle/route.ts
│   │           └── restore/route.ts
│   ├── layout.tsx             # Root layout
│   └── globals.css            # Global styles + Tailwind
├── components/
│   ├── ui/                    # Shadcn components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── toast.tsx
│   │   ├── checkbox.tsx
│   │   ├── sheet.tsx
│   │   ├── avatar.tsx
│   │   ├── separator.tsx
│   │   ├── skeleton.tsx
│   │   ├── form.tsx
│   │   └── label.tsx
│   ├── layout/
│   │   ├── navbar.tsx         # Main navigation
│   │   ├── mobile-nav.tsx     # Mobile hamburger menu
│   │   └── footer.tsx         # Site footer
│   ├── landing/
│   │   ├── hero-section.tsx   # Hero with CTA
│   │   ├── benefits-section.tsx
│   │   ├── demo-section.tsx   # Interactive demos
│   │   └── testimonials.tsx   # Social proof
│   ├── auth/
│   │   ├── login-form.tsx
│   │   ├── register-form.tsx
│   │   └── auth-provider.tsx  # Auth context
│   └── tasks/
│       ├── task-list.tsx
│       ├── task-item.tsx
│       ├── task-input.tsx
│       ├── empty-state.tsx
│       └── delete-dialog.tsx
├── contexts/
│   └── auth-context.tsx       # Authentication state
├── hooks/
│   ├── use-auth.ts            # Auth hook
│   ├── use-tasks.ts           # Tasks CRUD hook
│   └── use-toast.ts           # Toast notifications
├── lib/
│   ├── utils.ts               # cn() and utilities
│   ├── validations.ts         # Zod schemas
│   └── mock-data.ts           # Mock API data
└── types/
    └── index.ts               # TypeScript interfaces
```

**Structure Decision**: Web application structure using Next.js App Router with route groups for marketing, auth, and dashboard sections. Components organized by feature domain.

## Component Architecture

### Page Components (Server Components by default)

| Route | Component | Type | Description |
|-------|-----------|------|-------------|
| `/` | `(marketing)/page.tsx` | Server | Landing page with SSG |
| `/login` | `(auth)/login/page.tsx` | Server | Login form wrapper |
| `/register` | `(auth)/register/page.tsx` | Server | Registration form wrapper |
| `/dashboard` | `(dashboard)/dashboard/page.tsx` | Server | Task dashboard wrapper |

### Client Components ('use client')

| Component | Reason for Client |
|-----------|-------------------|
| `navbar.tsx` | Auth state, mobile menu toggle |
| `mobile-nav.tsx` | Sheet interaction |
| `login-form.tsx` | Form state, validation |
| `register-form.tsx` | Form state, validation |
| `task-list.tsx` | CRUD operations, optimistic updates |
| `task-item.tsx` | Toggle, edit, delete interactions |
| `task-input.tsx` | Form submission |
| `demo-section.tsx` | Interactive animations |
| `auth-provider.tsx` | Context provider |

### Shared Components (Server or Client based on usage)

| Component | Props | Accessibility |
|-----------|-------|---------------|
| `hero-section.tsx` | title, subtitle, ctaText, ctaHref | Semantic headings, focus management |
| `benefits-section.tsx` | benefits[] | Role="list", aria-labels |
| `footer.tsx` | - | nav role, links with aria-current |
| `empty-state.tsx` | message, actionLabel, onAction | Focus on action button |

## State Management Design

### Auth Context

```typescript
// contexts/auth-context.tsx
interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegistrationFormData) => Promise<void>;
  logout: () => void;
}
```

### Task State (Component Local)

```typescript
// hooks/use-tasks.ts
interface UseTasksReturn {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  addTask: (text: string) => Promise<void>;
  updateTask: (id: string, data: Partial<Task>) => Promise<void>;
  toggleTask: (id: string) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  restoreTask: (id: string) => void;
}
```

## API Routes Design

Per `contracts/api-schema.yaml`:

| Method | Endpoint | Handler | Auth |
|--------|----------|---------|------|
| POST | `/api/auth/register` | Create user | No |
| POST | `/api/auth/login` | Authenticate | No |
| POST | `/api/auth/logout` | Clear session | Yes |
| GET | `/api/auth/me` | Get current user | Yes |
| GET | `/api/tasks` | List user tasks | Yes |
| POST | `/api/tasks` | Create task | Yes |
| GET | `/api/tasks/[taskId]` | Get task | Yes |
| PATCH | `/api/tasks/[taskId]` | Update task | Yes |
| DELETE | `/api/tasks/[taskId]` | Delete task | Yes |
| POST | `/api/tasks/[taskId]/toggle` | Toggle completion | Yes |
| POST | `/api/tasks/[taskId]/restore` | Undo delete | Yes |

## Animation Strategy

Using Framer Motion for:

1. **Landing Page**
   - Hero text fade-in on load
   - Benefits cards stagger animation on scroll (useInView)
   - Demo interactive checkmark animation

2. **Task List**
   - AnimatePresence for add/remove transitions
   - Layout animations for reordering
   - Checkbox spring animation on toggle

3. **Modals/Sheets**
   - Overlay fade
   - Content slide/scale

## Performance Optimizations

1. **Next.js Optimizations**
   - Static generation for landing page
   - Dynamic imports for heavy components
   - Image optimization with `next/image`
   - Font optimization with `next/font`

2. **Bundle Optimization**
   - Shadcn components are tree-shakeable
   - Lazy load demo section below fold
   - Defer non-critical animations

3. **Runtime Performance**
   - Optimistic updates for instant feedback
   - Debounced form validation
   - Memoized task list items

## Accessibility Checklist

Per Constitution Principle III and spec WCAG 2.1 AA requirement:

- [ ] All interactive elements have visible focus states
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Touch targets ≥ 44x44 pixels on mobile
- [ ] Form inputs have associated labels
- [ ] Error messages are announced to screen readers
- [ ] Keyboard navigation works for all task operations
- [ ] Skip link to main content
- [ ] Reduced motion support via prefers-reduced-motion

## Complexity Tracking

> No constitution violations requiring justification.

| Decision | Rationale |
|----------|-----------|
| Mock API instead of real backend | Spec explicitly states "TypeScript for UI only" |
| Deferred full offline sync | Constitution allows gradual implementation; localStorage caching covers MVP |
| Optional tests | Spec marks tests as optional; structure supports TDD when enabled |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Bundle exceeds 200KB | Monitor with `next/bundle-analyzer`; lazy load below-fold content |
| Animation performance on mobile | Test on throttled devices; provide reduced-motion fallback |
| Form validation edge cases | Comprehensive Zod schemas; test with edge inputs |
| Auth state persistence | Use localStorage with expiry; handle tab sync |

## Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^10.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.300.0",
    "@radix-ui/react-checkbox": "^1.0.0",
    "@radix-ui/react-dialog": "^1.0.0",
    "@radix-ui/react-avatar": "^1.0.0",
    "@radix-ui/react-separator": "^1.0.0",
    "@radix-ui/react-slot": "^1.0.0",
    "@radix-ui/react-label": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.0.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0",
    "tailwindcss-animate": "^1.0.0"
  }
}
```

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Follow quickstart.md to initialize project
3. Implement in priority order: Setup → Foundational → US1 (Landing) → US2/3 (Auth) → US4 (CRUD) → US5/6 (Polish)
