/**
 * Injection molding simulation troubleshooting knowledge base.
 * Common defects, simulation artifacts, and their solutions.
 */

export interface TroubleshootingEntry {
  id: string;
  category: 'defect' | 'simulation' | 'process' | 'material';
  problem: string;
  keywords: string[];
  symptoms: string[];
  causes: string[];
  solutions: string[];
  simulation_check: string[];
}

export const TROUBLESHOOTING: TroubleshootingEntry[] = [
  // ──── Part Defects ────
  {
    id: 'short-shot',
    category: 'defect',
    problem: 'Short shot — part not fully filled',
    keywords: ['short shot', 'incomplete fill', 'unfilled', 'not filling', 'hesitation'],
    symptoms: [
      'Part is missing material in thin sections or far from gate',
      'Inconsistent fill across cavities in multi-cavity mold',
    ],
    causes: [
      'Insufficient injection pressure or speed',
      'Melt temperature too low — high viscosity',
      'Gate or runner too small — pressure drop',
      'Trapped air preventing fill (no venting)',
      'Wall thickness too thin relative to flow length',
    ],
    solutions: [
      'Increase injection speed and/or pressure',
      'Raise melt temperature within processing window',
      'Enlarge gate, runner, or add additional gates',
      'Add or enlarge vents (0.01-0.03 mm for most resins)',
      'Increase wall thickness in thin sections if design allows',
      'Switch to higher MFI grade of same material',
    ],
    simulation_check: [
      'Run fill analysis — check pressure at end of fill vs machine capacity',
      'Check fill time contour for hesitation marks',
      'Verify venting locations with air trap analysis',
      'Review clamp force — may indicate pressure limitations',
    ],
  },
  {
    id: 'flash',
    category: 'defect',
    problem: 'Flash — excess material at parting line',
    keywords: ['flash', 'flashing', 'parting line', 'overflow', 'excess material'],
    symptoms: [
      'Thin film of plastic at mold parting line or around inserts',
      'Flash at ejector pin locations',
    ],
    causes: [
      'Excessive injection or packing pressure',
      'Insufficient clamp tonnage',
      'Mold wear or damage — parting line gap',
      'Melt temperature too high — low viscosity',
      'Excessive packing time',
    ],
    solutions: [
      'Reduce injection and packing pressure',
      'Verify clamp force requirement (rule: 2-5 tons/in² projected area)',
      'Check and repair mold parting surfaces',
      'Lower melt temperature',
      'Reduce packing time and switch to gate-freeze-controlled packing',
    ],
    simulation_check: [
      'Check clamp force vs machine capacity — add 10-20% safety margin',
      'Run packing analysis — monitor pressure at parting line',
      'Use pressure distribution plot at V/P switchover point',
    ],
  },
  {
    id: 'sink-marks',
    category: 'defect',
    problem: 'Sink marks — surface depressions',
    keywords: ['sink', 'sink mark', 'depression', 'dimple', 'surface depression'],
    symptoms: [
      'Visible depressions on part surface, typically opposite ribs or bosses',
      'Surface not cosmetically acceptable',
    ],
    causes: [
      'Insufficient packing pressure or time',
      'Rib-to-wall ratio too high (>60% of wall thickness)',
      'Excessive wall thickness — long cooling time',
      'Gate freeze-off too early — cannot pack thick sections',
      'Melt temperature too high — more volumetric shrinkage',
    ],
    solutions: [
      'Increase packing pressure and duration',
      'Reduce rib thickness to ≤60% of nominal wall (50% preferred)',
      'Core out thick sections to create uniform wall thickness',
      'Enlarge gate or move gate closer to thick sections',
      'Lower melt temperature (within processing window)',
      'Consider gas/water-assist for thick sections',
    ],
    simulation_check: [
      'Run shrinkage analysis — check volumetric shrinkage contour',
      'Sink mark indicator plot in packing analysis',
      'Verify gate freeze-off time vs packing hold time',
      'Check pressure at end-of-fill in thick sections',
    ],
  },
  {
    id: 'warpage',
    category: 'defect',
    problem: 'Warpage — part distortion after ejection',
    keywords: ['warp', 'warpage', 'bow', 'twist', 'distortion', 'flatness', 'bent'],
    symptoms: [
      'Part does not meet dimensional tolerances after cooling',
      'Bowing, twisting, or corner lifting',
    ],
    causes: [
      'Non-uniform cooling — differential shrinkage',
      'Fiber orientation effects (filled materials)',
      'Residual stress from packing pressure gradient',
      'Asymmetric part geometry or wall thickness',
      'Unbalanced runner system in multi-cavity',
      'Ejection before adequate cooling',
    ],
    solutions: [
      'Balance cooling circuits — equalize temperatures on both mold halves',
      'Optimize gate location for balanced fill and uniform fiber orientation',
      'Increase cooling time until part is dimensionally stable',
      'Reduce packing pressure differential across part',
      'Add ribs or geometry stiffeners if design permits',
      'For glass-filled: consider gate placement to control fiber orientation',
    ],
    simulation_check: [
      'Warpage analysis with all 3 contributors: differential shrinkage, differential cooling, orientation',
      'Deflection plot — identify dominant warpage direction',
      'Cooling analysis — ΔT between core and cavity should be <5°C',
      'Fiber orientation tensor for filled materials',
    ],
  },
  {
    id: 'weld-lines',
    category: 'defect',
    problem: 'Weld/knit lines — visible lines where flow fronts meet',
    keywords: ['weld line', 'knit line', 'flow line', 'meeting', 'confluence'],
    symptoms: [
      'Visible line on part surface where two flow fronts merged',
      'Reduced mechanical strength at weld line location',
    ],
    causes: [
      'Multiple gates creating opposing flow fronts',
      'Flow splitting around holes, pins, or cores',
      'Low melt temperature at meeting point — poor fusion',
      'Trapped air at confluence — prevents bonding',
    ],
    solutions: [
      'Relocate gates to move weld lines to non-critical areas',
      'Increase melt temperature to improve fusion at weld',
      'Increase injection speed to maintain melt front temperature',
      'Add overflow well near weld to push contaminated material out',
      'Vent at weld line locations',
      'Use sequential valve gating to eliminate opposing fronts',
    ],
    simulation_check: [
      'Weld line location plot — overlay with critical stress areas',
      'Temperature at flow front (TAFT) — should be above no-flow temp',
      'Check pressure at weld formation point',
    ],
  },
  {
    id: 'burn-marks',
    category: 'defect',
    problem: 'Burn marks / dieseling',
    keywords: ['burn', 'diesel', 'char', 'black spot', 'discoloration', 'gas burn'],
    symptoms: [
      'Brown or black marks at end of fill or in corners',
      'Characteristic smell of burned plastic',
    ],
    causes: [
      'Trapped air compressed adiabatically (diesel effect)',
      'Injection speed too high in final fill phase',
      'Insufficient venting',
      'Excessive shear heating at gate or thin sections',
    ],
    solutions: [
      'Add or enlarge vents at burn locations (parting line, ejector pins)',
      'Reduce injection speed, especially near end of fill (multi-stage injection)',
      'Lower melt temperature',
      'Reduce clamp force if over-clamped (may compress vents)',
      'Vacuum venting for deep ribs or difficult geometries',
    ],
    simulation_check: [
      'Air trap analysis — identify trapped air locations',
      'Temperature contour at end of fill — any shear-heated regions >degradation temp?',
      'Shear rate plot — verify within material limits',
    ],
  },
  {
    id: 'jetting',
    category: 'defect',
    problem: 'Jetting — snake-like pattern on surface',
    keywords: ['jet', 'jetting', 'snake', 'worm track', 'serpentine'],
    symptoms: [
      'Wavy, snake-like marks starting from gate',
      'Surface roughness near gate area',
    ],
    causes: [
      'Material jets through gate without contacting mold wall',
      'Gate too small relative to cavity thickness',
      'Injection speed too high at gate entry',
      'Gate positioned opposite to thick wall — free stream',
    ],
    solutions: [
      'Redesign gate to direct flow against a wall (fan gate, tab gate)',
      'Reduce initial injection speed (use slow-fast profile)',
      'Enlarge gate opening',
      'Move gate to impinge on cavity wall at an angle',
    ],
    simulation_check: [
      'Fill animation — look for free jet pattern in early fill',
      'Gate shear rate — verify within material limits',
      'Flow front advancement near gate',
    ],
  },
  {
    id: 'splay',
    category: 'defect',
    problem: 'Splay / silver streaks',
    keywords: ['splay', 'silver', 'streak', 'moisture', 'splash mark'],
    symptoms: [
      'Silver streaks radiating from gate on part surface',
      'Surface appears rough or hazy',
    ],
    causes: [
      'Moisture in material — steam creates bubbles at flow front',
      'Material degradation — volatiles',
      'Excessive shear heating at gate',
      'Air entrainment in barrel (screw recovery too fast)',
    ],
    solutions: [
      'Dry material properly (check specific drying requirements)',
      'Reduce melt temperature if degradation suspected',
      'Reduce injection speed at gate to minimize shear',
      'Reduce screw RPM and back pressure to avoid air entrainment',
      'Use hopper dryer with dew point monitoring',
    ],
    simulation_check: [
      'Check if material is hygroscopic (see material card)',
      'Shear rate at gate — compare to max recommended',
      'Bulk temperature — any regions exceeding degradation limit?',
    ],
  },
  {
    id: 'voids',
    category: 'defect',
    problem: 'Voids / internal bubbles',
    keywords: ['void', 'bubble', 'vacuum void', 'internal hole', 'porosity'],
    symptoms: [
      'Internal bubbles visible in transparent parts or on cut sections',
      'Reduced mechanical properties',
    ],
    causes: [
      'Thick sections shrink internally — packing cannot compensate',
      'Gate freeze-off before thick section solidifies',
      'Insufficient packing pressure',
      'Moisture (creates gas bubbles, not vacuum voids)',
    ],
    solutions: [
      'Increase packing pressure and time — ensure gate stays open',
      'Enlarge gate for longer packing path',
      'Reduce wall thickness — core out thick sections',
      'Move gate closer to thick sections',
      'For thick parts: consider gas-assist or structural foam',
    ],
    simulation_check: [
      'Volumetric shrinkage contour — voids where >8% shrinkage',
      'Packing pressure transmission — any isolated thick regions?',
      'Gate freeze time vs packing time',
    ],
  },
  {
    id: 'flow-marks',
    category: 'defect',
    problem: 'Flow marks / record grooves',
    keywords: ['flow mark', 'record groove', 'wave', 'ripple', 'tiger stripe'],
    symptoms: [
      'Wavy pattern or concentric rings on part surface',
      'Alternating dull/glossy bands (tiger stripes on PP)',
    ],
    causes: [
      'Fountain flow instability at low speeds',
      'Melt front freezes and re-melts cyclically',
      'Material sticking/slipping at mold surface',
      'Mold temperature too low',
    ],
    solutions: [
      'Increase injection speed for consistent flow front',
      'Raise mold temperature (improves surface replication)',
      'Increase melt temperature slightly',
      'Use textured surface to hide marks',
      'For tiger stripes on PP: raise mold temp to 50-60°C',
    ],
    simulation_check: [
      'Flow front velocity contour — look for deceleration zones',
      'Melt front temperature — regions below no-flow temp',
      'Fill pattern animation — unsteady front advancement',
    ],
  },

  // ──── Simulation-Specific Issues ────
  {
    id: 'sim-mesh-sensitivity',
    category: 'simulation',
    problem: 'Results change with mesh refinement',
    keywords: ['mesh sensitivity', 'convergence', 'mesh size', 'element size', 'refinement'],
    symptoms: [
      'Pressure, temperature, or shrinkage results change >5% when mesh is refined',
      'Different results with different mesh densities',
    ],
    causes: [
      'Mesh too coarse — insufficient elements through thickness',
      'Poor element quality (high aspect ratio, skewed elements)',
      'Thin sections with only 1-2 elements through thickness',
      'Sharp corners without mesh refinement',
    ],
    solutions: [
      'Use at least 4 layers through thickness for midplane/dual-domain',
      'For 3D mesh: minimum 4 elements through wall thickness, 8+ preferred',
      'Refine mesh at gates, thin sections, and sharp corners',
      'Run mesh convergence study: coarse → medium → fine until <2% change',
      'Target aspect ratio <6:1, match count ratio 85%+ for dual-domain',
    ],
    simulation_check: [
      'Mesh statistics: element count, aspect ratio, match ratio',
      'Run at 2 mesh levels and compare key results (fill pressure, clamp force)',
      'Check elements through thickness in thin regions',
    ],
  },
  {
    id: 'sim-race-tracking',
    category: 'simulation',
    problem: 'Race-tracking / unexpected fill pattern',
    keywords: ['race track', 'race tracking', 'unbalanced fill', 'fast flow', 'hesitation'],
    symptoms: [
      'Material flows preferentially along thick sections or ribs',
      'Thin areas fill last despite being close to gate',
    ],
    causes: [
      'Thick-to-thin wall transitions create preferential flow paths',
      'Runner system not balanced',
      'Geometry features (ribs, flanges) acting as flow leaders',
    ],
    solutions: [
      'Redesign wall thickness for uniformity (gradual transitions)',
      'Use flow leaders or flow deflectors intentionally',
      'Balance runner system (naturally or with flow restrictors)',
      'Move gate to promote more uniform fill',
      'Consider sequential valve gating for large parts',
    ],
    simulation_check: [
      'Fill time contour — identify race tracking paths',
      'Pressure distribution at multiple fill percentages (25%, 50%, 75%)',
      'Flow front velocity contour — high velocity = race tracking',
    ],
  },
  {
    id: 'sim-cooling-imbalance',
    category: 'simulation',
    problem: 'Cooling imbalance / hot spots',
    keywords: ['cooling', 'hot spot', 'cold spot', 'cooling line', 'cycle time', 'temperature'],
    symptoms: [
      'Part surface temperature varies >10°C at end of cooling',
      'Ejection marks or sticking on hot side',
      'Excessive cycle time to achieve uniform part temperature',
    ],
    causes: [
      'Cooling lines too far from cavity surface',
      'Uneven spacing of cooling channels',
      'Core side lacks cooling or has restricted flow',
      'Hot runner system heat interfering with mold cooling',
    ],
    solutions: [
      'Place cooling channels 1-2× diameter from cavity surface',
      'Channel spacing ≤3× diameter for uniform cooling',
      'Use baffles, bubblers, or conformal cooling for cores',
      'Separate cooling circuits for core and cavity',
      'Add insulation around hot runner manifold',
      'Target ΔT < 5°C across part surface at ejection',
    ],
    simulation_check: [
      'Cooling analysis — circuit temperature rise (in-out ΔT < 3°C per circuit)',
      'Part surface temperature contour at ejection time',
      'Time to reach ejection temperature — identifies bottleneck',
      'Heat flux from part to coolant — uniform target',
    ],
  },
  {
    id: 'sim-overpacking',
    category: 'simulation',
    problem: 'Overpacking near gate',
    keywords: ['overpacking', 'overpack', 'gate area', 'high pressure', 'residual stress'],
    symptoms: [
      'High residual stress near gate region',
      'Excessive clamp force during packing',
      'Gate blush or gate vestige',
    ],
    causes: [
      'Packing pressure too high or too long',
      'Single-step packing profile — no pressure reduction',
      'Gate too large — packing transmits directly',
    ],
    solutions: [
      'Use multi-step packing profile: high → medium → low',
      'Reduce packing pressure to 40-60% of peak injection pressure',
      'Profile packing: start at 80% and step down to 40%',
      'Optimize gate size — balance packing vs gate vestige',
    ],
    simulation_check: [
      'Volumetric shrinkage contour — negative shrinkage = overpacked',
      'Packing pressure distribution — gradient from gate to end-of-flow',
      'Residual stress plot — highest near gate indicates overpacking',
    ],
  },
  {
    id: 'sim-shear-rate-exceeded',
    category: 'simulation',
    problem: 'Shear rate exceeding material limit',
    keywords: ['shear rate', 'shear stress', 'gate shear', 'degradation'],
    symptoms: [
      'Shear rate result exceeds material maximum at gate or thin section',
      'Part shows splay, burn marks, or material degradation near gate',
    ],
    causes: [
      'Gate too small for selected injection speed',
      'Injection speed too high',
      'Runner cross-section too small',
      'Thin wall section acts as restriction',
    ],
    solutions: [
      'Enlarge gate cross-section',
      'Reduce injection speed (use multi-stage profile)',
      'Increase runner diameter',
      'Consider multiple gates to reduce flow rate per gate',
    ],
    simulation_check: [
      'Shear rate at gate — compare to material max (see material properties)',
      'Bulk temperature at gate — check for shear-induced heating',
      'Use shear rate result to identify all exceedance locations',
    ],
  },

  // ──── Process Optimization ────
  {
    id: 'proc-cycle-time',
    category: 'process',
    problem: 'Excessive cycle time',
    keywords: ['cycle time', 'productivity', 'throughput', 'cooling time', 'fast cycle'],
    symptoms: [
      'Cycle time longer than expected for similar parts',
      'Cooling phase dominates cycle time',
    ],
    causes: [
      'Cooling time driven by thickest section',
      'Mold temperature too high',
      'Inadequate cooling circuit design',
      'Packing time exceeds gate freeze time',
    ],
    solutions: [
      'Core out thick sections to reduce maximum wall thickness',
      'Optimize cooling circuit layout',
      'Lower mold temperature (check surface quality impact)',
      'Match packing time to gate freeze time — no benefit from longer packing',
      'Consider high-conductivity mold inserts (Cu-Be) for hot spots',
      'Formula: cooling_time ≈ (wall_thickness²) / (π² × thermal_diffusivity) × ln(8/π² × (Tmelt-Tmold)/(Teject-Tmold))',
    ],
    simulation_check: [
      'Time to reach ejection temperature — which region is last?',
      'Gate freeze time from packing analysis',
      'Cooling circuit efficiency — Reynolds number should be >10000 (turbulent)',
    ],
  },
  {
    id: 'proc-gate-location',
    category: 'process',
    problem: 'Suboptimal gate location',
    keywords: ['gate', 'gate location', 'gate position', 'gate type', 'best gate'],
    symptoms: [
      'Unbalanced fill pattern',
      'Excessive pressure drop',
      'Cosmetic defects near gate area',
      'Weld lines in critical areas',
    ],
    causes: [
      'Gate placed at thin section instead of thick',
      'Gate location causing long flow paths',
      'Multiple gates creating problematic weld lines',
    ],
    solutions: [
      'Gate at thickest section — flow from thick to thin',
      'Gate for balanced fill (equal flow length in all directions)',
      'Keep weld lines away from structural/cosmetic areas',
      'For multi-gate: use sequential valve gating',
      'Consider gate type: edge < fan < tunnel < hot tip (cosmetic impact)',
      'Use gate location analysis tool in simulation software',
    ],
    simulation_check: [
      'Run gate location analysis (automatic gate suggestion)',
      'Compare fill balance with different gate positions',
      'Check pressure at fill for each gate scenario',
      'Evaluate weld line positions for each option',
    ],
  },
  {
    id: 'proc-vp-switchover',
    category: 'process',
    problem: 'V/P switchover optimization',
    keywords: ['switchover', 'velocity pressure', 'V/P', 'transfer', 'fill to pack'],
    symptoms: [
      'Inconsistent part weight shot-to-shot',
      'Flash or short shots intermittently',
      'Pressure spike at switchover',
    ],
    causes: [
      'Switchover position not matched to cavity fill',
      'Volume-based switchover unreliable with check ring wear',
      'Switchover too early = short shot, too late = pressure spike',
    ],
    solutions: [
      'Switch at 95-99% volumetric fill (before cavity is fully packed)',
      'Use cavity pressure sensor for consistent switchover',
      'Set switchover based on pressure, not position, for consistency',
      'Fill study: short shots at increasing volumes to find exact fill point',
    ],
    simulation_check: [
      'Fill analysis — note exact fill volume and pressure at 98% fill',
      'Pressure trace at switchover — should be smooth transition',
      'Compare part weight at different switchover positions',
    ],
  },

  // ──── Material-Related ────
  {
    id: 'mat-degradation',
    category: 'material',
    problem: 'Material degradation',
    keywords: ['degradation', 'decomposition', 'yellowing', 'browning', 'thermal damage'],
    symptoms: [
      'Discoloration (yellowing, browning) of molded part',
      'Reduced mechanical properties',
      'Characteristic smell (formaldehyde for POM, amines for PA)',
    ],
    causes: [
      'Barrel temperature exceeding material degradation limit',
      'Excessive residence time in barrel',
      'Shear heating adding to bulk temperature',
      'Dead spots in barrel or hot runner',
    ],
    solutions: [
      'Lower melt temperature within processing window',
      'Reduce cycle time or use smaller barrel to limit residence time',
      'Check and clean hot runner system for dead spots',
      'For POM: never exceed 220°C, purge with PE before shutdown',
      'For PA: dry properly, use nitrogen blanket in hopper',
    ],
    simulation_check: [
      'Bulk temperature plot — regions above degradation limit',
      'Residence time analysis — max time in barrel',
      'Temperature at flow front — detect shear heating',
    ],
  },
  {
    id: 'mat-crystallization',
    category: 'material',
    problem: 'Crystallization control issues',
    keywords: ['crystallization', 'crystallinity', 'amorphous', 'transparent', 'opaque', 'haze'],
    symptoms: [
      'Inconsistent shrinkage across part',
      'Unexpected opacity or haze in semi-crystalline parts',
      'Part warpage from uneven crystallization',
    ],
    causes: [
      'Non-uniform cooling rates → different crystallinity levels',
      'Mold temperature affects final crystallinity (higher = more crystalline)',
      'Thick sections cool slower = higher crystallinity = more shrinkage',
    ],
    solutions: [
      'For consistent crystallinity: uniform cooling and wall thickness',
      'Higher mold temp → higher crystallinity, better surface, more shrinkage',
      'Lower mold temp → lower crystallinity, less shrinkage, may be brittle',
      'For PET: cold mold (30°C) = amorphous clear, hot mold (140°C) = crystalline opaque',
      'Nucleating agents can accelerate crystallization and reduce sensitivity',
    ],
    simulation_check: [
      'Crystallinity distribution from cooling analysis',
      'Cooling rate contour — uniform target',
      'Volumetric shrinkage — correlates with crystallinity',
    ],
  },
  {
    id: 'mat-fiber-orientation',
    category: 'material',
    problem: 'Fiber orientation effects (filled materials)',
    keywords: ['fiber', 'glass fiber', 'orientation', 'anisotropic', 'filled', 'GF'],
    symptoms: [
      'Anisotropic shrinkage (different in flow vs cross-flow)',
      'Warpage in directions not expected from geometry alone',
      'Weak weld lines in structural areas',
    ],
    causes: [
      'Glass fibers align with flow direction during filling',
      'Shrinkage is low in fiber direction, high perpendicular to fibers',
      'Weld lines have perpendicular fiber orientation → very weak',
    ],
    solutions: [
      'Optimize gate position to control fiber orientation in critical areas',
      'Use simulation to predict orientation tensor and resulting warpage',
      'For structural weld lines: consider flow leaders to change orientation at weld',
      'Consider lower fiber content or shorter fibers for less anisotropy',
      'Use symmetrical gate layout for symmetrical parts',
    ],
    simulation_check: [
      'Fiber orientation tensor (a11, a22, a33 components)',
      'Shrinkage: separate in-flow vs cross-flow values',
      'Warpage analysis with fiber orientation contribution enabled',
      'Mechanical property prediction (anisotropic stiffness)',
    ],
  },
];

