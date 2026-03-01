# Contributing to MoldSim MCP

Thanks for your interest in contributing! MoldSim MCP is an open-source MCP server for injection molding simulation, and we welcome contributions of all kinds.

## Getting Started

### Prerequisites

- Node.js >= 18
- npm

### Development Setup

```bash
git clone https://github.com/kobzevvv/moldsim-mcp.git
cd moldsim-mcp
npm install
npm run build
```

### Running in Dev Mode

```bash
npm run dev   # watches for changes and recompiles
```

### Testing with MCP Inspector

```bash
npm run inspect
```

This opens the MCP Inspector UI where you can test all tools interactively.

## How to Contribute

### Adding a New Material

Materials live in `src/knowledge/materials.ts`. Each material requires:

1. **Cross-WLF viscosity model** parameters (from Moldflow material DB or published data)
2. **2-domain Tait PVT** model parameters
3. **Thermal properties** (conductivity, specific heat, density, ejection/no-flow temps)
4. **Processing window** (melt/mold temp ranges, max shear rate, drying)
5. **Mechanical properties** (tensile, flexural, elongation, HDT, shrinkage)

```typescript
{
  id: 'material-id',        // lowercase, hyphenated
  name: 'Material Name',
  family: 'FAMILY',         // e.g., PA, PP, PC
  type: 'semi-crystalline', // or 'amorphous'
  // ... all property groups
  notes: 'Brief description and typical applications.',
}
```

Add the material object to the `MATERIALS` array and run `npm run build` to verify.

### Adding a New Tool

1. Create a new file in `src/tools/` (e.g., `my-tool.ts`)
2. Export a function that takes typed input and returns a formatted string
3. Register the tool in `src/server.ts`:

```typescript
import { myTool } from './tools/my-tool.js';

// In createServer():
server.tool(
  'tool_name',
  'Tool description for the LLM',
  { /* zod schema */ },
  async (params) => ({
    content: [{ type: 'text', text: myTool(params) }],
  })
);
```

4. Run `npm run build` and test with `npm run inspect`

### Adding Knowledge Base Content

Troubleshooting articles are in `src/knowledge/troubleshooting.ts`. DFM rules and mesh guidelines are in `src/knowledge/guidelines.ts`.

## Code Style

- TypeScript, strict mode
- Functional style preferred (pure functions that return formatted strings)
- No external runtime dependencies beyond the MCP SDK and Zod
- Format output as Markdown for readability in LLM conversations

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes with clear commit messages
3. Run `npm run build` to ensure no TypeScript errors
4. Open a PR with:
   - What you changed and why
   - How to test the changes
   - Any relevant issue numbers

## Reporting Bugs

Use the [Bug Report](https://github.com/kobzevvv/moldsim-mcp/issues/new?template=bug_report.md) issue template. Include:

- Steps to reproduce
- Expected vs actual behavior
- Your environment (Node version, OS, MCP client)

## Questions?

Open a [Discussion](https://github.com/kobzevvv/moldsim-mcp/discussions) or file an issue.
