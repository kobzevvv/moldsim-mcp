/**
 * Design for Manufacturability (DFM) rules, meshing guidelines,
 * and process parameter bounds for injection molding simulation.
 */

export interface DFMRule {
  id: string;
  category: string;
  rule: string;
  details: string;
  typical_range?: string;
}

export interface MeshGuideline {
  id: string;
  mesh_type: 'midplane' | 'dual-domain' | '3D';
  topic: string;
  recommendation: string;
}

export interface ProcessBound {
  parameter: string;
  unit: string;
  general_min: number;
  general_max: number;
  notes: string;
}

// ──── DFM Rules ────

export const DFM_RULES: DFMRule[] = [
  {
    id: 'dfm-wall-uniform',
    category: 'Wall Thickness',
    rule: 'Maintain uniform wall thickness throughout the part',
    details: 'Variations in wall thickness cause differential cooling, uneven shrinkage, and warpage. Where changes are needed, use gradual transitions (3:1 taper ratio minimum). Thick-to-thin transitions promote race tracking.',
    typical_range: '1.0–4.0 mm for most thermoplastics',
  },
  {
    id: 'dfm-wall-min',
    category: 'Wall Thickness',
    rule: 'Minimum wall thickness depends on material and flow length',
    details: 'Thin walls increase injection pressure requirements and risk short shots. Maximum flow-length-to-thickness ratio varies by material: PP ~300:1, ABS ~200:1, PC ~100:1, PA ~150:1. Beyond these limits, consider multiple gates.',
    typical_range: 'ABS: 1.2–3.5mm, PP: 0.8–3.8mm, PC: 1.2–4.0mm, PA: 0.8–3.0mm',
  },
  {
    id: 'dfm-rib-thickness',
    category: 'Ribs',
    rule: 'Rib thickness should be 50-60% of adjoining wall thickness',
    details: 'Thicker ribs cause sink marks on the opposite surface. For cosmetic parts, use 50% ratio. If structural requirements demand thicker ribs, consider alternative stiffening approaches or textured surfaces to hide sinks.',
    typical_range: 'Rib thickness: 0.5–0.6 × wall thickness',
  },
  {
    id: 'dfm-rib-height',
    category: 'Ribs',
    rule: 'Maximum rib height should not exceed 3× wall thickness',
    details: 'Taller ribs are difficult to fill, eject, and maintain. They also act as flow leaders, causing race tracking. For additional stiffness, use more shorter ribs rather than fewer tall ones.',
    typical_range: 'Rib height ≤ 3 × wall thickness',
  },
  {
    id: 'dfm-rib-spacing',
    category: 'Ribs',
    rule: 'Rib spacing should be at least 2× wall thickness',
    details: 'Ribs placed too close together cause cooling problems between them, leading to hot spots and increased cycle time. Minimum spacing allows adequate cooling channel placement.',
    typical_range: 'Spacing ≥ 2 × wall thickness (center-to-center)',
  },
  {
    id: 'dfm-draft-angle',
    category: 'Draft',
    rule: 'Apply minimum 1° draft angle on all surfaces parallel to mold opening direction',
    details: 'Draft allows part ejection without damaging the part or mold. Textured surfaces need additional draft: add 1° per 0.025mm texture depth. Polished surfaces (SPI A-1) can use 0.5° minimum.',
    typical_range: 'Standard: 1–2°, Textured: 1° + 1°/0.025mm depth, Deep ribs: 0.25–0.5° per side',
  },
  {
    id: 'dfm-radius',
    category: 'Radii',
    rule: 'Use generous radii on all internal corners — minimum 0.5× wall thickness',
    details: 'Sharp corners create stress concentrations (factor 2-3×), impede material flow, and cause cooling issues. Internal radius = 0.5-0.75× wall thickness. External radius = internal + wall thickness. The radius/thickness ratio of 0.6 reduces stress concentration to ~1.5×.',
    typical_range: 'Internal radius: 0.5–1.0 × wall thickness',
  },
  {
    id: 'dfm-boss',
    category: 'Bosses',
    rule: 'Boss OD should not exceed 2× ID, connected to wall with ribs',
    details: 'Bosses are essentially thick cylindrical ribs. Standalone bosses with thick walls cause sink marks. Connect bosses to nearby walls with gusset ribs (50% wall thickness). Boss wall thickness should follow rib rules (50-60% of nominal wall).',
    typical_range: 'Boss OD: 2 × ID, Boss wall: 0.6 × nominal wall',
  },
  {
    id: 'dfm-undercut',
    category: 'Undercuts',
    rule: 'Avoid undercuts when possible; when needed, design for side actions or slides',
    details: 'Undercuts require complex tooling (slides, lifters, collapsing cores) that increases mold cost and maintenance. Internal undercuts are harder to release than external ones. Consider snap-fit designs that can be stripped from mold with material flexibility.',
  },
  {
    id: 'dfm-gate-thick',
    category: 'Gating',
    rule: 'Gate into the thickest section of the part',
    details: 'Gating into thick sections allows packing pressure to compensate for shrinkage. Flow should move from thick-to-thin to avoid hesitation and short shots. Gate should be placed to minimize flow length and balance fill pattern.',
  },
  {
    id: 'dfm-gate-size',
    category: 'Gating',
    rule: 'Gate thickness should be 50-80% of wall thickness',
    details: 'Undersized gate causes excessive shear and pressure drop. Oversized gate causes large vestige and longer cycle time (waiting for gate freeze). For cosmetic parts, smaller gates with longer packing time. For structural: larger gates for better packing.',
    typical_range: 'Gate thickness: 0.5–0.8 × wall thickness',
  },
  {
    id: 'dfm-tolerance',
    category: 'Tolerances',
    rule: 'Standard tolerance for injection molding is ±0.1mm/25mm + additional per material',
    details: 'Tighter tolerances increase cost exponentially. Amorphous plastics (ABS, PC) hold tighter tolerances than semi-crystalline (PP, PA). Across parting line add ±0.1mm. Glass-filled materials have anisotropic tolerances (tighter in flow direction).',
    typical_range: 'Fine: ±0.05mm/25mm (amorphous), Standard: ±0.1mm/25mm, Commercial: ±0.2mm/25mm',
  },
  {
    id: 'dfm-shrinkage',
    category: 'Shrinkage',
    rule: 'Account for material shrinkage in mold design — cavity is oversized',
    details: 'Mold cavity = part dimension × (1 + shrinkage rate). Amorphous materials: 0.4-0.8%. Semi-crystalline: 1.0-3.0%. Filled materials: lower in flow direction, higher cross-flow. Shrinkage varies with processing conditions (packing, cooling).',
    typical_range: 'Amorphous: 0.4–0.8%, Semi-crystalline: 1.0–3.0%, Filled: 0.2–1.5% (anisotropic)',
  },
  {
    id: 'dfm-weld-location',
    category: 'Weld Lines',
    rule: 'Position weld lines away from structural and cosmetic areas',
    details: 'Weld line strength is typically 60-90% of bulk material strength (lower for filled materials — can be <50%). Use gate placement and sequential gating to control weld line positions. Add overflow wells at weld locations for improved bonding.',
  },
  {
    id: 'dfm-vent-depth',
    category: 'Venting',
    rule: 'Vent depth depends on material viscosity',
    details: 'Vents at parting line, end of fill, and at weld line locations. Land length 1-2mm, then relief to atmosphere. Vent too deep = flash. Vent depth: crystalline materials (PP, PA) = 0.01-0.02mm; amorphous (ABS, PC) = 0.02-0.05mm; filled = 0.01-0.015mm.',
    typical_range: 'PP/PA: 0.01–0.02mm, ABS/PC: 0.02–0.05mm, Filled: 0.01–0.015mm',
  },
];

