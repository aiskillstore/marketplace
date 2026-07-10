# create-near-app

Scaffold new NEAR dApps via CLI.

## Usage

```bash
npx create-near-app@latest
```

Interactive prompts guide through project setup. Or pass arguments directly:

```bash
npx create-near-app <project-name> \
  --frontend next-app|next-page|vite-react|none \
  --contract rs|ts|none \
  --install
```

All arguments required except `--install`. Use `--install` to auto-install dependencies.

## Options

### Frontend Frameworks

| Option | Description |
|---|---|
| `vite-react` | Vite + React SPA |
| `next-app` | Next.js App Router |
| `next-page` | Next.js Pages Router |
| `none` | Contract only, no frontend |

### Contract Languages

| Option | Description |
|---|---|
| `rs` | Rust smart contract |
| `ts` | TypeScript smart contract (JS SDK) |
| `none` | Frontend only, no contract |

### Templates

When creating a contract, available templates:
- `auction` — basic auction contract
- `auction-adv` — advanced auction contract

## Project Structure

After scaffolding with frontend + contract:

```
my-app/
├── contract/           # Smart contract source
│   ├── src/
│   └── Cargo.toml      # (Rust) or package.json (TS)
├── frontend/           # Web application
│   ├── src/
│   ├── package.json
│   └── ...
├── integration-tests/  # Sandbox tests
└── README.md
```

## Prerequisites

- Node.js 18+ (for frontend)
- Rust toolchain (for `rs` contracts)

## After Scaffolding

Follow the generated `README.md` in the project. Typical flow:

```bash
cd my-app
npm install        # if --install not used
npm run dev        # start frontend dev server
npm run build      # build contract
npm run test       # run sandbox tests
npm run deploy     # deploy contract to testnet
```
