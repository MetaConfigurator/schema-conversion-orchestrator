import {Converter, SchemaLanguage} from "../dataStructures.js";
import { ShaclReader } from 'shacl-bridge';


export const converter: Converter = {
  name: "shacl-bridge",
  sourceLanguage: SchemaLanguage.SHACL_JSON_LD,
  targetLanguage: SchemaLanguage.JsonSchema,
  library: "shacl-bridge",
  libraryUrl: "https://www.npmjs.com/package/shacl-bridge",

  async convert(jsonLdString: string): Promise<string> {
    try {
      const jsonSchema = await new ShaclReader().fromJsonLdContent(jsonLdString).convert();
      return JSON.stringify(jsonSchema, null, 2);
    } catch (error: any) {
      throw new Error(`SHACL Ttl to JSON Schema conversion failed: ${error.message}`);
    }
  }
};

export default converter;
