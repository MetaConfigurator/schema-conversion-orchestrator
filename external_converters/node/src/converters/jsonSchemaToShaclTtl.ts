import {Converter, SchemaLanguage} from "../dataStructures.js";
import { ShaclWriter, DEFAULT_PREFIXES } from 'shacl-bridge';


export const converter: Converter = {
  name: "shacl-bridge",
  sourceLanguage: SchemaLanguage.JsonSchema,
  targetLanguage: SchemaLanguage.SHACL_TTL,
  library: "shacl-bridge",
  libraryUrl: "https://www.npmjs.com/package/shacl-bridge",

  async convert(jsonSchemaString: string): Promise<string> {
    try {
    const jsonSchema = JSON.parse(jsonSchemaString);
      const turtle = await new ShaclWriter(jsonSchema)
  .getStoreBuilder()
  .withPrefixes({ ...DEFAULT_PREFIXES, ex: 'http://example.org/' })
  .write();
      return turtle;
    } catch (error: any) {
      throw new Error(`SHACL Ttl to JSON Schema conversion failed: ${error.message}`);
    }
  }
};

export default converter;
