import { findMaterial, listMaterials, formatMaterialProperties } from '../knowledge/materials.js';

export function getMaterialProperties(
  material: string,
  properties?: string[]
): string {
  const matches = findMaterial(material);

  if (matches.length === 0) {
    const available = listMaterials();
    return [
      `No material found matching "${material}".`,
      '',
      'Available materials:',
      ...available.map(m => `- ${m.id}: ${m.name} (${m.family})`),
      '',
      'Try searching by family (e.g., "PA", "PP", "PC") or specific grade (e.g., "PA66-GF30").',
    ].join('\n');
  }

  if (matches.length === 1) {
    return formatMaterialProperties(matches[0], properties);
  }

  // Multiple matches — list them, then show first one in detail
  const lines = [
    `Found ${matches.length} materials matching "${material}":\n`,
    ...matches.map(m => `- **${m.id}**: ${m.name} (${m.family})`),
    '\n---\n',
    formatMaterialProperties(matches[0], properties),
  ];

  if (matches.length > 1) {
    lines.push(`\n> ${matches.length - 1} more match(es). Query a specific ID for details.`);
  }

  return lines.join('\n');
}
