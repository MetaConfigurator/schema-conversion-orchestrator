import {Converter, SchemaLanguage} from "../dataStructures.js";
import { spawn } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { createRequire } from "module";
import { fileURLToPath } from "url";

// Create require function for CommonJS modules
const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface XjcNode {
  name: string;
  dataType: string | null;
  minOccurs: string | null;
  maxOccurs: string | null;
  minLength: string | null;
  maxLength: string | null;
  pattern: string | null;
  fractionDigits: string | null;
  totalDigits: string | null;
  minInclusive: string | null;
  maxInclusive: string | null;
  minExclusive: string | null;
  maxExclusive: string | null;
  values: string[] | null;
  elements: XjcNode[];
}

interface XjcResult {
  namespace: string | null;
  schemaElement: XjcNode;
}

function getBundledExecutable(): string {
  const packageJson = require.resolve("xsd-json-converter/package.json");
  const packageDir = path.dirname(packageJson);
  const platformDir = process.platform === "darwin"
    ? "osx-x64"
    : process.platform === "linux"
      ? "linux-x64"
      : process.platform === "win32"
        ? "win-x64"
        : "";
  if (!platformDir) {
    throw new Error(`Unsupported platform for xsd-json-converter: ${process.platform}`);
  }
  const executableName = process.platform === "win32" ? "XSDConverter.exe" : "XSDConverter";
  return path.join(packageDir, "dist", "tools", platformDir, executableName);
}

function runBundledConverter(executablePath: string, inputPath: string): Promise<string> {
  return new Promise((resolve, reject) => {
    if (process.platform !== "win32") {
      fs.chmodSync(executablePath, 0o755);
    }

    const child = spawn(executablePath, [inputPath]);
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", data => {
      stdout += data.toString();
    });
    child.stderr.on("data", data => {
      stderr += data.toString();
    });
    child.on("error", reject);
    child.on("close", code => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(stderr.trim() || `xsd-json-converter exited with code ${code}`));
      }
    });
  });
}

function parseOccurs(value: string | null): number | null {
  if (!value || value === "unbounded") {
    return null;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function jsonSchemaType(dataType: string | null): Record<string, unknown> {
  const type = (dataType ?? "string").toLowerCase().replace(/^xs:/, "");
  switch (type) {
    case "boolean":
      return { type: "boolean" };
    case "byte":
    case "int":
    case "integer":
    case "long":
    case "negativeinteger":
    case "nonnegativeinteger":
    case "nonpositiveinteger":
    case "positiveinteger":
    case "short":
    case "unsignedbyte":
    case "unsignedint":
    case "unsignedlong":
    case "unsignedshort":
      return { type: "integer" };
    case "decimal":
    case "double":
    case "float":
      return { type: "number" };
    case "date":
      return { type: "string", format: "date" };
    case "datetime":
      return { type: "string", format: "date-time" };
    case "time":
      return { type: "string", format: "time" };
    default:
      return { type: "string" };
  }
}

function withRestrictions(schema: Record<string, unknown>, node: XjcNode): Record<string, unknown> {
  if (node.values?.length) {
    schema.enum = node.values;
  }
  if (node.minLength) {
    schema.minLength = Number.parseInt(node.minLength, 10);
  }
  if (node.maxLength) {
    schema.maxLength = Number.parseInt(node.maxLength, 10);
  }
  if (node.pattern) {
    schema.pattern = node.pattern;
  }
  if (node.minInclusive) {
    schema.minimum = Number.parseFloat(node.minInclusive);
  }
  if (node.maxInclusive) {
    schema.maximum = Number.parseFloat(node.maxInclusive);
  }
  if (node.minExclusive) {
    schema.exclusiveMinimum = Number.parseFloat(node.minExclusive);
  }
  if (node.maxExclusive) {
    schema.exclusiveMaximum = Number.parseFloat(node.maxExclusive);
  }
  return schema;
}

function nodeToJsonSchema(node: XjcNode): Record<string, unknown> {
  if (node.elements?.length) {
    const properties: Record<string, unknown> = {};
    const required: string[] = [];

    for (const child of node.elements) {
      let childSchema = nodeToJsonSchema(child);
      const maxOccurs = child.maxOccurs;
      if (maxOccurs === "unbounded" || (parseOccurs(maxOccurs) ?? 1) > 1) {
        const arraySchema: Record<string, unknown> = {
          type: "array",
          items: childSchema,
        };
        const minItems = parseOccurs(child.minOccurs);
        const maxItems = parseOccurs(maxOccurs);
        if (minItems !== null) {
          arraySchema.minItems = minItems;
        }
        if (maxItems !== null) {
          arraySchema.maxItems = maxItems;
        }
        childSchema = arraySchema;
      }
      properties[child.name] = childSchema;
      if (child.minOccurs !== "0") {
        required.push(child.name);
      }
    }

    const schema: Record<string, unknown> = {
      type: "object",
      properties,
      additionalProperties: false,
    };
    if (required.length) {
      schema.required = required;
    }
    return schema;
  }

  return withRestrictions(jsonSchemaType(node.dataType), node);
}

function xjcTreeToJsonSchema(xjcResult: XjcResult): Record<string, unknown> {
  const root = xjcResult.schemaElement;
  return {
    $schema: "http://json-schema.org/draft-07/schema#",
    title: root.name,
    ...(xjcResult.namespace ? { description: `XSD namespace: ${xjcResult.namespace}` } : {}),
    ...nodeToJsonSchema(root),
  };
}

export const converter: Converter = {
  name: "xsd-json-converter (xjc)",
  sourceLanguage: SchemaLanguage.Xsd,
  targetLanguage: SchemaLanguage.JsonSchema,
  library: "xsd-json-converter",
  libraryUrl: "https://www.npmjs.com/package/xsd-json-converter",

  async convert(schema: string): Promise<string> {
      console.error(`xsd-json-converter (xjc) processing schema: ${schema.substring(0, 100)}...`);

      // temporarily store the schema in a file
      const fileName = path.join(os.tmpdir(), `xjc_schema_${process.pid}_${Date.now()}.xsd`);
      fs.writeFileSync(fileName, schema);

      let result: string | undefined = undefined;
      let error: any = undefined;

      try {
          const executable = getBundledExecutable();
          const rawOutput = await runBundledConverter(executable, fileName);
          const nativeTree = JSON.parse(rawOutput) as XjcResult;
          result = JSON.stringify(xjcTreeToJsonSchema(nativeTree), null, 2);
      } catch (conversionError) {
          console.error("xsd-json-converter failed:", conversionError);
          error = conversionError;
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