// ──── Mesh Guidelines ────

export const MESH_GUIDELINES: MeshGuideline[] = [
  {
    id: 'mesh-midplane-use',
    mesh_type: 'midplane',
    topic: 'When to use midplane mesh',
    recommendation: 'Best for thin, shell-like parts with uniform wall thickness. Fastest to solve. Not suitable for thick parts, 3D flow features, or complex core/cavity geometry. Wall thickness assigned as property, not geometric. Use for early-stage gate location studies.',
  },
  {
    id: 'mesh-dual-use',
    mesh_type: 'dual-domain',
    topic: 'When to use dual-domain (Fusion) mesh',
    recommendation: 'Best for most injection molded parts. Uses triangular elements on both surfaces with matched pairs. Good balance of accuracy and speed. Handles ribs, bosses, and thickness variations. Match ratio should be >85%. Not suitable for very thick parts (>5mm) or complex 3D flow.',
  },
  {
    id: 'mesh-3d-use',
    mesh_type: '3D',
    topic: 'When to use 3D mesh',
    recommendation: 'Required for thick parts (wall >4mm), complex flow patterns, gas/water assist, co-injection, overmolding, insert molding, or any analysis where through-thickness effects matter. Most accurate but slowest. Use minimum 4 elements through thickness, 8+ for accurate thermal results.',
  },
  {
    id: 'mesh-element-size',
    mesh_type: 'dual-domain',
    topic: 'Element size selection',
    recommendation: 'Default global edge length = 2-3× nominal wall thickness. Refine at gates (0.5× wall), thin sections (1× wall), corners and features. Total element count: 50k-200k for most parts. Over-meshing wastes time without improving accuracy.',
  },
  {
    id: 'mesh-3d-layers',
    mesh_type: '3D',
    topic: '3D mesh through-thickness layers',
    recommendation: 'Minimum 4 tetrahedral layers through wall thickness. For accurate thermal/fiber/shrinkage results: 8-12 layers. Gate region: 10+ layers. Total element count: 500k-5M typical. Use boundary layer meshing for better thermal resolution near walls.',
  },
  {
    id: 'mesh-runner',
    mesh_type: 'dual-domain',
    topic: 'Runner system meshing',
    recommendation: 'Use beam elements for cold runners. At least 6 elements around the runner cross-section for 3D runners. Match runner mesh density with part mesh at gate junction. Hot runner systems need thermal mesh on manifold.',
  },
  {
    id: 'mesh-quality',
    mesh_type: 'dual-domain',
    topic: 'Mesh quality metrics',
    recommendation: 'Target: aspect ratio <6:1 (max 20:1), match ratio >85% for dual domain, no free edges, no intersecting elements. For 3D: aspect ratio <20:1, no inverted elements. Fix mesh issues before running analysis — poor mesh = unreliable results.',
  },
  {
    id: 'mesh-cooling',
    mesh_type: '3D',
    topic: 'Cooling channel mesh',
    recommendation: 'Cooling channels should have at least 8 elements around circumference. Mesh density near channel surface affects heat transfer accuracy. BEM (Boundary Element Method) for mold cooling is more efficient than FEM for the mold body.',
  },
];

