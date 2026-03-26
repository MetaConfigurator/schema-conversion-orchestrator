import {Converter, SchemaLanguage} from "../dataStructures.js";
import {nodeShapeToJSONSchema} from '@comake/shacl-to-json-schema';
import jsonld from "jsonld";

export const SHACL_CONTEXT: any = {
  "@context": {
    sh: "http://www.w3.org/ns/shacl#",
    rdf: "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    rdfs: "http://www.w3.org/2000/01/rdf-schema#",
    xsd: "http://www.w3.org/2001/XMLSchema#",
    NodeShape: "sh:NodeShape",
    property: { "@id": "sh:property", "@container": "@set" },
    path: "sh:path",
    datatype: "sh:datatype",
    node: "sh:node",
    nodeKind: "sh:nodeKind",
    minCount: "sh:minCount",
    maxCount: "sh:maxCount",
    name: "sh:name",
    description: "sh:description",
    targetClass: { "@id": "sh:targetClass", "@type": "@id", "@container": "@set" },
    closed: "sh:closed",
    in: "sh:in"
  }
};

const SUPPORTED_SHACL_KEYS = {
  property: "http://www.w3.org/ns/shacl#property",
  datatype: "http://www.w3.org/ns/shacl#datatype",
  node: "http://www.w3.org/ns/shacl#node",
  nodeKind: "http://www.w3.org/ns/shacl#nodeKind",
  path: "http://www.w3.org/ns/shacl#path"
};

function isNodeShape(type: any): boolean {
  if (!type) return false;
  const types = Array.isArray(type) ? type : [type];
  return types.some(t =>
    t === "http://www.w3.org/ns/shacl#NodeShape" ||
    t === "sh:NodeShape" ||
    t === "NodeShape"
  );
}

function extractNodeShapes(doc: any): any[] {
  const graph = doc["@graph"] ?? [doc];
  return graph.filter((n: any) => isNodeShape(n["@type"]));
}

function localName(iri: string): string {
  return iri.split(/[\/#]/).pop() || "NodeShape";
}

function getShapeBaseName(shape: any, index: number): string {
  const name = shape.name?.[0]?.['@value'] ||
               shape.targetClass?.[0]?.['@id'] ||
               shape["@id"];
  return localName(name || `NodeShape_${index}`);
}

function uniqueDefName(base: string, defs: Record<string, any>): string {
  if (!defs[base]) return base;
  let i = 2;
  while (defs[`${base}_${i}`]) i++;
  return `${base}_${i}`;
}

function normalizeJsonLd(doc: any): { "@graph": any[] } {
  if (Array.isArray(doc)) return { "@graph": doc };
  if (doc["@graph"]) return doc;
  return { "@graph": [doc] };
}

// Resolve @id references recursively
function resolveRef(id: string, graph: any[]): any | null {
  return graph.find((n: any) => n['@id'] === id) || null;
}

function flattenShapeRecursively(shape: any, graph: any[]): any {
  const flattened = { ...shape };

  Object.keys(flattened).forEach(key => {
    const value = flattened[key];
    if (Array.isArray(value)) {
      flattened[key] = value.map((item: any) => {
        // Resolve @id refs
        if (item?.['@id']) {
          const resolved = resolveRef(item['@id'], graph);
          return resolved ? flattenShapeRecursively(resolved, graph) : item;
        }
        // Handle RDF lists
        if (item?.['@list']) {
          item['@list'] = item['@list'].map((listItem: any) =>
            listItem?.['@id']
              ? flattenShapeRecursively(resolveRef(listItem['@id'], graph)!, graph)
              : listItem
          );
        }
        return item;
      });
    }
  });

  return flattened;
}

// Filter to @comake-supported property shapes ONLY
function filterSupportedProperties(shape: any): any {
  const processed = { ...shape };
  const propKey = SUPPORTED_SHACL_KEYS.property;

  if (processed[propKey]?.length) {
    const originalCount = processed[propKey].length;
    const supportedProps = processed[propKey].filter((prop: any) => {
      const hasDatatype = prop[SUPPORTED_SHACL_KEYS.datatype]?.length;
      const hasNode = prop[SUPPORTED_SHACL_KEYS.node]?.length;
      const hasNodeKind = prop[SUPPORTED_SHACL_KEYS.nodeKind]?.length;

      return hasDatatype || hasNode || hasNodeKind;
    });

    processed[propKey] = supportedProps;
    console.log(`Filtered ${shape['@id'] || 'shape'}: ${supportedProps.length}/${originalCount} properties kept`);
  }

  return processed;
}

export const converter: Converter = {
  name: "@comake/shacl-to-json-schema",
  sourceLanguage: SchemaLanguage.SHACL_JSON_LD,
  targetLanguage: SchemaLanguage.JsonSchema,

  async convert(schema: string): Promise<string> {
    try {
      const shaclJsonLd = JSON.parse(schema);
      const graph = Array.isArray(shaclJsonLd) ? shaclJsonLd : shaclJsonLd['@graph'] || [shaclJsonLd];

      // COMPACT to get proper prefixed keys that @comake expects
      const compacted = normalizeJsonLd(await jsonld.compact({ "@graph": graph }, SHACL_CONTEXT));

      const shapes = extractNodeShapes(compacted);
      if (shapes.length === 0) {
        throw new Error("No sh:NodeShape found in SHACL document");
      }

      // Flatten refs + filter unsupported properties
      const processedShapes = shapes.map(shape =>
        filterSupportedProperties(flattenShapeRecursively(shape, compacted['@graph']))
      );

      const rootSchema: any = {
        $schema: "https://json-schema.org/draft/2020-12/schema",
        $defs: {},
        type: "object"
      };

      processedShapes.forEach((shape, index) => {
        const baseName = getShapeBaseName(shape, index);
        const defName = uniqueDefName(baseName.replace(/Shape$/, ""), rootSchema.$defs);

        try {
          // Use @comake options for richer output
          rootSchema.$defs[defName] = nodeShapeToJSONSchema(shape, {
            useNames: true,        // Use sh:name instead of full path IRIs
            addTitles: true,       // Add sh:name as title
            addDescriptions: true  // Add sh:description
          });
        } catch (e: any) {
          console.error(`Failed NodeShape ${baseName}:`, e.message);
          // Continue with other shapes instead of failing completely
        }
      });

      return JSON.stringify(rootSchema, null, 2);
    } catch (error: any) {
      throw new Error(`SHACL JSON-LD to JSON Schema conversion failed: ${error.message}`);
    }
  }
};

export default converter;
