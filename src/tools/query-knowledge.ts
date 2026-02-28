import { searchTroubleshooting, formatTroubleshooting } from '../knowledge/troubleshooting.js';
import { searchGuidelines, formatDFMRule, formatMeshGuideline, formatProcessBound } from '../knowledge/guidelines.js';
import { findMaterial, formatMaterialProperties } from '../knowledge/materials.js';

export function queryKnowledge(question: string, context?: string): string {
  const query = context ? `${question} ${context}` : question;
  const sections: string[] = [];

  // Search troubleshooting
  const troubleEntries = searchTroubleshooting(query);
  if (troubleEntries.length > 0) {
    sections.push('# Troubleshooting Results\n');
    troubleEntries.slice(0, 3).forEach(entry => {
      sections.push(formatTroubleshooting(entry));
      sections.push('');
    });
  }

  // Search guidelines
  const { dfm, mesh, process } = searchGuidelines(query);
  if (dfm.length > 0) {
    sections.push('# DFM Guidelines\n');
    dfm.slice(0, 3).forEach(rule => {
      sections.push(formatDFMRule(rule));
      sections.push('');
    });
  }
  if (mesh.length > 0) {
    sections.push('# Mesh Recommendations\n');
    mesh.slice(0, 2).forEach(guide => {
      sections.push(formatMeshGuideline(guide));
      sections.push('');
    });
  }
  if (process.length > 0) {
    sections.push('# Process Parameter Bounds\n');
    process.slice(0, 3).forEach(bound => {
      sections.push(formatProcessBound(bound));
      sections.push('');
    });
  }

  // Check if any materials are mentioned
  const materialMatches = findMaterial(query);
  if (materialMatches.length > 0 && materialMatches.length <= 3) {
    sections.push('# Related Materials\n');
    materialMatches.slice(0, 2).forEach(mat => {
      sections.push(`- **${mat.name}** (${mat.family}, ${mat.type}): ${mat.notes}`);
    });
    sections.push('');
  }

  if (sections.length === 0) {
    return [
      'No specific matches found for your query. Try:',
      '- Specific defect names: "sink marks", "warpage", "short shot", "weld lines"',
      '- Material names: "PA66-GF30", "PC", "ABS", "PP"',
      '- Process topics: "gate location", "cooling", "packing", "cycle time"',
      '- Design rules: "rib thickness", "draft angle", "wall thickness", "tolerances"',
      '- Simulation topics: "mesh", "3D vs dual domain", "convergence"',
    ].join('\n');
  }

  return sections.join('\n');
}
