import { findMaterial, type Material } from '../knowledge/materials.js';
import { DFM_RULES } from '../knowledge/guidelines.js';

export interface DFMInput {
  description: string;
  wall_thickness_mm?: number;
  rib_thickness_mm?: number;
  rib_height_mm?: number;
  draft_angle_deg?: number;
  material?: string;
  has_undercuts?: boolean;
  has_texture?: boolean;
  texture_depth_mm?: number;
  gate_type?: string;
  cosmetic_requirements?: boolean;
}

type CheckStatus = 'pass' | 'warn' | 'fail' | 'info';

interface CheckResult {
  category: string;
  check: string;
  status: CheckStatus;
  detail: string;
}

export function generateDFMChecklist(input: DFMInput): string {
  const mat = input.material ? findMaterial(input.material)[0] : undefined;
  const wall = input.wall_thickness_mm;
  const results: CheckResult[] = [];

  // 1. Wall thickness uniformity
  results.push({
    category: 'Wall Thickness',
    check: 'Uniform wall thickness',
    status: 'info',
    detail: wall
      ? `Nominal wall: ${wall}mm. Maintain ±10% variation throughout part. Use gradual transitions (3:1 taper) where changes are needed.`
      : 'Specify wall thickness for detailed checks. Standard range: 1.0–4.0mm.',
  });

  // 2. Wall thickness range
  if (wall != null) {
    let status: CheckStatus = 'pass';
    let detail: string;
    if (wall < 0.5) {
      status = 'fail';
      detail = `${wall}mm is too thin for conventional injection molding. Minimum ~0.5mm for small parts with easy-flow materials.`;
    } else if (wall < 1.0) {
      status = 'warn';
      detail = `${wall}mm is thin — requires high injection pressure and speed. Verify flow length ratio for material.`;
    } else if (wall > 4.0) {
      status = 'warn';
      detail = `${wall}mm is thick — expect long cycle time, sink marks, and voids. Consider coring out to <4mm.`;
    } else if (wall > 6.0) {
      status = 'fail';
      detail = `${wall}mm is too thick — severe sink marks, voids, and very long cooling. Core out or use gas-assist / structural foam.`;
    } else {
      detail = `${wall}mm is within standard range (1.0–4.0mm).`;
    }
    results.push({ category: 'Wall Thickness', check: 'Wall thickness range', status, detail });
  }

  // 3. Flow length ratio
  if (wall != null && mat) {
    const flowRatios: Record<string, number> = {
      PP: 300, PE: 300, HDPE: 250, LDPE: 300,
      ABS: 200, PS: 250, HIPS: 250, SAN: 180,
      PC: 100, PMMA: 130, POM: 150,
      PA: 150, PBT: 150, PET: 120,
      TPU: 150, ASA: 200, PPE: 120,
    };
    const ratio = flowRatios[mat.family] ?? 200;
    results.push({
      category: 'Wall Thickness',
      check: 'Flow length/thickness ratio',
      status: 'info',
      detail: `Max flow-length-to-thickness ratio for ${mat.family}: ~${ratio}:1. At ${wall}mm wall, max flow length ~${(ratio * wall).toFixed(0)}mm before needing additional gates.`,
    });
  }

  // 4. Rib thickness
  if (input.rib_thickness_mm != null && wall != null) {
    const ratio = input.rib_thickness_mm / wall;
    let status: CheckStatus;
    let detail: string;
    if (ratio <= 0.6) {
      status = 'pass';
      detail = `Rib thickness ${input.rib_thickness_mm}mm = ${(ratio * 100).toFixed(0)}% of wall (${wall}mm). Within 50-60% guideline.`;
    } else if (ratio <= 0.75) {
      status = 'warn';
      detail = `Rib thickness ${input.rib_thickness_mm}mm = ${(ratio * 100).toFixed(0)}% of wall. Slightly above 60% — may cause visible sink marks on opposite side.`;
    } else {
      status = 'fail';
      detail = `Rib thickness ${input.rib_thickness_mm}mm = ${(ratio * 100).toFixed(0)}% of wall. Exceeds 60% guideline — sink marks likely. Reduce to ${(wall * 0.5).toFixed(1)}–${(wall * 0.6).toFixed(1)}mm.`;
    }
    results.push({ category: 'Ribs', check: 'Rib thickness ratio', status, detail });
  }

  // 5. Rib height
  if (input.rib_height_mm != null && wall != null) {
    const ratio = input.rib_height_mm / wall;
    let status: CheckStatus;
    let detail: string;
    if (ratio <= 3.0) {
      status = 'pass';
      detail = `Rib height ${input.rib_height_mm}mm = ${ratio.toFixed(1)}× wall thickness. Within 3× guideline.`;
    } else if (ratio <= 5.0) {
      status = 'warn';
      detail = `Rib height ${input.rib_height_mm}mm = ${ratio.toFixed(1)}× wall thickness. Exceeds 3× — may be hard to fill and eject. Ensure adequate draft.`;
    } else {
      status = 'fail';
      detail = `Rib height ${input.rib_height_mm}mm = ${ratio.toFixed(1)}× wall thickness. Far exceeds 3× guideline — filling, ejection, and warpage issues likely. Use multiple shorter ribs instead.`;
    }
    results.push({ category: 'Ribs', check: 'Rib height ratio', status, detail });
  }

  // 6. Draft angle
  if (input.draft_angle_deg != null) {
    let status: CheckStatus;
    let detail: string;
    const minDraft = input.has_texture && input.texture_depth_mm
      ? 1.0 + (input.texture_depth_mm / 0.025)
      : 1.0;

    if (input.draft_angle_deg >= minDraft) {
      status = 'pass';
      detail = `Draft angle ${input.draft_angle_deg}° meets minimum ${minDraft}°.`;
    } else if (input.draft_angle_deg >= 0.5) {
      status = 'warn';
      detail = `Draft angle ${input.draft_angle_deg}° is below recommended ${minDraft}°. May cause ejection issues${input.has_texture ? ' especially with textured surfaces' : ''}.`;
    } else {
      status = 'fail';
      detail = `Draft angle ${input.draft_angle_deg}° is too low. Minimum ${minDraft}° required${input.has_texture ? ` (includes texture depth compensation)` : ''}. Risk: part sticking, scuffing, mold damage.`;
    }
    results.push({ category: 'Draft', check: 'Draft angle', status, detail });
  } else {
    results.push({
      category: 'Draft',
      check: 'Draft angle',
      status: 'info',
      detail: `Apply minimum 1° draft on all surfaces parallel to mold opening direction. Textured surfaces need more: add 1° per 0.025mm texture depth.`,
    });
  }

  // 7. Corner radii
  results.push({
    category: 'Radii',
    check: 'Internal corner radii',
    status: 'info',
    detail: wall
      ? `Use minimum internal radius of ${(wall * 0.5).toFixed(1)}mm (50% of wall). External radius should be ${(wall * 1.5).toFixed(1)}mm (internal + wall). Reduces stress concentration by ~50%.`
      : 'Internal radius should be 50-75% of wall thickness. Sharp corners create 2-3× stress concentration.',
  });

  // 8. Undercuts
  if (input.has_undercuts === true) {
    results.push({
      category: 'Undercuts',
      check: 'Undercut features',
      status: 'warn',
      detail: 'Part has undercuts — requires side actions, slides, or lifters in mold. Increases tooling cost 15-30%. Consider redesigning with snap-fits that can be stripped if material is flexible enough.',
    });
  } else if (input.has_undercuts === false) {
    results.push({
      category: 'Undercuts',
      check: 'Undercut features',
      status: 'pass',
      detail: 'No undercuts — simpler tooling, lower mold cost.',
    });
  }

  // 9. Gate placement
  if (input.gate_type) {
    const gateInfo: Record<string, string> = {
      edge: 'Edge gate: simple, easy to trim. Gate vestige visible. Best for flat parts.',
      sub: 'Submarine gate: auto-degates on ejection. Small vestige. Good for automated production.',
      pin: 'Pin-point gate: minimal vestige. Requires 3-plate mold. Higher mold cost.',
      hot: 'Hot runner: no runner waste, consistent filling. Highest mold cost. Best for high-volume production.',
      fan: 'Fan gate: wide, uniform flow front. Reduces weld lines. Good for flat parts with cosmetic requirements.',
      tunnel: 'Tunnel/cashew gate: auto-degates. Can gate below parting line. Complex geometry.',
    };
    const info = gateInfo[input.gate_type.toLowerCase()] ?? `${input.gate_type} gate specified.`;
    results.push({
      category: 'Gating',
      check: 'Gate type',
      status: 'info',
      detail: `${info} Gate thickness should be 50-80% of wall thickness${wall ? ` (${(wall * 0.5).toFixed(1)}–${(wall * 0.8).toFixed(1)}mm)` : ''}.`,
    });
  }

  // 10. Gate into thickest section
  results.push({
    category: 'Gating',
    check: 'Gate location — thick section',
    status: 'info',
    detail: 'Gate must feed into the thickest section. Flow path should go thick-to-thin to avoid hesitation and short shots.',
  });

  // 11. Sink mark risk
  if (wall != null) {
    const hasSinkRisk = (input.rib_thickness_mm != null && input.rib_thickness_mm / wall > 0.6) || wall > 3.0;
    results.push({
      category: 'Surface Quality',
      check: 'Sink mark risk',
      status: hasSinkRisk ? 'warn' : 'pass',
      detail: hasSinkRisk
        ? `Sink marks likely due to ${wall > 3.0 ? 'thick wall sections' : 'rib thickness exceeding 60% of wall'}. Mitigation: increase packing, texture surface, or redesign thick sections.`
        : 'Low sink mark risk based on current geometry.',
    });
  }

  // 12. Weld line considerations
  results.push({
    category: 'Surface Quality',
    check: 'Weld line positioning',
    status: 'info',
    detail: mat
      ? `${mat.name}: weld line strength ~${mat.type === 'semi-crystalline' ? '70-80' : '85-95'}%${mat.filler ? ' (filled materials: 50-60%)' : ''} of bulk. Position away from structural/cosmetic areas.`
      : 'Weld lines form where flow fronts meet. Strength: amorphous 85-95%, semi-crystalline 70-80%, filled 50-60% of bulk.',
  });

  // 13. Venting
  if (mat) {
    const ventDepths: Record<string, string> = {
      amorphous: '0.02–0.05mm',
      'semi-crystalline': '0.01–0.02mm',
    };
    const depth = mat.filler ? '0.01–0.015mm' : (ventDepths[mat.type] ?? '0.02–0.04mm');
    results.push({
      category: 'Venting',
      check: 'Vent depth for material',
      status: 'info',
      detail: `${mat.name} (${mat.type}${mat.filler ? ', filled' : ''}): recommended vent depth ${depth}. Land length 1-2mm, then relief to atmosphere. Vents at parting line, end of fill, and weld line locations.`,
    });
  }

  // 14. Shrinkage compensation
  if (mat) {
    results.push({
      category: 'Tolerances',
      check: 'Shrinkage compensation',
      status: mat.mechanical.shrinkage_pct_max > 1.5 ? 'warn' : 'info',
      detail: `${mat.name}: shrinkage ${mat.mechanical.shrinkage_pct_min}–${mat.mechanical.shrinkage_pct_max}%.${mat.mechanical.shrinkage_pct_max > 1.5 ? ' High shrinkage — tight tolerances will be difficult.' : ''} Mold cavity oversized by shrinkage factor.${mat.filler ? ' Anisotropic shrinkage (lower in flow direction).' : ''}`,
    });
  }

  // 15. Material-specific drying
  if (mat && mat.processing.drying_temp_C != null) {
    results.push({
      category: 'Material',
      check: 'Drying requirement',
      status: 'warn',
      detail: `${mat.name} is hygroscopic — MUST dry before molding: ${mat.processing.drying_temp_C}°C for ${mat.processing.drying_time_hr}h minimum. Failure to dry causes splay, bubbles, and mechanical property loss.`,
    });
  }

  // 16. Ejection considerations
  results.push({
    category: 'Ejection',
    check: 'Ejector pin placement',
    status: 'info',
    detail: wall
      ? `Place ejector pins on flat surfaces, ribs, and edges. Pin diameter should be ≥${Math.max(3, wall * 2).toFixed(0)}mm to avoid punch-through. Avoid placing on cosmetic surfaces.`
      : 'Ensure sufficient ejector pin area to avoid part deformation during ejection. Pins on ribs and structural features.',
  });

  // Format output
  return formatChecklist(results, mat, input);
}

