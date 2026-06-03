import {Converter, SchemaLanguage} from "../dataStructures.js";
import { createRequire } from "module";

// Create require function for CommonJS modules
const require = createRequire(import.meta.url);

export const converter: Converter = {
  name: "xsd2jsonschema",
  sourceLanguage: SchemaLanguage.Xsd,
  targetLanguage: SchemaLanguage.JsonSchema,

  async convert(schema: string): Promise<string> {

          // Use createRequire to import the CommonJS module
          const Xsd2JsonSchema = require('xsd2jsonschema').Xsd2JsonSchema;
          const xs2js = new Xsd2JsonSchema();

          const convertedSchemas = xs2js.processAllSchemas({schemas: {'temp_schema.xsd': schema}
          });
          const jsonSchema = convertedSchemas['temp_schema.xsd'].getJsonSchema();
          return JSON.stringify(jsonSchema, null, 2);

  }
};

// Also export as default for compatibility
export default converter;