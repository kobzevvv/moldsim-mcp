import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { queryKnowledge } from './tools/query-knowledge.js';
import { getMaterialProperties } from './tools/get-material.js';
import { validateProcessParameters } from './tools/validate-params.js';
import { generateSimulationSpec } from './tools/generate-spec.js';
import { compareMaterials } from './tools/compare-materials.js';
import { generateDFMChecklist } from './tools/dfm-checklist.js';
import { listMaterials } from './knowledge/materials.js';
import { warmupEmbedding } from './qdrant.js';

export function createServer(): McpServer {
  const server = new McpServer({
    name: 'moldsim-mcp',
    version: '0.4.0',
  });

  // Start loading embedding model in background
  warmupEmbedding();

  // Tool 1: Query simulation knowledge
  server.tool(
    'query_simulation_knowledge',
    'Search injection molding simulation knowledge base. Covers troubleshooting (defects, simulation issues), DFM rules, mesh guidelines, and process parameter recommendations. Use for general questions about molding, simulation setup, or problem-solving.',
    {
      question: z.string().describe('Your question about injection molding simulation'),
      context: z.string().optional().describe('Additional context (material, part type, defect observed)'),
    },
    async ({ question, context }) => ({
      content: [{ type: 'text', text: await queryKnowledge(question, context) }],
    })
  );

  // Tool 2: Get material properties
  server.tool(
    'get_material_properties',
    `Look up material properties for injection molding simulation. Returns Cross-WLF viscosity model, 2-domain Tait PVT, thermal properties, processing window, and mechanical data. Available materials: ${listMaterials().map(m => m.id).join(', ')}`,
    {
      material: z.string().describe('Material name, family, or ID (e.g., "PA66-GF30", "PC", "ABS", "pp-homo")'),
      properties: z.array(z.string()).optional().describe('Filter to specific property groups: "cross_wlf", "pvt", "thermal", "processing", "mechanical". Omit for all properties.'),
    },
    async ({ material, properties }) => ({
      content: [{ type: 'text', text: getMaterialProperties(material, properties) }],
    })
  );

  // Tool 3: Validate process parameters
  server.tool(
    'validate_process_parameters',
    'Validate injection molding process parameters against material processing window. Checks melt/mold temperature, estimates shear rate, calculates cooling time, and flags out-of-range values with suggestions.',
    {
      material: z.string().describe('Material name or ID (e.g., "PA66-GF30", "ABS")'),
      melt_temp_C: z.number().optional().describe('Melt temperature in °C'),
      mold_temp_C: z.number().optional().describe('Mold temperature in °C'),
      injection_speed_mm_s: z.number().optional().describe('Injection speed in mm/s'),
      packing_pressure_MPa: z.number().optional().describe('Packing pressure in MPa'),
      wall_thickness_mm: z.number().optional().describe('Nominal wall thickness in mm'),
      cooling_time_s: z.number().optional().describe('Cooling time in seconds'),
    },
    async (params) => ({
      content: [{ type: 'text', text: validateProcessParameters(params) }],
    })
  );

  // Tool 4: Generate simulation spec
  server.tool(
    'generate_simulation_spec',
    'Generate a structured simulation specification from a natural language description of the part and requirements. Outputs analysis types, process conditions, mesh recommendations, and expected results.',
    {
      description: z.string().describe('Describe the part, material, and what you want to analyze (e.g., "Automotive dashboard panel in PC/ABS, 2.5mm wall, need warpage and cooling analysis")'),
      cad_format: z.string().optional().describe('CAD file format if known (e.g., "STEP", "STL", "Parasolid", "IGES")'),
    },
    async ({ description, cad_format }) => ({
      content: [{ type: 'text', text: generateSimulationSpec(description, cad_format) }],
    })
  );

  // Tool 5: Compare materials
  server.tool(
    'compare_materials',
    `Compare 2-4 materials side-by-side. Returns a table of processing, thermal, and mechanical properties with key differences highlighted. Available materials: ${listMaterials().map(m => m.id).join(', ')}`,
    {
      materials: z.array(z.string()).min(2).max(4).describe('List of material IDs to compare (e.g., ["abs-generic", "pc", "pa66-gf30"])'),
    },
    async ({ materials }) => ({
      content: [{ type: 'text', text: compareMaterials(materials) }],
    })
  );

  // Tool 6: DFM checklist generator
  server.tool(
    'generate_dfm_checklist',
    'Generate a Design for Manufacturability (DFM) checklist for an injection molded part. Returns pass/warn/fail status for 15+ design rules based on part description and parameters.',
    {
      description: z.string().describe('Description of the part (e.g., "Automotive connector housing with snap-fits and thin walls")'),
      wall_thickness_mm: z.number().optional().describe('Nominal wall thickness in mm'),
      rib_thickness_mm: z.number().optional().describe('Rib thickness in mm'),
      rib_height_mm: z.number().optional().describe('Rib height in mm'),
      draft_angle_deg: z.number().optional().describe('Draft angle in degrees'),
      material: z.string().optional().describe('Material name or ID (e.g., "PA66-GF30", "ABS")'),
      has_undercuts: z.boolean().optional().describe('Whether the part has undercut features'),
      has_texture: z.boolean().optional().describe('Whether surfaces are textured'),
      texture_depth_mm: z.number().optional().describe('Texture depth in mm (for draft calculation)'),
      gate_type: z.string().optional().describe('Gate type: "edge", "sub", "pin", "hot", "fan", "tunnel"'),
      cosmetic_requirements: z.boolean().optional().describe('Whether part has cosmetic surface requirements'),
    },
    async (params) => ({
      content: [{ type: 'text', text: generateDFMChecklist(params) }],
    })
  );

  return server;
}
