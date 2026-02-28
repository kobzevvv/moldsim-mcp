# MoldSim MCP Server

An MCP (Model Context Protocol) server that gives AI assistants expert knowledge about injection molding simulation. Material properties, process validation, troubleshooting, and simulation specification generation — all available as tools.

## Why

Setting up injection molding simulations (Moldflow, Moldex3D, Cadmould) requires deep knowledge: Cross-WLF viscosity models, Tait PVT data, processing windows, mesh strategies, DFM rules. This MCP server makes that knowledge available to any AI assistant that supports MCP.

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

**20 materials included:** ABS, PP Homo, PP Copo, PA6, PA66, PA66-GF30, PC, PC/ABS, POM, HDPE, LDPE, PMMA, PBT, PBT-GF30, PET, PS, HIPS, TPU, SAN, ASA, PPE/PS

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
Natural language → structured simulation specification. Describes the part and get back analysis types, mesh recommendations, process conditions, and expected outputs.

```
"Automotive dashboard panel in PC/ABS, 2.5mm wall, warpage analysis"
→ Fill+Pack+Cool+Warp sequence, dual-domain mesh, process conditions, expected outputs
```

## Install

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

### Claude Code

```bash
claude mcp add moldsim -- npx -y moldsim-mcp
```

### From source

```bash
git clone https://github.com/kobzevvv/moldsim-mcp.git
cd moldsim-mcp
npm install
npm run build
```

Then point your MCP client to `node dist/index.js`.

## Examples

Ask your AI assistant:

- "What are the Cross-WLF parameters for PA66-GF30?"
- "I'm getting sink marks on my PC housing — what should I check?"
- "Validate my process: ABS at 250°C melt, 70°C mold, 2mm wall"
- "Generate a simulation spec for a PP container with 1.5mm walls"
- "What mesh type should I use for a thick-walled POM gear (5mm)?"
- "How do I fix warpage in a glass-filled PA66 connector?"

## Knowledge Coverage

| Area | Coverage |
|------|----------|
| Materials | 20 grades with Cross-WLF, Tait PVT, thermal, mechanical, processing |
| Defects | Short shot, flash, sink marks, warpage, weld lines, burn marks, jetting, splay, voids, flow marks |
| Simulation | Mesh sensitivity, race tracking, cooling, overpacking, shear rate |
| Process | Cycle time, gate location, V/P switchover, degradation, crystallization, fiber orientation |
| DFM | Wall thickness, ribs, draft, radii, bosses, gating, tolerances, shrinkage, venting |
| Meshing | Midplane, dual-domain, 3D — when to use, element sizing, quality metrics |

## License

MIT
