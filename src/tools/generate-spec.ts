import { findMaterial } from '../knowledge/materials.js';
import { MESH_GUIDELINES } from '../knowledge/guidelines.js';

interface SimulationSpec {
  project_name: string;
  analysis_types: string[];
  material: {
    name: string;
    family: string;
    source: string;
  };
  process_conditions: {
    melt_temp_C: number;
    mold_temp_C: number;
    coolant_temp_C: number;
    injection_time_s: string;
    packing_pressure_profile: string;
    packing_time_s: string;
    cooling_time_s: string;
    v_p_switchover: string;
  };
  mesh_recommendation: {
    type: string;
    rationale: string;
    element_size_mm: string;
    refinement_zones: string[];
  };
  preprocessing_notes: string[];
  expected_outputs: string[];
}

export function generateSimulationSpec(
  description: string,
  cadFormat?: string
): string {
  const desc = description.toLowerCase();

  // Try to extract material from description
  const materialKeywords = [
    'abs', 'pp', 'pa6', 'pa66', 'pc', 'pom', 'pe', 'hdpe', 'ldpe',
    'pmma', 'pbt', 'pet', 'ps', 'hips', 'tpu', 'san', 'asa', 'ppe',
    'nylon', 'acetal', 'polycarbonate', 'polypropylene', 'polyethylene',
    'acrylic', 'polystyrene', 'glass fiber', 'gf30', 'gf',
  ];

  let detectedMaterial = '';
  for (const kw of materialKeywords) {
    if (desc.includes(kw)) {
      detectedMaterial = kw;
      break;
    }
  }

  const materialMatches = detectedMaterial ? findMaterial(detectedMaterial) : [];
  const mat = materialMatches[0];

  // Detect analysis types from description
  const analysisTypes: string[] = ['Fill'];
  if (desc.includes('warp') || desc.includes('shrink') || desc.includes('dimension')) {
    analysisTypes.push('Pack', 'Warp');
  }
  if (desc.includes('cool') || desc.includes('cycle time') || desc.includes('temperature')) {
    analysisTypes.push('Cool');
  }
  if (desc.includes('fiber') || desc.includes('glass') || desc.includes('gf') || desc.includes('orient')) {
    analysisTypes.push('Fiber Orientation');
  }
  if (desc.includes('stress') || desc.includes('structural') || desc.includes('load')) {
    analysisTypes.push('Stress');
  }
  // Default: at least Fill + Pack
  if (!analysisTypes.includes('Pack')) analysisTypes.push('Pack');
  // If warpage is important, need cooling too
  if (analysisTypes.includes('Warp') && !analysisTypes.includes('Cool')) {
    analysisTypes.push('Cool');
  }

  // Detect wall thickness hints
  let wallThickness = '2.0';
  const thickMatch = desc.match(/(\d+\.?\d*)\s*mm\s*(wall|thick)/);
  if (thickMatch) wallThickness = thickMatch[1];
  const thinWall = desc.includes('thin') || parseFloat(wallThickness) < 1.5;
  const thickWall = desc.includes('thick') || parseFloat(wallThickness) > 4.0;

  // Determine mesh type
  let meshType = 'Dual Domain (Fusion)';
  let meshRationale = 'Best balance of accuracy and speed for standard parts';
  if (thickWall || desc.includes('gas assist') || desc.includes('overmold') || desc.includes('insert')) {
    meshType = '3D';
    meshRationale = 'Required for thick parts, gas assist, overmolding, or insert molding';
  }
  if (desc.includes('early') || desc.includes('quick') || desc.includes('gate location study')) {
    meshType = 'Midplane';
    meshRationale = 'Fast for early-stage gate location studies';
  }

  // Build spec
  const spec: SimulationSpec = {
    project_name: extractProjectName(description),
    analysis_types: analysisTypes,
    material: mat ? {
      name: mat.name,
      family: mat.family,
      source: 'MoldSim MCP material database (verify against supplier datasheet)',
    } : {
      name: detectedMaterial || 'NOT SPECIFIED — select material',
      family: 'unknown',
      source: 'User must specify material or select from database',
    },
    process_conditions: {
      melt_temp_C: mat ? mat.processing.melt_temp_recommended_C : 0,
      mold_temp_C: mat ? mat.processing.mold_temp_recommended_C : 0,
      coolant_temp_C: mat ? Math.max(10, mat.processing.mold_temp_recommended_C - 15) : 20,
      injection_time_s: thinWall ? '0.3–1.0 (thin wall — fast fill)' : thickWall ? '2.0–5.0 (thick wall — controlled fill)' : '0.5–2.0 (standard)',
      packing_pressure_profile: mat ? `Step 1: ${Math.round(mat.processing.melt_temp_recommended_C * 0.4)}–${Math.round(mat.processing.melt_temp_recommended_C * 0.6)} MPa (set from simulation fill pressure, 50-80%)` : 'Set from fill analysis: 50-80% of peak injection pressure',
      packing_time_s: 'Set from gate freeze analysis (typically 3–15s)',
      cooling_time_s: 'Set from cooling analysis — time to reach ejection temperature',
      v_p_switchover: '95–99% volumetric fill',
    },
    mesh_recommendation: {
      type: meshType,
      rationale: meshRationale,
      element_size_mm: meshType === '3D'
        ? `Global: ${parseFloat(wallThickness) * 0.5}mm, 4-8 layers through thickness`
        : `Global: ${parseFloat(wallThickness) * 2}–${parseFloat(wallThickness) * 3}mm`,
      refinement_zones: [
        'Gate region: 0.5× global size',
        'Thin sections: 1× wall thickness',
        'Sharp corners and transitions: local refinement',
        ...(desc.includes('weld') ? ['Weld line critical areas: refined mesh'] : []),
      ],
    },
    preprocessing_notes: [
      ...(cadFormat ? [`CAD format: ${cadFormat} — import and verify geometry integrity`] : []),
      'Remove unnecessary features (logos, text, micro-features) that don\'t affect flow',
      'Heal any surface gaps or missing faces before meshing',
      'Verify wall thickness is captured correctly in mesh',
      ...(mat?.processing.drying_temp_C != null ? [`Material drying required: ${mat.processing.drying_temp_C}°C for ${mat.processing.drying_time_hr}h`] : []),
      ...(mat?.filler ? [`Glass-filled material — enable fiber orientation analysis`] : []),
    ],
    expected_outputs: [
      'Fill time contour',
      'Injection pressure (XY plot and contour)',
      'Air trap locations',
      'Weld line locations',
      ...(analysisTypes.includes('Pack') ? ['Volumetric shrinkage', 'Sink mark indicator'] : []),
      ...(analysisTypes.includes('Cool') ? ['Part temperature at ejection', 'Cooling circuit efficiency'] : []),
      ...(analysisTypes.includes('Warp') ? ['Total deflection', 'Deflection contributors (shrinkage, cooling, orientation)'] : []),
      ...(analysisTypes.includes('Fiber Orientation') ? ['Fiber orientation tensor', 'Mechanical property distribution'] : []),
      'Clamp force requirement',
    ],
  };

  return formatSpec(spec);
}

