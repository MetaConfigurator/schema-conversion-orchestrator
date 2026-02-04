import {Converter, SchemaLanguage} from "../dataStructures.js";

import { nodeShapeToJSONSchema } from '@comake/shacl-to-json-schema';


export const converter: Converter = {
  name: "@comake/shacl-to-json-schema",
  sourceLanguage: SchemaLanguage.SHACL_JSON_LD,
  targetLanguage: SchemaLanguage.JsonSchema,

  async convert(schema: string): Promise<string> {
    const jsonldSchema = JSON.parse(schema);
    const jsonSchema = nodeShapeToJSONSchema(jsonldSchema);
    return JSON.stringify(jsonSchema, null, 2);
  }
};


// Also export as default for compatibility
export default converter;