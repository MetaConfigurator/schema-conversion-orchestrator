import express from 'express';

const app = express();
const port = 3001;

app.use(express.json());

app.post('/convert', (req, res) => {
  const { schema, sourceFormat, targetFormat } = req.body;
  const result = {
    schema: `[Node.js Dummy] Converted from ${sourceFormat} to ${targetFormat}: ${schema}`
  };
  res.json(result);
});

app.listen(port, () => {
  console.log(`Node.js converter listening at http://localhost:${port}`);
});
