# MoldSim MCP — Testing Guide

How to connect, test, and verify the MoldSim MCP server.

---

## Option 1: Claude Code (fastest)

One command to install and use:

```bash
claude mcp add moldsim -- npx -y moldsim-mcp
```

Then start a Claude session and ask:

```bash
claude "What causes warpage in glass-filled PA66 parts?"
claude "Compare ABS vs PC vs PA66-GF30 for an automotive connector"
claude "Validate my process: ABS, 250°C melt, 70°C mold, 2.5mm wall"
claude "Run a DFM check: 2mm wall, 1.5mm ribs, 1° draft, ABS material"
claude "Generate a simulation spec for a PP container with 1.5mm walls"
```

Claude will automatically use the MoldSim tools when relevant.

---

## Option 2: Claude Desktop

Add to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

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

Restart Claude Desktop. The MoldSim tools will appear in the tools panel.

---

## Option 3: Local build (for development)

```bash
git clone https://github.com/kobzevvv/moldsim-mcp.git
cd moldsim-mcp
npm install
npm run build
```

Then register the local build with Claude Code:

```bash
claude mcp add moldsim-local -- node /path/to/moldsim-mcp/dist/index.js
```

Or add to Claude Desktop config:

```json
{
  "mcpServers": {
    "moldsim-local": {
      "command": "node",
      "args": ["/path/to/moldsim-mcp/dist/index.js"]
    }
  }
}
```

---

## Option 4: Test without Claude (direct MCP protocol)

The MCP server uses JSON-RPC over stdio. You can talk to it directly.

### Step 1: Start the server

```bash
node dist/index.js
# Output: MoldSim MCP server running on stdio
```

### Step 2: Send JSON-RPC messages

The server reads newline-delimited JSON from stdin. First initialize, then call tools.

**Initialize:**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

**List available tools:**
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

**Call a tool:**
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_material_properties","arguments":{"material":"ABS"}}}
```

### Step 3: One-liner test

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"validate_process_parameters","arguments":{"material":"ABS","melt_temp_C":250,"mold_temp_C":60,"wall_thickness_mm":2.5}}}\n' | node dist/index.js 2>/dev/null
```

### Step 4: Interactive testing script

Save as `test-mcp.sh` and run `bash test-mcp.sh`:

```bash
#!/bin/bash
# Quick MCP test for all 6 tools

SERVER="node $(pwd)/dist/index.js"

run_tool() {
  local name=$1
  local args=$2
  printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"'"$name"'","arguments":'"$args"'}}\n' \
    | $SERVER 2>/dev/null \
    | python3 -c "import sys,json; [print(json.loads(l)['result']['content'][0]['text'][:200]) for l in sys.stdin if l.strip() and json.loads(l).get('id')==2]"
}

echo "=== 1. query_simulation_knowledge ==="
run_tool "query_simulation_knowledge" '{"question":"What causes sink marks?"}'

echo "=== 2. get_material_properties ==="
run_tool "get_material_properties" '{"material":"abs-generic","properties":["processing"]}'

echo "=== 3. validate_process_parameters ==="
run_tool "validate_process_parameters" '{"material":"ABS","melt_temp_C":280,"mold_temp_C":60}'

echo "=== 4. generate_simulation_spec ==="
run_tool "generate_simulation_spec" '{"description":"PP cap, 1.5mm wall, check fill and cooling"}'

echo "=== 5. compare_materials ==="
run_tool "compare_materials" '{"materials":["abs-generic","pc","pa66"]}'

echo "=== 6. generate_dfm_checklist ==="
run_tool "generate_dfm_checklist" '{"description":"Connector housing","wall_thickness_mm":2,"rib_thickness_mm":1.4,"draft_angle_deg":1,"material":"abs-generic"}'
```

---

## Available Tools

| Tool | What it does |
|------|-------------|
| `query_simulation_knowledge` | Free-text Q&A: defects, mesh strategy, DFM rules, process optimization |
| `get_material_properties` | Material data: Cross-WLF viscosity, Tait PVT, thermal, processing window, mechanical |
| `validate_process_parameters` | Checks melt/mold temps against material window, estimates cooling time |
| `generate_simulation_spec` | Natural language → full simulation specification (analysis types, mesh, process) |
| `compare_materials` | Side-by-side comparison of 2–4 materials, highlights key differences |
| `generate_dfm_checklist` | 15+ DFM rule checks: wall ratio, rib thickness, draft, gating, venting |

### 21 supported materials

`abs-generic`, `pp-homo`, `pp-copo`, `pa6`, `pa66`, `pa66-gf30`, `pc`, `pc-abs`, `pom`, `hdpe`, `ldpe`, `pmma`, `pbt`, `pbt-gf30`, `pet`, `ps`, `hips`, `tpu`, `san`, `asa`, `ppe-ps`

---

## Example prompts to test

Paste any of these into Claude after connecting the MCP:

```
What causes warpage in glass-filled nylon parts?

I'm seeing sink marks on a PC housing — what should I check in simulation?

Give me the Cross-WLF viscosity parameters for PA66-GF30

Validate: ABS at 245°C melt, 60°C mold, 2.5mm wall, 15s cooling

Compare ABS vs PC vs PA66-GF30 for an automotive connector housing

Generate a simulation spec for a medical syringe in PP, 0.8mm wall, sterility requirements

DFM check: 2mm wall, 1.5mm ribs, 0.5° draft, textured surface, PC material

What mesh type for a thick-walled POM gear (5mm)?

My PA66 part is crystallizing unevenly — what process parameters to check?
```

---

## Troubleshooting

**Server doesn't start:**
```bash
npm install && npm run build
node dist/index.js  # should print: MoldSim MCP server running on stdio
```

**Tool not appearing in Claude:**
- Check config file JSON syntax (no trailing commas)
- Restart Claude Desktop fully (Cmd+Q, not just close window)
- For Claude Code: `claude mcp list` to verify registration

**`compare_materials` returning wrong data (all same material):**
- This is a bug in npm versions ≤ 0.4.1 — fixed in local build
- Workaround: use exact material IDs from the list above
- Fix: run from local build (`node dist/index.js`) or wait for 0.4.2 npm release

**Slow first response:**
- The server loads embedding models on first query — 5–15s is normal
- Subsequent queries are fast

---

## Running tests from this repo

```bash
npm run build  # TypeScript compilation, should exit 0 with no errors
```

No test suite yet. To add tests:

```bash
npm install --save-dev jest ts-jest @types/jest
```

The core logic is pure functions in `src/tools/` and `src/knowledge/` — easy to unit test.
