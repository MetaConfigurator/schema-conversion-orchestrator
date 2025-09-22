import {Converter, SchemaLanguage, SchemaFeature} from "../dataStructures.js";
import xsd from "xsd-json-converter";
import * as fs from "fs";

export const converter: Converter = {
  name: "xsd-json-converter (xjc)",
  sourceFormat: SchemaLanguage.Xsd,
  targetFormat: SchemaLanguage.JsonSchema,
  supportedFeatures: [SchemaFeature.Properties, SchemaFeature.Attributes, SchemaFeature.Constraints],

  async convert(schema: string): Promise<string> {
      console.debug(`xsd-json-converter (xjc) processing schema: ${schema.substring(0, 100)}...`);

      // temporarily store the schema in a file
      const fileName = "temp_schema.xsd";
      fs.writeFileSync(fileName, schema);

      let result: string|undefined = undefined;
      let error: any = undefined;

      // Use the xsd-json-converter library to convert XSD to JSON Schema
      await xsd.convert(fileName).then((result => {
            console.debug("Conversion result:", result);
            result = JSON.stringify(result, null, 2);
      })).catch((err: any) => {
            console.error("Conversion error:", err);
            error = err;
      }).finally(() => {
            // Clean up the temporary file
            fs.unlinkSync(fileName);
      });

      if (error) {
          throw new Error(`Conversion failed: ${error}`);
      } else if (!result) {
          throw new Error("Conversion failed: No result returned");
      } else {
          return result;
      }

  }
};

// Also export as default for compatibility
export default converter;