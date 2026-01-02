# Research: TodoList Pro Complete UI

**Feature Branch**: `002-todolist-pro-ui`
**Date**: 2025-12-30
**Status**: Complete

## Technology Stack Decisions

### 1. Frontend Framework: Next.js 14+ (App Router)

**Decision**: Use Next.js 14+ with App Router for the frontend framework

**Rationale**:
- App Router provides React Server Components for optimal performance
- Built-in routing eliminates need for additional routing library
- Server-side rendering (SSR) and static generation (SSG) for SEO-friendly landing page
- API routes can handle authentication and task operations
- Excellent TypeScript support out of the box
- Native image optimization for landing page assets

**Alternatives Considered**:
- Vite + React: Faster dev server but lacks SSR without additional setup
- Create React App: Deprecated, no SSR support
- Remix: Good alternative but smaller ecosystem than Next.js

**Best Practices for Next.js App Router**:
- Use `app/` directory structure with route groups for organization
- Leverage Server Components by default, use `'use client'` only when necessary
- Use `loading.tsx` and `error.tsx` for better UX
- Implement route handlers (`route.ts`) for API endpoints
- Use `next/font` for optimized font loading
- Implement `metadata` exports for SEO

### 2. Styling: Tailwind CSS

**Decision**: Use Tailwind CSS for utility-first styling

**Rationale**:
- Rapid UI development with utility classes
- Built-in responsive design utilities (sm:, md:, lg:, xl:)
- Consistent design system through configuration
- Excellent integration with Shadcn/UI
- Small production bundle with purging unused styles
- Dark mode support via `dark:` variants

**Alternatives Considered**:
- CSS Modules: More boilerplate, less rapid development
- Styled Components: Runtime overhead, SSR complexity
- Vanilla CSS: Maintenance burden at scale

**Best Practices for Tailwind**:
- Configure custom colors in `tailwind.config.ts` for brand consistency
- Use `@apply` sparingly, prefer utility classes
- Organize complex component styles with `cn()` utility (class-variance-authority)
- Define reusable design tokens (spacing, colors, typography)

### 3. Component Library: Shadcn/UI

**Decision**: Use Shadcn/UI for accessible, customizable components

**Rationale**:
- Not a dependency - components are copied into codebase for full control
- Built on Radix UI primitives with excellent accessibility (WCAG 2.1 AA)
- Pre-styled with Tailwind CSS, consistent with our styling approach
- Includes all needed components: Button, Input, Card, Dialog, Toast, Checkbox
- TypeScript-first with excellent type definitions
- Customizable via CSS variables

**Alternatives Considered**:
- Material UI: Heavy bundle, opinionated styling
- Chakra UI: Good but different styling paradigm
- Headless UI: Would require more custom styling work

**Components Needed for This Feature**:
- `Button` - CTAs, form submissions, task actions
- `Input` - Form fields for auth and task creation
- `Card` - Benefit sections, task items
- `Dialog` - Delete confirmation, edit task modal
- `Toast` - Success/error notifications, undo prompts
- `Checkbox` - Task completion toggle, remember me
- `Sheet` - Mobile navigation drawer
- `Avatar` - User profile indicator
- `Separator` - Visual dividers
- `Skeleton` - Loading states

### 4. Form Handling & Validation

**Decision**: Use React Hook Form with Zod for form management and validation

**Rationale**:
- React Hook Form: Minimal re-renders, excellent performance
- Zod: TypeScript-first schema validation, runtime type checking
- Seamless integration with Shadcn form components
- Supports real-time validation per spec requirements

**Validation Schemas Required**:
```
RegistrationSchema:
  - name: string, 2-50 chars
  - email: valid email format
  - password: min 8 chars, 1 uppercase, 1 lowercase, 1 number
  - confirmPassword: must match password

LoginSchema:
  - email: valid email format
  - password: non-empty

TaskSchema:
  - text: string, 1-500 chars
```

### 5. State Management

**Decision**: Use React Context + useReducer for auth state, local state for UI

**Rationale**:
- Auth state needs to be global (user session)
- Task state can be component-local with optimistic updates
- No need for Redux/Zustand complexity for this scope
- Server state managed via Next.js data fetching patterns

