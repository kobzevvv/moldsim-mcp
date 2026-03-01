import { findMaterial, type Material } from '../knowledge/materials.js';

export function compareMaterials(materialIds: string[]): string {
  if (materialIds.length < 2) {
    return 'Please provide at least 2 material IDs to compare.';
  }
  if (materialIds.length > 4) {
    return 'Maximum 4 materials can be compared at once. Please reduce the list.';
  }

  const results: { query: string; material: Material | null }[] = materialIds.map(id => {
    const matches = findMaterial(id);
    return { query: id, material: matches[0] ?? null };
  });

  const notFound = results.filter(r => !r.material);
  if (notFound.length > 0) {
    return [
      `Materials not found: ${notFound.map(r => `"${r.query}"`).join(', ')}`,
      '',
      'Use get_material_properties to list available material IDs.',
    ].join('\n');
  }

  const mats = results.map(r => r.material!);
  const lines: string[] = [];

  lines.push(`# Material Comparison: ${mats.map(m => m.name).join(' vs ')}\n`);

  // General info
  lines.push('## General');
  lines.push(row('Family', mats.map(m => m.family)));
  lines.push(row('Type', mats.map(m => m.type)));
  lines.push(row('Filler', mats.map(m => m.filler ? `${m.filler} (${m.filler_pct}%)` : '—')));

  // Processing window
  lines.push('\n## Processing Window');
  lines.push(row('Melt temp range', mats.map(m => `${m.processing.melt_temp_min_C}–${m.processing.melt_temp_max_C}°C`)));
  lines.push(row('Melt temp (rec)', mats.map(m => `${m.processing.melt_temp_recommended_C}°C`)));
  lines.push(row('Mold temp range', mats.map(m => `${m.processing.mold_temp_min_C}–${m.processing.mold_temp_max_C}°C`)));
  lines.push(row('Mold temp (rec)', mats.map(m => `${m.processing.mold_temp_recommended_C}°C`)));
  lines.push(row('Max shear rate', mats.map(m => `${m.processing.max_shear_rate_1_s} 1/s`)));
  lines.push(row('Drying', mats.map(m =>
    m.processing.drying_temp_C != null
      ? `${m.processing.drying_temp_C}°C / ${m.processing.drying_time_hr}h`
      : 'Not required'
  )));
  lines.push(row('Max residence', mats.map(m => `${m.processing.max_residence_time_min} min`)));

  // Thermal
  lines.push('\n## Thermal Properties');
  lines.push(row('Conductivity', mats.map(m => `${m.thermal.thermal_conductivity_W_mK} W/(m·K)`)));
  lines.push(row('Specific heat', mats.map(m => `${m.thermal.specific_heat_J_kgK} J/(kg·K)`)));
  lines.push(row('Density', mats.map(m => `${m.thermal.density_kg_m3} kg/m³`)));
  lines.push(row('Ejection temp', mats.map(m => `${m.thermal.ejection_temp_C}°C`)));
  lines.push(row('No-flow temp', mats.map(m => `${m.thermal.no_flow_temp_C}°C`)));

  // Mechanical
  lines.push('\n## Mechanical Properties');
  lines.push(row('Tensile strength', mats.map(m => `${m.mechanical.tensile_strength_MPa} MPa`)));
  lines.push(row('Flexural modulus', mats.map(m => `${m.mechanical.flexural_modulus_MPa} MPa`)));
  lines.push(row('Elongation', mats.map(m => `${m.mechanical.elongation_at_break_pct}%`)));
  lines.push(row('HDT @ 1.8 MPa', mats.map(m => `${m.mechanical.HDT_at_1_8MPa_C}°C`)));
  lines.push(row('Shrinkage', mats.map(m => `${m.mechanical.shrinkage_pct_min}–${m.mechanical.shrinkage_pct_max}%`)));

  // Key differences
  lines.push('\n## Key Differences');
  lines.push(...generateKeyDifferences(mats));

  lines.push('\n---');
  lines.push('*Data from MoldSim MCP material database. Verify against supplier datasheets for your specific grade.*');

  return lines.join('\n');
}

function row(label: string, values: string[]): string {
  return `| ${label} | ${values.join(' | ')} |`;
}

function generateKeyDifferences(mats: Material[]): string[] {
  const diffs: string[] = [];

  // Stiffness comparison
  const stiffest = mats.reduce((a, b) => a.mechanical.flexural_modulus_MPa > b.mechanical.flexural_modulus_MPa ? a : b);
  const softest = mats.reduce((a, b) => a.mechanical.flexural_modulus_MPa < b.mechanical.flexural_modulus_MPa ? a : b);
  if (stiffest !== softest) {
    const ratio = (stiffest.mechanical.flexural_modulus_MPa / softest.mechanical.flexural_modulus_MPa).toFixed(1);
    diffs.push(`- **Stiffness**: ${stiffest.name} is ${ratio}× stiffer than ${softest.name}`);
  }

  // Shrinkage comparison
  const highShrink = mats.reduce((a, b) => a.mechanical.shrinkage_pct_max > b.mechanical.shrinkage_pct_max ? a : b);
  const lowShrink = mats.reduce((a, b) => a.mechanical.shrinkage_pct_min < b.mechanical.shrinkage_pct_min ? a : b);
  if (highShrink.mechanical.shrinkage_pct_max > lowShrink.mechanical.shrinkage_pct_min * 2) {
    diffs.push(`- **Shrinkage**: ${highShrink.name} (up to ${highShrink.mechanical.shrinkage_pct_max}%) vs ${lowShrink.name} (as low as ${lowShrink.mechanical.shrinkage_pct_min}%) — mold dimensions differ significantly`);
  }

  // Temperature resistance
  const highHDT = mats.reduce((a, b) => a.mechanical.HDT_at_1_8MPa_C > b.mechanical.HDT_at_1_8MPa_C ? a : b);
  const lowHDT = mats.reduce((a, b) => a.mechanical.HDT_at_1_8MPa_C < b.mechanical.HDT_at_1_8MPa_C ? a : b);
  if (highHDT.mechanical.HDT_at_1_8MPa_C - lowHDT.mechanical.HDT_at_1_8MPa_C > 20) {
    diffs.push(`- **Heat resistance**: ${highHDT.name} (HDT ${highHDT.mechanical.HDT_at_1_8MPa_C}°C) vs ${lowHDT.name} (HDT ${lowHDT.mechanical.HDT_at_1_8MPa_C}°C)`);
  }

  // Drying requirements
  const needsDrying = mats.filter(m => m.processing.drying_temp_C != null);
  const noDrying = mats.filter(m => m.processing.drying_temp_C == null);
  if (needsDrying.length > 0 && noDrying.length > 0) {
    diffs.push(`- **Drying**: ${needsDrying.map(m => m.name).join(', ')} require${needsDrying.length === 1 ? 's' : ''} drying; ${noDrying.map(m => m.name).join(', ')} do${noDrying.length === 1 ? 'es' : ''} not`);
  }

  // Crystallinity
  const amorphous = mats.filter(m => m.type === 'amorphous');
  const crystalline = mats.filter(m => m.type === 'semi-crystalline');
  if (amorphous.length > 0 && crystalline.length > 0) {
    diffs.push(`- **Crystallinity**: ${crystalline.map(m => m.name).join(', ')} = semi-crystalline (higher shrinkage, better chemical resistance); ${amorphous.map(m => m.name).join(', ')} = amorphous (tighter tolerances, transparent possible)`);
  }

  if (diffs.length === 0) {
    diffs.push('- Materials have similar overall properties');
  }

  return diffs;
}
