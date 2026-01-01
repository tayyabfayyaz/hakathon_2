# Quickstart: TodoList Pro

**Feature Branch**: `002-todolist-pro-ui`
**Date**: 2025-12-30

## Prerequisites

- Node.js 18.17 or later
- npm 9+ or pnpm 8+
- Git
- VS Code (recommended)

## Quick Setup

### 1. Initialize Next.js Project

```bash
# Create new Next.js project with TypeScript and Tailwind
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install when prompted:
# ✔ Would you like to use TypeScript? Yes
# ✔ Would you like to use ESLint? Yes
# ✔ Would you like to use Tailwind CSS? Yes
# ✔ Would you like to use `src/` directory? Yes
# ✔ Would you like to use App Router? Yes
# ✔ Would you like to customize the default import alias? Yes (@/*)
```

### 2. Install Shadcn/UI

```bash
# Initialize shadcn-ui
npx shadcn-ui@latest init

# Select when prompted:
# ✔ Which style would you like to use? Default
# ✔ Which color would you like to use as base color? Slate
# ✔ Would you like to use CSS variables for colors? Yes

# Install required components
npx shadcn-ui@latest add button input card dialog toast checkbox sheet avatar separator skeleton form label
```

### 3. Install Additional Dependencies

```bash
# Form handling and validation
npm install react-hook-form zod @hookform/resolvers

# Animations
npm install framer-motion

# Icons
npm install lucide-react

# Development tools
npm install -D prettier prettier-plugin-tailwindcss
```

### 4. Project Structure Setup

Create the following directory structure:

```bash
mkdir -p src/components/{ui,layout,landing,auth,tasks}
mkdir -p src/lib
mkdir -p src/hooks
mkdir -p src/types
mkdir -p src/contexts
mkdir -p src/app/\(marketing\)
mkdir -p src/app/\(auth\)/login
mkdir -p src/app/\(auth\)/register
mkdir -p src/app/\(dashboard\)/dashboard
mkdir -p src/app/api/auth/{login,register,logout,me}
mkdir -p src/app/api/tasks
```

### 5. Configure TypeScript

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 6. Configure Tailwind

Update `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### 7. Create Utility Files

Create `src/lib/utils.ts`:

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### 8. Create Type Definitions

Create `src/types/index.ts`:

```typescript
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  lastLoginAt: Date | null;
  avatarUrl?: string;
}

export interface Task {
  id: string;
  userId: string;
  text: string;
  completed: boolean;
  createdAt: Date;
  updatedAt: Date;
  completedAt: Date | null;
  order: number;
}

export interface Session {
  token: string;
  userId: string;
  expiresAt: Date;
  createdAt: Date;
}
```

## Development

### Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run format` | Format code with Prettier |

## Verification Checklist

After setup, verify:

- [ ] `npm run dev` starts without errors
- [ ] http://localhost:3000 shows Next.js default page
- [ ] TypeScript compiles without errors (`npm run build`)
- [ ] Shadcn components are in `src/components/ui/`
- [ ] Tailwind CSS is working (test by adding `className="bg-red-500"` to an element)
- [ ] All directories from step 4 exist

## Next Steps

1. Create layout components (`navbar.tsx`, `footer.tsx`)
2. Build landing page with hero and benefits sections
3. Implement auth forms (login, register)
4. Create task dashboard with CRUD operations
5. Add animations and polish

## Troubleshooting

### Common Issues

**Shadcn components not installing:**
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**TypeScript path aliases not working:**
- Restart VS Code
- Verify `tsconfig.json` has correct paths configuration
- Run `npm run build` to verify compilation

**Tailwind styles not applying:**
- Check `content` paths in `tailwind.config.ts`
- Verify `@tailwind` directives in `globals.css`
- Restart development server

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Shadcn/UI Documentation](https://ui.shadcn.com)
- [React Hook Form Documentation](https://react-hook-form.com)
- [Framer Motion Documentation](https://www.framer.com/motion)
