#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import { Converter} from './dataStructures.js';
import {fileURLToPath, pathToFileURL} from "url";

const DEBUG_MODE = false;

interface ConversionRequest {
  sourceFormat: string;
  targetFormat: string;
  converterName: string;
  schema: string;
}

interface ConversionResponse {
  schema: string;
  error?: string;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const convertersDir = path.join(__dirname, 'converters');

class ConverterRegistry {
  private converters: Map<string, Converter> = new Map();
  isLoaded: boolean = false;

  constructor() {
    this.loadConverters();
  }

  private async loadConverters() {

    if (!fs.existsSync(convertersDir)) {
      console.error(`Converters directory not found: ${convertersDir}`);
      return;
    }

    const files = fs.readdirSync(convertersDir);

    for (const file of files) {
      if (file.endsWith('.js') || file.endsWith('.ts') ) {
        try {
          const converterPath = path.join(convertersDir, file);

          const modulePath = pathToFileURL(converterPath).href;
          if (DEBUG_MODE)
            console.log("attempting to import module at path: " + modulePath);
          const converterModule = await import(modulePath);

          // Support both default export and named exports
          const converter: Converter = converterModule.default || converterModule.converter || converterModule;

          if (this.isValidConverter(converter)) {
            const key = converterKey(converter.sourceFormat, converter.targetFormat, converter.name);
            this.converters.set(key, converter);
            if (DEBUG_MODE)
              console.error(`Loaded converter: ${converter.name} (${key})`);
          } else {
            console.error(`Invalid converter in file ${file}:`, converter);
          }
        } catch (error) {
          console.error(`Failed to load converter from ${file}:`, error);
        }
      }
    }

    if (DEBUG_MODE)
      console.error(`Total converters loaded: ${this.converters.size}`);
    this.isLoaded = true;
  }

  private isValidConverter(obj: any): obj is Converter {
    return obj && 
           typeof obj.name === 'string' &&
           typeof obj.sourceFormat === 'string' &&
           typeof obj.targetFormat === 'string' &&
           typeof obj.convert === 'function' &&
           Array.isArray(obj.supportedFeatures);
  }

  findConverter(sourceFormat: string, targetFormat: string, name: string): Converter | null {
    const key = converterKey(sourceFormat, targetFormat, name);
    return this.converters.get(key) || null;
  }

  getAllConverters(): Converter[] {
    return Array.from(this.converters.values());
  }
}

function converterKey(sourceFormat: string, targetFormat: string, name: string): string {
    return `${name} (${sourceFormat}->${targetFormat})`;
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.error('Usage: node converter.js <command> [args]');
    console.error('Commands:');
    console.error('  convert <input_file>     - Convert schema from input file');
    console.error('  list                     - List all available converters');
    process.exit(1);
  }

  const command = args[0];
  const registry = new ConverterRegistry();

    // Wait until converters are loaded
    while (!registry.isLoaded) {
        await new Promise(resolve => setTimeout(resolve, 20));
    }

  if (command === 'list') {
    const converters = registry.getAllConverters();
    console.log(JSON.stringify({
      converters: converters.map(c => ({
        name: c.name,
        sourceFormat: c.sourceFormat,
        targetFormat: c.targetFormat,
        supportedFeatures: c.supportedFeatures
      }))
    }, null, 2));
    return;
  }

  if (command === 'convert') {
    if (args.length !== 2) {
      console.error('Usage: node converter.js convert <input_file>');
      process.exit(1);
    }

    const inputFile = args[1];
    
    try {
      // Read input file
      const inputData = fs.readFileSync(inputFile, 'utf8');
      const request: ConversionRequest = JSON.parse(inputData);
      
      // Validate request
      if (!request.sourceFormat || !request.targetFormat || !request.schema) {
        throw new Error('Missing required fields: sourceFormat, targetFormat, schema');
      }

      // Find appropriate converter
      const converter = registry.findConverter(request.sourceFormat, request.targetFormat, request.converterName);
      
      if (!converter) {
        throw new Error(
          `No converter found for ${request.sourceFormat} → ${request.targetFormat}. ` +
          `Available converters: ${registry.getAllConverters().map(c => 
            `${c.sourceFormat}->${c.targetFormat}`).join(', ')}`
        );
      }

      if (DEBUG_MODE)
        console.error(`Using converter: ${converter.name}`);

      // Perform conversion
      const convertedSchema = await converter.convert(request.schema);
      
      // Output result to stdout
      const response: ConversionResponse = {
        schema: convertedSchema
      };
      
      console.log(JSON.stringify(response));
      
    } catch (error) {
      console.error(`Conversion error: ${error instanceof Error ? error.message : error}`);
      
      // Output error response to stdout
      const errorResponse: ConversionResponse = {
        schema: "",
        error: error instanceof Error ? error.message : "Unknown error"
      };
      
      console.log(JSON.stringify(errorResponse));
      process.exit(1);
    }
  } else {
    console.error(`Unknown command: ${command}`);
    process.exit(1);
  }
}

// Run the converter
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}