// ──── Process Parameter Bounds ────

export const PROCESS_BOUNDS: ProcessBound[] = [
  {
    parameter: 'injection_speed',
    unit: 'mm/s',
    general_min: 10,
    general_max: 500,
    notes: 'Thin walls need high speed. Thick walls and shear-sensitive materials (PVC, POM) need low speed. Multi-stage profile recommended.',
  },
  {
    parameter: 'injection_pressure',
    unit: 'MPa',
    general_min: 30,
    general_max: 200,
    notes: 'Machine maximum typically 140-200 MPa. Thin walls and long flow: higher. Thick walls and easy-flow: lower. Fill should use 50-80% of machine pressure capacity.',
  },
  {
    parameter: 'packing_pressure',
    unit: '% of injection pressure',
    general_min: 30,
    general_max: 80,
    notes: 'Start at 50% of injection pressure. Multi-step profile: 80% → 60% → 40%. Reduce to minimize overpacking near gate while maintaining packing at end-of-flow.',
  },
  {
    parameter: 'packing_time',
    unit: 's',
    general_min: 1,
    general_max: 30,
    notes: 'Should match gate freeze time (from simulation). Packing longer than gate freeze wastes cycle time. Typical: 3-15s depending on gate size.',
  },
  {
    parameter: 'cooling_time',
    unit: 's',
    general_min: 3,
    general_max: 60,
    notes: 'Dominated by thickest wall section. Scales with wall_thickness². Approximate: t_cool = (s²/π²α) × ln(8(T_melt-T_mold)/π²(T_eject-T_mold)). Typical: 8-30s.',
  },
  {
    parameter: 'coolant_temperature',
    unit: '°C',
    general_min: 10,
    general_max: 140,
    notes: 'Typically 10-30°C below mold target temp. Water up to 90°C, pressurized water to 140°C, oil for higher. Flow rate must ensure turbulent flow (Re >10000).',
  },
  {
    parameter: 'coolant_flow_rate',
    unit: 'L/min',
    general_min: 2,
    general_max: 20,
    notes: 'Must achieve turbulent flow (Reynolds >10000). Typical 5-12 L/min per circuit. Max ΔT in-out should be <3°C for uniform cooling.',
  },
  {
    parameter: 'clamp_force',
    unit: 'tons',
    general_min: 20,
    general_max: 6000,
    notes: 'Rule of thumb: 2-5 tons per sq inch of projected area. Crystalline materials (PP, PA): use higher multiplier. Use simulation result + 10-20% safety margin.',
  },
  {
    parameter: 'screw_speed',
    unit: 'RPM',
    general_min: 20,
    general_max: 200,
    notes: 'Affects plastication and shear heating. Higher speed = faster recovery but more shear. Shear-sensitive materials (PVC, POM): 20-60 RPM. Standard: 60-150 RPM.',
  },
  {
    parameter: 'back_pressure',
    unit: 'MPa',
    general_min: 0.3,
    general_max: 10,
    notes: 'Ensures melt homogeneity and consistent density. Too high = shear degradation. Too low = air entrainment. Standard: 0.5-3 MPa. Filled materials: 3-8 MPa.',
  },
];

