import { searchTroubleshooting, formatTroubleshooting } from '../knowledge/troubleshooting.js';
import { searchGuidelines, formatDFMRule, formatMeshGuideline, formatProcessBound } from '../knowledge/guidelines.js';
import { findMaterial } from '../knowledge/materials.js';
import { searchKnowledge as qdrantSearch } from '../qdrant.js';

export async function queryKnowledge(question: string, context?: string): Promise<string> {
  const query = context ? `${question} ${context}` : question;
  const sections: string[] = [];

  // ── Qdrant semantic search (primary) ──
  const vectorResults = await qdrantSearch(query, 5);
  if (vectorResults.length > 0) {
    sections.push('# Knowledge Base Results\n');
    for (const r of vectorResults) {
      if (r.score < 0.25) continue; // skip low-relevance
      sections.push(r.text);
      sections.push('');
    }
  }

  // ── Local keyword search (supplement) ──
  const troubleEntries = searchTroubleshooting(query);
  if (troubleEntries.length > 0) {
    sections.push('# Additional Troubleshooting\n');
    troubleEntries.slice(0, 2).forEach(entry => {
      sections.push(formatTroubleshooting(entry));
      sections.push('');
    });
  }

  const { dfm, mesh, process } = searchGuidelines(query);
  if (dfm.length > 0) {
    sections.push('# DFM Guidelines\n');
    dfm.slice(0, 2).forEach(rule => {
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
    process.slice(0, 2).forEach(bound => {
      sections.push(formatProcessBound(bound));
      sections.push('');
    });
  }

  // Material mentions
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
