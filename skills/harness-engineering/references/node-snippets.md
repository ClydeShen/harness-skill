# Node / TypeScript Snippets

Paste-ready configs for Node.js and TypeScript projects.

---

## package.json — scripts section

Add these to your existing `package.json`. Adjust commands to match your
actual build tool (Next.js, tsc, esbuild, etc.).

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "eslint . --ext .ts,.tsx --fix",
    "typecheck": "tsc --noEmit",
    "test": "jest --passWithNoTests"
  }
}
```

For non-Next.js projects, replace `next dev` / `next build` with your tool:
- Plain TS: `"build": "tsc"`, `"dev": "ts-node src/index.ts"`
- Express: `"build": "tsc"`, `"dev": "ts-node-dev src/index.ts"`

---

## tsconfig.json — strict baseline

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

For Next.js, use `"module": "ESNext"` and `"moduleResolution": "Bundler"`.

---

## .lintstagedrc.json — lint-staged config

```json
{
  "*.{ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{js,jsx,json,md}": [
    "prettier --write"
  ]
}
```

---

## .husky/pre-commit — pre-commit hook

Create `.husky/pre-commit` with:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Step 1: lint and format staged files
npx lint-staged

# Step 2: type check whole project (TypeScript requires cross-file context)
npx tsc --noEmit
```

Install Husky if not present:

```bash
npm install --save-dev husky lint-staged
npx husky init
```

---

## ESLint flat config baseline (eslint.config.mjs)

```js
import tseslint from 'typescript-eslint'

export default tseslint.config(
  ...tseslint.configs.recommended,
  {
    rules: {
      'no-console': 'warn',
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  }
)
```

Install:

```bash
npm install --save-dev typescript-eslint
```

---