function formatChecklist(results: CheckResult[], mat: Material | undefined, input: DFMInput): string {
  const lines: string[] = [];
  const icons: Record<CheckStatus, string> = { pass: 'PASS', warn: 'WARN', fail: 'FAIL', info: 'INFO' };

  lines.push('# DFM Checklist\n');

  if (mat) {
    lines.push(`Material: **${mat.name}** (${mat.family}, ${mat.type})`);
  }
  if (input.wall_thickness_mm) {
    lines.push(`Wall thickness: **${input.wall_thickness_mm}mm**`);
  }
  lines.push('');

  // Summary
  const fails = results.filter(r => r.status === 'fail').length;
  const warns = results.filter(r => r.status === 'warn').length;
  const passes = results.filter(r => r.status === 'pass').length;
  lines.push(`## Summary: ${fails} FAIL, ${warns} WARN, ${passes} PASS\n`);

  // Group by category
  const categories = [...new Set(results.map(r => r.category))];
  for (const cat of categories) {
    lines.push(`## ${cat}`);
    const catResults = results.filter(r => r.category === cat);
    for (const r of catResults) {
      lines.push(`[${icons[r.status]}] **${r.check}**`);
      lines.push(`  ${r.detail}\n`);
    }
  }

  lines.push('---');
  lines.push('*Generated by MoldSim MCP. Consult with mold designer for final validation.*');

  return lines.join('\n');
}