function extractProjectName(description: string): string {
  // Try to extract a meaningful project name from the description
  const words = description.split(/\s+/).slice(0, 5);
  return words.join('-').replace(/[^a-zA-Z0-9-]/g, '').toLowerCase() || 'molding-simulation';
}

function formatSpec(spec: SimulationSpec): string {
  const lines: string[] = [];

  lines.push(`# Simulation Specification: ${spec.project_name}\n`);

  lines.push(`## Analysis Types`);
  lines.push(`Sequence: ${spec.analysis_types.join(' → ')}\n`);

  lines.push(`## Material`);
  lines.push(`- Name: ${spec.material.name}`);
  lines.push(`- Family: ${spec.material.family}`);
  lines.push(`- Source: ${spec.material.source}\n`);

  lines.push(`## Process Conditions`);
  if (spec.process_conditions.melt_temp_C > 0) {
    lines.push(`- Melt temperature: ${spec.process_conditions.melt_temp_C}°C`);
    lines.push(`- Mold temperature: ${spec.process_conditions.mold_temp_C}°C`);
    lines.push(`- Coolant temperature: ${spec.process_conditions.coolant_temp_C}°C`);
  }
  lines.push(`- Injection time: ${spec.process_conditions.injection_time_s}`);
  lines.push(`- Packing pressure: ${spec.process_conditions.packing_pressure_profile}`);
  lines.push(`- Packing time: ${spec.process_conditions.packing_time_s}`);
  lines.push(`- Cooling time: ${spec.process_conditions.cooling_time_s}`);
  lines.push(`- V/P switchover: ${spec.process_conditions.v_p_switchover}\n`);

  lines.push(`## Mesh Recommendation`);
  lines.push(`- Type: ${spec.mesh_recommendation.type}`);
  lines.push(`- Rationale: ${spec.mesh_recommendation.rationale}`);
  lines.push(`- Element size: ${spec.mesh_recommendation.element_size_mm}`);
  lines.push(`- Refinement zones:`);
  spec.mesh_recommendation.refinement_zones.forEach(z => lines.push(`  - ${z}`));
  lines.push('');

  lines.push(`## Preprocessing Notes`);
  spec.preprocessing_notes.forEach(n => lines.push(`- ${n}`));
  lines.push('');

  lines.push(`## Expected Outputs`);
  spec.expected_outputs.forEach(o => lines.push(`- ${o}`));

  lines.push('\n---');
  lines.push('*Generated by MoldSim MCP Server. Verify all parameters against material supplier datasheet.*');

  return lines.join('\n');
}