// ──── Search Functions ────

export function searchGuidelines(query: string): {
  dfm: DFMRule[];
  mesh: MeshGuideline[];
  process: ProcessBound[];
} {
  const q = query.toLowerCase();
  const terms = q.split(/\s+/).filter(t => t.length > 2);

  const matchScore = (text: string): number =>
    terms.reduce((sum, term) => (text.toLowerCase().includes(term) ? sum + 1 : sum), 0);

  const dfm = DFM_RULES
    .filter(r => matchScore(`${r.category} ${r.rule} ${r.details} ${r.typical_range ?? ''}`) > 0)
    .sort((a, b) =>
      matchScore(`${b.category} ${b.rule} ${b.details}`) -
      matchScore(`${a.category} ${a.rule} ${a.details}`)
    );

  const mesh = MESH_GUIDELINES
    .filter(m => matchScore(`${m.topic} ${m.recommendation} ${m.mesh_type}`) > 0);

  const process = PROCESS_BOUNDS
    .filter(p => matchScore(`${p.parameter} ${p.notes}`) > 0);

  return { dfm, mesh, process };
}

export function formatDFMRule(rule: DFMRule): string {
  const lines = [`### ${rule.rule}`, `Category: ${rule.category}`, '', rule.details];
  if (rule.typical_range) lines.push(`\nTypical range: ${rule.typical_range}`);
  return lines.join('\n');
}

export function formatMeshGuideline(guide: MeshGuideline): string {
  return `### ${guide.topic} (${guide.mesh_type})\n${guide.recommendation}`;
}

export function formatProcessBound(bound: ProcessBound): string {
  return `### ${bound.parameter} (${bound.unit})\nRange: ${bound.general_min}–${bound.general_max} ${bound.unit}\n${bound.notes}`;
}