/** Search troubleshooting entries by keyword match. */
export function searchTroubleshooting(query: string): TroubleshootingEntry[] {
  const q = query.toLowerCase();
  const terms = q.split(/\s+/).filter(t => t.length > 2);

  return TROUBLESHOOTING
    .map(entry => {
      const searchText = [
        entry.problem,
        ...entry.keywords,
        ...entry.symptoms,
        ...entry.causes,
        ...entry.solutions,
      ].join(' ').toLowerCase();

      const score = terms.reduce((sum, term) => {
        if (entry.keywords.some(k => k.includes(term))) return sum + 3;
        if (entry.problem.toLowerCase().includes(term)) return sum + 2;
        if (searchText.includes(term)) return sum + 1;
        return sum;
      }, 0);

      return { entry, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ entry }) => entry);
}

export function formatTroubleshooting(entry: TroubleshootingEntry): string {
  const lines: string[] = [];
  lines.push(`# ${entry.problem}`);
  lines.push(`Category: ${entry.category}\n`);

  lines.push(`## Symptoms`);
  entry.symptoms.forEach(s => lines.push(`- ${s}`));

  lines.push(`\n## Root Causes`);
  entry.causes.forEach(c => lines.push(`- ${c}`));

  lines.push(`\n## Solutions`);
  entry.solutions.forEach(s => lines.push(`- ${s}`));

  lines.push(`\n## Simulation Checks`);
  entry.simulation_check.forEach(c => lines.push(`- ${c}`));

  return lines.join('\n');
}