**State Structure**:
```
AuthContext:
  - user: User | null
  - isLoading: boolean
  - isAuthenticated: boolean

TaskContext (if needed):
  - tasks: Task[]
  - isLoading: boolean
  - optimisticUpdates: Map<string, Task>
```

### 6. Authentication Strategy

**Decision**: JWT-based authentication with HTTP-only cookies for UI-only implementation

**Rationale**:
- Spec mentions "TypeScript for UI only" - focusing on frontend
- HTTP-only cookies prevent XSS token theft
- JWT allows stateless authentication
- Can mock auth endpoints for UI development

**For MVP/Demo**:
- Implement auth UI flows completely
- Use mock authentication (localStorage or mock API)
- Structure code to easily swap for real backend later

### 7. Animation & Interactions

**Decision**: Use Framer Motion for animations

**Rationale**:
- Spec requires "smooth animations" for interactive demos
- Declarative animation API works well with React
- Supports layout animations for task list reordering
- Exit animations for delete confirmation
- Spring physics for natural feel

**Animation Use Cases**:
- Hero section entrance animations
- Benefit section scroll-triggered reveals
- Task checkbox completion animation
- Task list item add/remove transitions
- Toast notification slide-in/out
- Button hover/tap states

## Architecture Decisions

### Routing Structure (App Router)

```
app/
├── (marketing)/           # Route group for public pages
│   ├── page.tsx          # Landing page (/)
│   └── layout.tsx        # Marketing layout (no auth navbar)
├── (auth)/               # Route group for auth pages
│   ├── login/
│   │   └── page.tsx      # Login page (/login)
│   ├── register/
│   │   └── page.tsx      # Registration page (/register)
│   └── layout.tsx        # Auth layout (centered card)
├── (dashboard)/          # Route group for authenticated pages
│   ├── dashboard/
│   │   └── page.tsx      # Task dashboard (/dashboard)
│   └── layout.tsx        # Dashboard layout (with sidebar/navbar)
├── api/                  # API routes (mock or real)
│   ├── auth/
│   │   ├── login/route.ts
│   │   ├── register/route.ts
│   │   └── logout/route.ts
│   └── tasks/
│       └── route.ts      # CRUD operations
├── layout.tsx            # Root layout
└── globals.css           # Global styles
```

### Component Organization

```
components/
├── ui/                   # Shadcn components (auto-generated)
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   └── ...
├── layout/               # Layout components
│   ├── navbar.tsx
│   ├── footer.tsx
│   └── mobile-nav.tsx
├── landing/              # Landing page components
│   ├── hero-section.tsx
│   ├── benefits-section.tsx
│   ├── demo-section.tsx
│   └── testimonials.tsx
├── auth/                 # Auth-related components
│   ├── login-form.tsx
│   ├── register-form.tsx
│   └── auth-provider.tsx
└── tasks/                # Task management components
    ├── task-list.tsx
    ├── task-item.tsx
    ├── task-input.tsx
    ├── empty-state.tsx
    └── delete-dialog.tsx
```

### Performance Optimizations

Per constitution Performance Budget (VI):
- Use Next.js Image component for optimized images
- Implement code splitting with dynamic imports
- Use Server Components for non-interactive content
- Lazy load below-fold landing page sections
- Implement skeleton loading states
- Configure font subsetting with `next/font`

### Accessibility Implementation

Per constitution UX Excellence (III):
- All Shadcn components have ARIA attributes built-in
- Implement keyboard navigation for task list
- Focus management for modals and navigation
- Color contrast ratios verified against WCAG 2.1 AA
- Screen reader announcements for task actions (aria-live)

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Bundle size exceeds 200KB | Use dynamic imports, analyze with next/bundle-analyzer |
| Animation jank on low-end devices | Use `will-change` sparingly, test on throttled CPU |
| Form validation UX complexity | Use Shadcn Form component with react-hook-form integration |
| Auth state persistence across tabs | Use storage event listeners or broadcast channel |
| Offline capability per constitution | Implement service worker for task caching (future phase) |

## Dependencies Summary

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
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.0.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0"
  }
}
```
