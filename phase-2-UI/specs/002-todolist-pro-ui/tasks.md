# Tasks: TodoList Pro Complete UI

**Input**: Design documents from `/specs/002-todolist-pro-ui/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-schema.yaml, quickstart.md

**Tests**: Tests are OPTIONAL per spec - not included unless explicitly requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Next.js App Router**: `src/app/` for routes, `src/components/` for components
- **Types**: `src/types/`
- **Hooks**: `src/hooks/`
- **Utilities**: `src/lib/`
- **Contexts**: `src/contexts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Next.js project with all dependencies and base configuration

- [ ] T001 Create Next.js project with TypeScript, Tailwind, App Router using `npx create-next-app@latest`
- [ ] T002 Install Shadcn/UI and initialize with `npx shadcn-ui@latest init`
- [ ] T003 [P] Install Shadcn components: button, input, card, dialog, toast, checkbox, sheet, avatar, separator, skeleton, form, label
- [ ] T004 [P] Install additional dependencies: react-hook-form, zod, @hookform/resolvers, framer-motion, lucide-react
- [ ] T005 [P] Configure Prettier with tailwindcss plugin in `.prettierrc`
- [ ] T006 Create TypeScript interfaces in `src/types/index.ts` (User, Task, Session, form types)
- [ ] T007 Create utility function `cn()` in `src/lib/utils.ts`
- [ ] T008 Create Zod validation schemas in `src/lib/validations.ts` (registration, login, task schemas)
- [ ] T009 Create mock data and storage utilities in `src/lib/mock-data.ts`

**Checkpoint**: Project initialized with all dependencies, types, and utilities ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create root layout with fonts and metadata in `src/app/layout.tsx`
- [ ] T011 Configure global styles and CSS variables in `src/app/globals.css`
- [ ] T012 Create AuthContext with useReducer in `src/contexts/auth-context.tsx`
- [ ] T013 Create AuthProvider wrapper component in `src/components/auth/auth-provider.tsx`
- [ ] T014 Create useAuth hook in `src/hooks/use-auth.ts`
- [ ] T015 [P] Create toast hook in `src/hooks/use-toast.ts`
- [ ] T016 [P] Create Toaster component for notifications in `src/components/ui/toaster.tsx`
- [ ] T017 Create Navbar component (logo, conditional auth buttons) in `src/components/layout/navbar.tsx`
- [ ] T018 Create MobileNav component (hamburger menu with Sheet) in `src/components/layout/mobile-nav.tsx`
- [ ] T019 Create Footer component with copyright in `src/components/layout/footer.tsx`

**Checkpoint**: Foundation ready - auth context, layout components, and hooks available for all stories

---

## Phase 3: User Story 1 - Landing Page (Priority: P1) 🎯 MVP

**Goal**: First-time visitors see compelling landing page with benefits and CTAs

**Independent Test**: Load homepage, verify hero section, benefits, and interactive demos render correctly

### Implementation for User Story 1

- [ ] T020 [US1] Create marketing layout in `src/app/(marketing)/layout.tsx`
- [ ] T021 [US1] Create landing page in `src/app/(marketing)/page.tsx`
- [ ] T022 [P] [US1] Create HeroSection component with headline, subtitle, CTA buttons in `src/components/landing/hero-section.tsx`
- [ ] T023 [P] [US1] Create BenefitsSection component with 3+ benefit cards in `src/components/landing/benefits-section.tsx`
- [ ] T024 [P] [US1] Create DemoSection component with interactive task demo in `src/components/landing/demo-section.tsx`
- [ ] T025 [P] [US1] Create TestimonialsSection component with placeholder testimonials in `src/components/landing/testimonials.tsx`
- [ ] T026 [US1] Add Framer Motion animations to hero (fade-in) and benefits (stagger on scroll) sections
- [ ] T027 [US1] Add smooth scroll navigation for benefit section links
- [ ] T028 [US1] Ensure landing page is responsive (320px to 1920px)

**Checkpoint**: Landing page complete - visitors can see value proposition and click to sign up

---

## Phase 4: User Story 2 - New User Registration (Priority: P1)

**Goal**: New users can create an account with validated registration form

**Independent Test**: Navigate to /register, fill form with valid data, see success message

### Implementation for User Story 2

- [ ] T029 [US2] Create auth layout (centered card design) in `src/app/(auth)/layout.tsx`
- [ ] T030 [US2] Create registration page in `src/app/(auth)/register/page.tsx`
- [ ] T031 [US2] Create RegisterForm component with React Hook Form + Zod in `src/components/auth/register-form.tsx`
- [ ] T032 [US2] Implement real-time email validation with error messages
- [ ] T033 [US2] Implement password strength validation (8+ chars, uppercase, lowercase, number)
- [ ] T034 [US2] Implement password confirmation matching validation
- [ ] T035 [US2] Create mock register API route in `src/app/api/auth/register/route.ts`
- [ ] T036 [US2] Add form submission handling with loading state and success/error feedback
- [ ] T037 [US2] Add link to login page for existing users
- [ ] T038 [US2] Prevent double-submission during form processing

