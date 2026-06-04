import {Converter, SchemaLanguage} from "../dataStructures.js";
import {nodeShapeToJSONSchema} from '@comake/shacl-to-json-schema';
import jsonld from "jsonld";

const SHACL_NS = 'http://www.w3.org/ns/shacl#';

/**
 * Frame the (expanded) SHACL JSON-LD around sh:NodeShape so every property
 * shape (a blank node in the expanded graph) is nested inline under its node
 * shape, producing the tree structure `nodeShapeToJSONSchema` expects.
 */
async function frameNodeShapes(doc: unknown): Promise<any[]> {
  const framed = (await jsonld.frame(doc as any, {
    '@type': `${SHACL_NS}NodeShape`,
  })) as Record<string, unknown>;

  const graph = framed['@graph'];
  if (Array.isArray(graph)) return graph as any[];
  if (framed['@type']) return [framed as any];
  return [];
}

function localName(id: string): string {
  if (id.includes('#')) return id.split('#').pop()!;
  if (id.includes('/')) return id.split('/').pop()!;
  return id;
}

// `useNames` keys properties by sh:name; when a property shape has none, give it
// one derived from the local name of its sh:path so the output uses readable
// keys (e.g. "tags") instead of "undefined".
function ensurePropertyNames(shape: any): void {
  const propKey = `${SHACL_NS}property`;
  const nameKey = `${SHACL_NS}name`;
  const pathKey = `${SHACL_NS}path`;

  let props = shape?.[propKey];
  if (!props) return;
  if (!Array.isArray(props)) props = [props];

  for (const prop of props) {
    if (!prop || typeof prop !== 'object') continue;
    if (prop[nameKey]) continue;
    const path = prop[pathKey];
    const pathId = Array.isArray(path) ? path[0]?.['@id'] : path?.['@id'];
    if (pathId) prop[nameKey] = [{ '@value': localName(pathId) }];
  }
}

// Use sh:name for property keys/titles instead of full path IRIs, and surface
// sh:name / sh:description as title / description.
const COMAKE_OPTIONS = {
  useNames: true,
  addTitles: true,
  addDescriptions: true,
} as const;

export const converter: Converter = {
  name: "@comake/shacl-to-json-schema",
  sourceLanguage: SchemaLanguage.SHACL_JSON_LD,
  targetLanguage: SchemaLanguage.JsonSchema,
  library: "@comake/shacl-to-json-schema",
  libraryUrl: "https://www.npmjs.com/package/@comake/shacl-to-json-schema",

  async convert(schema: string): Promise<string> {
    try {
      const shaclJsonLd = JSON.parse(schema);
      const nodeShapes = await frameNodeShapes(shaclJsonLd);

      if (nodeShapes.length === 0) {
        throw new Error("No sh:NodeShape found in SHACL document");
      }

      for (const shape of nodeShapes) ensurePropertyNames(shape);

      if (nodeShapes.length === 1) {
        const jsonSchema = nodeShapeToJSONSchema(nodeShapes[0] as any, COMAKE_OPTIONS);
        return JSON.stringify(jsonSchema, null, 2);
      }

      // Multiple node shapes: emit each under $defs, keyed by its local name,
      // and surface the first shape's schema at the top level.
      const defs: Record<string, unknown> = {};
      for (const shape of nodeShapes) {
        const id = (shape['@id'] as string) ?? 'NodeShape';
        defs[localName(id)] = nodeShapeToJSONSchema(shape as any, COMAKE_OPTIONS);
      }
      const first = Object.keys(defs)[0];
      const combined = { ...(defs[first] as object), $defs: defs };
      return JSON.stringify(combined, null, 2);
    } catch (error: any) {
      throw new Error(`SHACL JSON-LD to JSON Schema conversion failed: ${error.message}`);
    }
  }
};

export default converter;
