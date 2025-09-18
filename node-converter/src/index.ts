// index.ts
import express from "express";
import fetch from "node-fetch";
import { Converter } from "./dataStructures";
import { dummyConverter } from "./dummyConverter";

const app = express();
const port = 3001;

// All available converters in this Node.js service
const converters: Converter[] = [dummyConverter];

// Middleware
app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// Conversion endpoint
app.post("/convert", async (req, res) => {
  const { schema, sourceFormat, targetFormat } = req.body;

  console.log("Received conversion request:", { sourceFormat, targetFormat });

  try {
    const converter = converters.find(
      (c) => c.sourceFormat === sourceFormat && c.targetFormat === targetFormat
    );

    if (!converter) {
      console.error(`No converter found for ${sourceFormat} → ${targetFormat}`);
      return res.status(404).json({
        error: `No converter found for ${sourceFormat} → ${targetFormat}`,
      });
    }

    const result = await converter.convert(schema);
    console.log("Conversion result:", result);
    return res.json({ schema: result });
  } catch (err: any) {
    console.error("Conversion error:", err);
    return res.status(500).json({ error: err.message || "Conversion failed" });
  }
});

// Register converters with Python backend
async function registerWithPythonBackend() {
  for (const converter of converters) {
    try {
      const response = await fetch("http://localhost:5002/registerConversion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: converter.name,
          serviceAddress: converter.serviceAddress,
          sourceFormat: converter.sourceFormat,
          targetFormat: converter.targetFormat,
          supportedFeatures: converter.supportedFeatures,
        }),
      });

      if (!response.ok) {
        console.error(
          `Failed to register ${converter.name}:`,
          await response.text()
        );
      } else {
        console.log(`Registered converter ${converter.name} with Python backend`);
      }
    } catch (error) {
      console.error(`Error registering converter ${converter.name}:`, error);
    }
  }
}

// Start service
app.listen(port, () => {
  console.log(`Node.js converter listening at http://localhost:${port}`);
  registerWithPythonBackend();
});