**Checkpoint**: Registration complete - new users can create accounts

---

## Phase 5: User Story 3 - Returning User Login (Priority: P1)

**Goal**: Registered users can log in and access their dashboard

**Independent Test**: Navigate to /login, enter valid credentials, redirect to dashboard

### Implementation for User Story 3

- [ ] T039 [US3] Create login page in `src/app/(auth)/login/page.tsx`
- [ ] T040 [US3] Create LoginForm component with React Hook Form + Zod in `src/components/auth/login-form.tsx`
- [ ] T041 [US3] Implement email and password fields with validation
- [ ] T042 [US3] Add "Remember me" checkbox option
- [ ] T043 [US3] Add "Forgot Password" placeholder link
- [ ] T044 [US3] Create mock login API route in `src/app/api/auth/login/route.ts`
- [ ] T045 [US3] Create mock logout API route in `src/app/api/auth/logout/route.ts`
- [ ] T046 [US3] Create mock me API route in `src/app/api/auth/me/route.ts`
- [ ] T047 [US3] Add generic error message for failed authentication (security)
- [ ] T048 [US3] Implement redirect to dashboard after successful login
- [ ] T049 [US3] Add link to registration page for new users

**Checkpoint**: Login complete - users can authenticate and access protected routes

---

## Phase 6: User Story 4 - Task Management CRUD (Priority: P1)

**Goal**: Authenticated users can create, read, update, delete, and toggle tasks

**Independent Test**: Login, create task, view in list, edit, toggle complete, delete with undo

### Implementation for User Story 4

- [ ] T050 [US4] Create dashboard layout in `src/app/(dashboard)/layout.tsx`
- [ ] T051 [US4] Create dashboard page in `src/app/(dashboard)/dashboard/page.tsx`
- [ ] T052 [US4] Create useTasks hook with CRUD operations in `src/hooks/use-tasks.ts`
- [ ] T053 [US4] Create TaskInput component (text field + add button) in `src/components/tasks/task-input.tsx`
- [ ] T054 [US4] Create TaskList component (container for task items) in `src/components/tasks/task-list.tsx`
- [ ] T055 [US4] Create TaskItem component (checkbox, text, edit, delete) in `src/components/tasks/task-item.tsx`
- [ ] T056 [US4] Create EmptyState component (no tasks guidance) in `src/components/tasks/empty-state.tsx`
- [ ] T057 [US4] Create DeleteDialog component (confirmation modal) in `src/components/tasks/delete-dialog.tsx`
- [ ] T058 [US4] Create mock tasks API routes (GET, POST) in `src/app/api/tasks/route.ts`
- [ ] T059 [US4] Create mock task API routes (GET, PATCH, DELETE) in `src/app/api/tasks/[taskId]/route.ts`
- [ ] T060 [US4] Create mock toggle API route in `src/app/api/tasks/[taskId]/toggle/route.ts`
- [ ] T061 [US4] Create mock restore API route in `src/app/api/tasks/[taskId]/restore/route.ts`
- [ ] T062 [US4] Implement optimistic updates for all CRUD operations
- [ ] T063 [US4] Implement undo functionality for task deletion (5+ seconds)
- [ ] T064 [US4] Add visual distinction for completed tasks (strikethrough, opacity)
- [ ] T065 [US4] Add Framer Motion animations for task add/remove/toggle
- [ ] T066 [US4] Implement inline edit mode for task text

**Checkpoint**: Task CRUD complete - core product functionality working

---

## Phase 7: User Story 5 - Navigation and Footer (Priority: P2)

**Goal**: Consistent navigation across all pages with auth-aware navbar and footer

**Independent Test**: Visit any page, verify navbar shows correct auth state, footer displays copyright

### Implementation for User Story 5

- [ ] T067 [US5] Update Navbar to show Login/Sign Up for unauthenticated users
- [ ] T068 [US5] Update Navbar to show profile avatar and Logout for authenticated users
- [ ] T069 [US5] Make logo clickable linking to homepage
- [ ] T070 [US5] Make Navbar sticky/fixed on scroll
- [ ] T071 [US5] Ensure Footer displays "All rights reserved by Tayyab Fayyaz" with current year
- [ ] T072 [US5] Add optional placeholder links in Footer (Privacy, Terms)
- [ ] T073 [US5] Ensure Footer is consistently positioned on all pages

**Checkpoint**: Navigation complete - consistent UX across all pages

---

## Phase 8: User Story 6 - Responsive Mobile Experience (Priority: P2)

**Goal**: Full functionality on mobile devices with touch-friendly UI

