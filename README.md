# MoldSim MCP Server

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![npm](https://img.shields.io/npm/v/moldsim-mcp)](https://www.npmjs.com/package/moldsim-mcp)
[![MCP](https://img.shields.io/badge/MCP-compatible-00e5ff)](https://modelcontextprotocol.io)

**Give your AI assistant injection molding expertise.**

An MCP (Model Context Protocol) server that gives AI assistants expert knowledge about injection molding simulation. Material properties, process validation, troubleshooting, and simulation specification generation — all available as tools.

**Website:** [moldsim.com](https://moldsim.com)

## Why

Setting up injection molding simulations (Moldflow, Moldex3D, Cadmould) requires deep knowledge: Cross-WLF viscosity models, Tait PVT data, processing windows, mesh strategies, DFM rules. This MCP server makes that knowledge available to any AI assistant that supports MCP.

## Quick Start

### Claude Code (recommended)

```bash
claude mcp add moldsim -- npx -y moldsim-mcp
```

That's it. Ask Claude about injection molding — it will automatically use MoldSim tools.

```bash
claude "What causes warpage in glass-filled nylon parts?"
claude "Give me the Cross-WLF parameters for PC/ABS"
claude "Validate: ABS at 245C melt, 60C mold, 2.5mm wall"
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "moldsim": {
      "command": "npx",
      "args": ["-y", "moldsim-mcp"]
    }
  }
}
```

### From source

```bash
git clone https://github.com/kobzevvv/moldsim-mcp.git
cd moldsim-mcp
npm install
npm run build
```

Then point your MCP client to `node dist/index.js`.

## Tools

### `query_simulation_knowledge`
Free-text Q&A against the knowledge base. Ask about defects, DFM rules, mesh strategies, process optimization.

```
"Why is my part warping?" → causes, solutions, simulation checks
"What mesh type should I use?" → midplane vs dual-domain vs 3D guidance
"How to reduce cycle time?" → cooling optimization strategies
```

### `get_material_properties`
Material property lookup. Returns Cross-WLF viscosity, Tait PVT, thermal, processing window, and mechanical data.

**21 materials included:** ABS, PP Homo, PP Copo, PA6, PA66, PA66-GF30, PC, PC/ABS, POM, HDPE, LDPE, PMMA, PBT, PBT-GF30, PET, PS, HIPS, TPU, SAN, ASA, PPE/PS

```
"PA66-GF30" → Cross-WLF coefficients, Tait PVT, processing window 275-310°C, fiber effects
"PC" → all properties or filter by group (viscosity, thermal, processing)
```

### `validate_process_parameters`
Checks your process parameters against the material's processing window. Flags errors, warnings, and provides suggestions.

```
material: "ABS", melt_temp_C: 280 → ERROR: exceeds max 260°C, risk of degradation
material: "PA66", mold_temp_C: 40 → WARNING: below min 70°C, poor crystallization
```

### `generate_simulation_spec`
Natural language → structured simulation specification. Describe the part and get back analysis types, mesh recommendations, process conditions, and expected outputs.

```
"Automotive dashboard panel in PC/ABS, 2.5mm wall, warpage analysis"
→ Fill+Pack+Cool+Warp sequence, dual-domain mesh, process conditions, expected outputs
```

### `compare_materials`
Side-by-side comparison of 2-4 materials. Processing windows, thermal properties, mechanical data, and auto-generated key differences.

```
["abs-generic", "pc", "pa66-gf30"] → comparison table with stiffness, shrinkage, heat resistance diffs
```

### `generate_dfm_checklist`
Design for Manufacturability checklist with pass/warn/fail ratings. Input part parameters and get 15+ DFM rule checks.

```
material: "ABS", wall: 2mm, rib: 1.5mm, draft: 0.5°
→ 16 checks: wall OK, rib WARN (75% ratio), draft WARN (below 1°), sink risk, venting...
```

## Examples

Ask your AI assistant:

- "What are the Cross-WLF parameters for PA66-GF30?"
- "I'm getting sink marks on my PC housing — what should I check?"
- "Validate my process: ABS at 250°C melt, 70°C mold, 2mm wall"
- "Generate a simulation spec for a PP container with 1.5mm walls"
- "Compare ABS vs PC vs PA66-GF30 for an automotive connector"
- "Run a DFM check: 2mm wall, 1.5mm ribs, 0.5° draft in PC"
- "What mesh type should I use for a thick-walled POM gear (5mm)?"
- "How do I fix warpage in a glass-filled PA66 connector?"

## Knowledge Coverage

| Area | Coverage |
|------|----------|
| Materials | 21 grades with Cross-WLF, Tait PVT, thermal, mechanical, processing + comparison |
| Defects | Short shot, flash, sink marks, warpage, weld lines, burn marks, jetting, splay, voids, flow marks |
| Simulation | Mesh sensitivity, race tracking, cooling, overpacking, shear rate |
| Process | Cycle time, gate location, V/P switchover, degradation, crystallization, fiber orientation |
| DFM | Wall thickness, ribs, draft, radii, bosses, gating, tolerances, shrinkage, venting |
| Meshing | Midplane, dual-domain, 3D — when to use, element sizing, quality metrics |

## Compatible Software

MoldSim MCP provides software-agnostic knowledge that applies to all major injection molding simulation packages:

- **Autodesk Moldflow** — Adviser & Insight
- **Moldex3D** — all editions
- **CADMOULD** — Simcon
- **SIGMASOFT** — Virtual Molding
- **SolidWorks Plastics**

## Tech Stack

- **Runtime:** Node.js, TypeScript
- **Search:** Qdrant vector database (local, embedded)
- **Embeddings:** HuggingFace transformers
- **Protocol:** Model Context Protocol (MCP)

## License

MIT
