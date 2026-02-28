import { findMaterial } from '../knowledge/materials.js';

export interface ValidationInput {
  material: string;
  melt_temp_C?: number;
  mold_temp_C?: number;
  injection_speed_mm_s?: number;
  packing_pressure_MPa?: number;
  wall_thickness_mm?: number;
  cooling_time_s?: number;
}

interface Warning {
  level: 'error' | 'warning' | 'info';
  parameter: string;
  message: string;
  suggestion: string;
}

export function validateProcessParameters(input: ValidationInput): string {
  const matches = findMaterial(input.material);

  if (matches.length === 0) {
    return `Material "${input.material}" not found in database. Cannot validate parameters. Use get_material_properties to list available materials.`;
  }

  const mat = matches[0];
  const proc = mat.processing;
  const warnings: Warning[] = [];

  // Melt temperature
  if (input.melt_temp_C != null) {
    if (input.melt_temp_C < proc.melt_temp_min_C) {
      warnings.push({
        level: 'error',
        parameter: 'melt_temp_C',
        message: `${input.melt_temp_C}°C is below minimum (${proc.melt_temp_min_C}°C) for ${mat.name}`,
        suggestion: `Increase melt temperature to at least ${proc.melt_temp_min_C}°C. Recommended: ${proc.melt_temp_recommended_C}°C. Risk: high viscosity, short shots, poor surface.`,
      });
    } else if (input.melt_temp_C > proc.melt_temp_max_C) {
      warnings.push({
        level: 'error',
        parameter: 'melt_temp_C',
        message: `${input.melt_temp_C}°C exceeds maximum (${proc.melt_temp_max_C}°C) for ${mat.name}`,
        suggestion: `Reduce melt temperature to at most ${proc.melt_temp_max_C}°C. Recommended: ${proc.melt_temp_recommended_C}°C. Risk: material degradation, discoloration, property loss.`,
      });
    } else if (Math.abs(input.melt_temp_C - proc.melt_temp_recommended_C) > 15) {
      warnings.push({
        level: 'info',
        parameter: 'melt_temp_C',
        message: `${input.melt_temp_C}°C is within range but differs from recommended (${proc.melt_temp_recommended_C}°C)`,
        suggestion: `Consider using recommended value of ${proc.melt_temp_recommended_C}°C for optimal results.`,
      });
    }
  }

  // Mold temperature
  if (input.mold_temp_C != null) {
    if (input.mold_temp_C < proc.mold_temp_min_C) {
      warnings.push({
        level: 'warning',
        parameter: 'mold_temp_C',
        message: `${input.mold_temp_C}°C is below minimum (${proc.mold_temp_min_C}°C) for ${mat.name}`,
        suggestion: `Increase mold temperature to at least ${proc.mold_temp_min_C}°C. Recommended: ${proc.mold_temp_recommended_C}°C. Low mold temp → poor surface, incomplete crystallization (semi-crystalline).`,
      });
    } else if (input.mold_temp_C > proc.mold_temp_max_C) {
      warnings.push({
        level: 'warning',
        parameter: 'mold_temp_C',
        message: `${input.mold_temp_C}°C exceeds maximum (${proc.mold_temp_max_C}°C) for ${mat.name}`,
        suggestion: `Reduce mold temperature to at most ${proc.mold_temp_max_C}°C. Recommended: ${proc.mold_temp_recommended_C}°C. High mold temp → long cycle time, potential sticking.`,
      });
    }
  }

  // Injection speed vs shear rate (simplified check)
  if (input.injection_speed_mm_s != null && input.wall_thickness_mm != null) {
    // Approximate shear rate at gate: γ ≈ 6Q/(w*h²) simplified as speed/thickness * factor
    const approxShearRate = (6 * input.injection_speed_mm_s) / (input.wall_thickness_mm);
    if (approxShearRate > proc.max_shear_rate_1_s * 0.5) {
      warnings.push({
        level: 'warning',
        parameter: 'injection_speed',
        message: `Estimated shear rate (${Math.round(approxShearRate)} 1/s) may be high for ${mat.name} at ${input.wall_thickness_mm}mm wall`,
        suggestion: `Maximum shear rate for ${mat.name}: ${proc.max_shear_rate_1_s} 1/s. Consider reducing injection speed or increasing wall thickness. Note: actual shear rate depends on gate geometry — run simulation for accurate values.`,
      });
    }
  }

  // Wall thickness general checks
  if (input.wall_thickness_mm != null) {
    if (input.wall_thickness_mm < 0.5) {
      warnings.push({
        level: 'error',
        parameter: 'wall_thickness',
        message: `${input.wall_thickness_mm}mm is extremely thin for injection molding`,
        suggestion: 'Minimum practical wall thickness is ~0.5mm for small parts with easy-flow materials. Consider micro-molding if needed.',
      });
    } else if (input.wall_thickness_mm > 6) {
      warnings.push({
        level: 'warning',
        parameter: 'wall_thickness',
        message: `${input.wall_thickness_mm}mm is very thick — expect long cycle time and sink marks`,
        suggestion: 'Core out thick sections to <4mm. Consider gas-assist or structural foam for thick parts. Expected cooling time increases with thickness².',
      });
    }

    // Cooling time estimate
    if (input.melt_temp_C != null && input.mold_temp_C != null) {
      const alpha = mat.thermal.thermal_conductivity_W_mK /
        (mat.thermal.density_kg_m3 * mat.thermal.specific_heat_J_kgK);
      const s = input.wall_thickness_mm / 1000; // convert to meters
      const Teject = mat.thermal.ejection_temp_C;
      const arg = (8 / (Math.PI * Math.PI)) *
        ((input.melt_temp_C - input.mold_temp_C) / (Teject - input.mold_temp_C));
      if (arg > 1) {
        const tCool = (s * s / (Math.PI * Math.PI * alpha)) * Math.log(arg);
        warnings.push({
          level: 'info',
          parameter: 'cooling_time',
          message: `Estimated minimum cooling time: ${tCool.toFixed(1)}s for ${input.wall_thickness_mm}mm wall`,
          suggestion: `Based on ${mat.name} thermal properties. Actual cooling time may be longer depending on cooling circuit efficiency.`,
        });
      }
    }
  }

  // Packing pressure check
  if (input.packing_pressure_MPa != null) {
    if (input.packing_pressure_MPa > 150) {
      warnings.push({
        level: 'warning',
        parameter: 'packing_pressure',
        message: `${input.packing_pressure_MPa} MPa packing pressure is very high`,
        suggestion: 'Typical packing pressure is 30-80% of injection pressure. Very high packing → overpacking near gate, high clamp force, residual stress.',
      });
    }
  }

  // Drying reminder
  if (proc.drying_temp_C != null) {
    warnings.push({
      level: 'info',
      parameter: 'drying',
      message: `${mat.name} is hygroscopic — drying required`,
      suggestion: `Dry at ${proc.drying_temp_C}°C for ${proc.drying_time_hr}h minimum. Moisture causes splay, bubbles, and property loss.`,
    });
  }

  // Format output
  const lines: string[] = [];
  lines.push(`# Parameter Validation for ${mat.name}\n`);

  if (warnings.length === 0) {
    lines.push('All parameters are within acceptable ranges.');
  } else {
    const errors = warnings.filter(w => w.level === 'error');
    const warns = warnings.filter(w => w.level === 'warning');
    const infos = warnings.filter(w => w.level === 'info');

    if (errors.length > 0) {
      lines.push('## ERRORS (out of range)\n');
      errors.forEach(w => {
        lines.push(`**${w.parameter}**: ${w.message}`);
        lines.push(`  → ${w.suggestion}\n`);
      });
    }
    if (warns.length > 0) {
      lines.push('## Warnings\n');
      warns.forEach(w => {
        lines.push(`**${w.parameter}**: ${w.message}`);
        lines.push(`  → ${w.suggestion}\n`);
      });
    }
    if (infos.length > 0) {
      lines.push('## Notes\n');
      infos.forEach(w => {
        lines.push(`**${w.parameter}**: ${w.message}`);
        lines.push(`  → ${w.suggestion}\n`);
      });
    }
  }

  // Add processing window summary
  lines.push(`\n## ${mat.name} Processing Window`);
  lines.push(`- Melt: ${proc.melt_temp_min_C}–${proc.melt_temp_max_C}°C (rec: ${proc.melt_temp_recommended_C}°C)`);
  lines.push(`- Mold: ${proc.mold_temp_min_C}–${proc.mold_temp_max_C}°C (rec: ${proc.mold_temp_recommended_C}°C)`);
  lines.push(`- Max shear rate: ${proc.max_shear_rate_1_s} 1/s`);
  if (proc.drying_temp_C) {
    lines.push(`- Drying: ${proc.drying_temp_C}°C / ${proc.drying_time_hr}h`);
  }
  lines.push(`- Max residence: ${proc.max_residence_time_min} min`);

  return lines.join('\n');
}
