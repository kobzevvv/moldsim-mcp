/**
 * Qdrant vector search client for MoldSim MCP.
 * Uses @huggingface/transformers for local embedding (all-MiniLM-L6-v2)
 * and @qdrant/js-client-rest for vector search.
 */

import { QdrantClient } from '@qdrant/js-client-rest';

const QDRANT_URL = 'https://d072a605-3a1a-471a-aaf3-a6bdd11f07d2.us-west-2-0.aws.cloud.qdrant.io';
const QDRANT_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9tpiCCNFb9wWBzxVJkT21qcWDYqZ0PV1fu9siVlo3kY';
const COLLECTION = 'moldsim_knowledge';

let qdrantClient: QdrantClient | null = null;
let pipelinePromise: Promise<any> | null = null;

function getQdrantClient(): QdrantClient {
  if (!qdrantClient) {
    qdrantClient = new QdrantClient({
      url: QDRANT_URL,
      apiKey: QDRANT_API_KEY,
    });
  }
  return qdrantClient;
}

async function getEmbeddingPipeline() {
  if (!pipelinePromise) {
    pipelinePromise = (async () => {
      // Dynamic import to avoid top-level ESM issues
      const { pipeline } = await import('@huggingface/transformers');
      return pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
        dtype: 'fp32',
      });
    })();
  }
  return pipelinePromise;
}

async function embedText(text: string): Promise<number[]> {
  const pipe = await getEmbeddingPipeline();
  const output = await pipe(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data as Float32Array);
}

export interface SearchResult {
  text: string;
  category: string;
  subcategory?: string;
  score: number;
}

export async function searchKnowledge(
  query: string,
  limit: number = 5,
  categoryFilter?: string,
): Promise<SearchResult[]> {
  try {
    const client = getQdrantClient();
    const vector = await embedText(query);

    const filter = categoryFilter
      ? { must: [{ key: 'category', match: { value: categoryFilter } }] }
      : undefined;

    const results = await client.query(COLLECTION, {
      query: vector,
      limit,
      filter,
      with_payload: true,
    });

    return results.points.map((r: any) => ({
      text: r.payload?.text ?? '',
      category: r.payload?.category ?? '',
      subcategory: r.payload?.subcategory,
      score: r.score ?? 0,
    }));
  } catch (error) {
    console.error('Qdrant search failed, falling back to local:', error);
    return [];
  }
}

/** Pre-warm the embedding model in background. */
export function warmupEmbedding(): void {
  getEmbeddingPipeline().catch(() => {});
}
