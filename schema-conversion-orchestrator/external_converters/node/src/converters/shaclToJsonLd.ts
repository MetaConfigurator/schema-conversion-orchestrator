import {Converter, SchemaLanguage} from "../dataStructures.js";

import {Parser, Store, Writer} from "n3";
import * as jsonld from "jsonld";


import { nodeShapeToJSONSchema } from '@comake/shacl-to-json-schema';


export const converter: Converter = {
  name: "n3 and rdf-ext",
  sourceLanguage: SchemaLanguage.SHACL,
  targetLanguage: SchemaLanguage.JsonSchema,

  async convert(schema: string): Promise<string> {

    const result = await turtleToJsonLD(schema);
    if (!result.success) {
      throw new Error(`Conversion failed: ${result.error}`);
    }

    const jsonldSchema = JSON.parse(result.data!);
    const jsonSchema = nodeShapeToJSONSchema(jsonldSchema);

    return JSON.stringify(jsonSchema, null, 2);
  }
};




// Interface for the conversion result
interface ConversionResult {
  success: boolean;
  data?: string;
  error?: string;
}

/**
 * Converts RDF Turtle string to JSON-LD string
 * @param turtleString - The Turtle RDF string to parse
 * @param context - Optional JSON-LD context object
 * @returns Promise containing the JSON-LD string or error
 */
async function turtleToJsonLD(
  turtleString: string,
  context?: any
): Promise<ConversionResult> {
  try {
    // Step 1: Parse Turtle into N3 Store
    const parser = new Parser({ format: 'text/turtle' });
    const store = new Store();

    // Parse the turtle string
    const quads = parser.parse(turtleString);
    store.addQuads(quads);

    // Step 2: Convert N3 Store to N-Quads (intermediate format)
    const writer = new Writer({ format: 'application/n-quads' });
    const nquads = writer.quadsToString(store.getQuads(null, null, null, null));

    // Step 3: Convert N-Quads to JSON-LD
    const doc = await jsonld.fromRDF(nquads, { format: 'application/n-quads' });

    // Step 4: Apply context if provided and compact
    let result;
    if (context) {
      result = await jsonld.compact(doc, context);
    } else {
      result = doc;
    }

    return {
      success: true,
      data: JSON.stringify(result, null, 2)
    };

  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}



// Also export as default for compatibility
export default converter;