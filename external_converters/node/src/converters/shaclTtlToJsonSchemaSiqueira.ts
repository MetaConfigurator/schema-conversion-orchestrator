import {Converter, SchemaLanguage} from "../dataStructures.js";
import {getUniqueSchemaFromTtl} from 'shacl-jsonschema-converter';

/**
 * Inject sh:targetClass, sh:closed true and sh:ignoredProperties ( rdf:type )
 * into every NodeShape that lacks them, since this converter requires them to
 * process a shape (shapes missing them are otherwise silently dropped).
 */
function preprocessTurtle(turtle: string): string {
  let result = turtle;
  if (!/^@prefix\s+rdf:\s/m.test(result)) {
    result = `@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n${result}`;
  }
  if (!/^@prefix\s+ex:\s/m.test(result)) {
    result = `@prefix ex: <http://example.org/> .\n${result}`;
  }

  result = result.replace(
    /(a\s+sh:NodeShape\s*;)([\s\S]*?)(\s*sh:\w+\s)/g,
    (_match, head: string, middle: string, nextKeyword: string) => {
      let injected = '';
      if (!middle.includes('sh:targetClass')) {
        injected += '\n    sh:targetClass ex:DummyClass ;';
      }
      if (!middle.includes('sh:closed')) {
        injected += '\n    sh:closed true ;';
      }
      if (!middle.includes('sh:ignoredProperties')) {
        injected += '\n    sh:ignoredProperties ( rdf:type ) ;';
      }
      return `${head}${middle}${injected}${nextKeyword}`;
    }
  );

  return result;
}

export const converter: Converter = {
  name: "shacl-jsonschema-converter",
  sourceLanguage: SchemaLanguage.SHACL_TTL,
  targetLanguage: SchemaLanguage.JsonSchema,
  library: "shacl-jsonschema-converter",
  libraryUrl: "https://www.npmjs.com/package/shacl-jsonschema-converter",

  async convert(schema: string): Promise<string> {
    try {
      const processed = preprocessTurtle(schema);
      const jsonSchema = getUniqueSchemaFromTtl(processed);
      return JSON.stringify(jsonSchema, null, 2);
    } catch (error: any) {
      throw new Error(`SHACL Ttl to JSON Schema conversion failed: ${error.message}`);
    }
  }
};

export default converter;