**Independent Test**: Access all pages on mobile viewport, verify layouts adapt and touch targets are adequate

### Implementation for User Story 6

- [ ] T074 [US6] Implement hamburger menu toggle for Navbar on mobile (< 768px)
- [ ] T075 [US6] Ensure landing page content stacks vertically on mobile
- [ ] T076 [US6] Ensure all form inputs have proper mobile keyboard types (email, password)
- [ ] T077 [US6] Verify touch targets are at least 44x44 pixels for all interactive elements
- [ ] T078 [US6] Test and fix task dashboard layout on mobile
- [ ] T079 [US6] Add swipe gesture support for task actions (optional enhancement)
- [ ] T080 [US6] Verify all pages work correctly from 320px to 1920px viewport

**Checkpoint**: Mobile experience complete - app works on all device sizes

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T081 [P] Add visible focus states to all interactive elements for accessibility
- [ ] T082 [P] Verify color contrast ratios meet WCAG 2.1 AA (4.5:1 minimum)
- [ ] T083 [P] Add aria-labels to icon-only buttons and interactive elements
- [ ] T084 [P] Implement keyboard navigation for task operations
- [ ] T085 Add loading skeletons for pages and components
- [ ] T086 Add error boundary components for graceful error handling
- [ ] T087 [P] Add prefers-reduced-motion support for animations
- [ ] T088 Performance audit: verify bundle size < 200KB gzipped
- [ ] T089 Run Lighthouse audit and address any issues (target >90 scores)
- [ ] T090 Final responsive testing across all breakpoints

**Checkpoint**: Polish complete - production-ready application

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ─────────────────────────────────────────┐
                                                         │
Phase 2: Foundational ◄──────────────────────────────────┘
         │
         ├──► Phase 3: US1 - Landing Page (P1)
         │
         ├──► Phase 4: US2 - Registration (P1)
         │
         ├──► Phase 5: US3 - Login (P1)
         │
         └──► Phase 6: US4 - Task CRUD (P1) ◄── depends on US3 for auth
                       │
                       ├──► Phase 7: US5 - Navigation (P2)
                       │
                       └──► Phase 8: US6 - Mobile (P2)
                                     │
                                     └──► Phase 9: Polish
```

### User Story Dependencies

| Story | Can Start After | Dependencies |
|-------|-----------------|--------------|
| US1 - Landing | Phase 2 complete | None |
| US2 - Registration | Phase 2 complete | None |
| US3 - Login | Phase 2 complete | None |
| US4 - Task CRUD | US3 complete | Auth context for protected routes |
| US5 - Navigation | US3 complete | Auth state for conditional UI |
| US6 - Mobile | US1-5 complete | All components must exist |

### Parallel Opportunities

**Within Phase 1 (Setup)**:
```
T003, T004, T005 can run in parallel (independent package installs)
```

**Within Phase 2 (Foundational)**:
```
T015, T016 can run in parallel (toast hook + toaster component)
```

**Within Phase 3 (US1 - Landing)**:
```
T022, T023, T024, T025 can run in parallel (independent section components)
```

**Across User Stories** (after Phase 2):
```
US1 (Landing), US2 (Registration), US3 (Login) can run in parallel
US4 must wait for US3 (needs auth)
US5 can start once US3 is complete
US6 needs all previous stories complete
```

---

## Implementation Strategy

### MVP First (Core Functionality)

1. Complete **Phase 1**: Setup (T001-T009)
2. Complete **Phase 2**: Foundational (T010-T019)
3. Complete **Phase 3**: Landing Page (T020-T028)
4. Complete **Phase 4**: Registration (T029-T038)
5. Complete **Phase 5**: Login (T039-T049)
6. Complete **Phase 6**: Task CRUD (T050-T066)
7. **STOP and VALIDATE**: Test complete user journey

### Incremental Delivery

| Milestone | Stories Complete | Demo Capability |
|-----------|------------------|-----------------|
| M1 | Setup + Foundation + US1 | Landing page live |
| M2 | M1 + US2 + US3 | Users can register and login |
| M3 | M2 + US4 | Full task management working |
| M4 | M3 + US5 + US6 | Complete responsive experience |
| M5 | M4 + Polish | Production-ready |

---

## Task Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| 1 | Setup | 9 | 4 |
| 2 | Foundational | 10 | 2 |
| 3 | US1 - Landing | 9 | 4 |
| 4 | US2 - Registration | 10 | 0 |
| 5 | US3 - Login | 11 | 0 |
| 6 | US4 - Task CRUD | 17 | 0 |
| 7 | US5 - Navigation | 7 | 0 |
| 8 | US6 - Mobile | 7 | 0 |
| 9 | Polish | 10 | 5 |
| **Total** | | **90** | **15** |

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable after completion
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- Tests are optional - add if TDD approach is requested later
