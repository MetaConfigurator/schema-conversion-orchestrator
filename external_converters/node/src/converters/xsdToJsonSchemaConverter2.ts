import {Converter, SchemaLanguage} from "../dataStructures.js";
import * as fs from "fs";
import { createRequire } from "module";

// Create require function for CommonJS modules
const require = createRequire(import.meta.url);

export const converter: Converter = {
  name: "xsd-json-converter (xjc)",
  sourceLanguage: SchemaLanguage.Xsd,
  targetLanguage: SchemaLanguage.JsonSchema,
  library: "xsd-json-converter",
  libraryUrl: "https://www.npmjs.com/package/xsd-json-converter",

  async convert(schema: string): Promise<string> {
      console.debug(`xsd-json-converter (xjc) processing schema: ${schema.substring(0, 100)}...`);

      // temporarily store the schema in a file
      const fileName = "temp_schema.xsd";
      fs.writeFileSync(fileName, schema);

      let result: string | undefined = undefined;
      let error: any = undefined;

      try {

            // Use createRequire to import the CommonJS module
            const xsd = require('xsd-json-converter');

          // Use the xsd-json-converter library to convert XSD to JSON Schema
          await xsd.convert(fileName).then((conversionResult: any) => {
              result = JSON.stringify(conversionResult, null, 2);
          }).catch((err: any) => {
              console.error("Conversion error:", err);
              error = err;
          });

      } catch (requireError) {
          console.error("Failed to require xsd-json-converter:", requireError);
          error = requireError;
      } finally {
          // Clean up the temporary file
          if (fs.existsSync(fileName)) {
              fs.unlinkSync(fileName);
          }
      }

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