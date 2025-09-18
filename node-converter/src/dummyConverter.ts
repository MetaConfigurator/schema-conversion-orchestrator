// dummyConverter.ts
import { Converter, SchemaLanguage, SchemaFeature } from "./dataStructures";

export const dummyConverter: Converter = {
  name: "DummyNodeConverter",
  serviceAddress: "http://localhost:3001/convert", // Node service endpoint
  sourceFormat: SchemaLanguage.SHACL,
  targetFormat: SchemaLanguage.JsonSchema,
  supportedFeatures: [SchemaFeature.Properties, SchemaFeature.Attributes],

  async convert(schema: string): Promise<string> {
    console.log("DummyNodeConverter received schema:", schema);
    // Dummy implementation
    return `{
      "type": "object",
      "properties": {
        "dummyField": {
          "type": "string",
          "description": "This is a dummy field added by DummyNodeConverter"
        }
      }
    }`;
  },
};
