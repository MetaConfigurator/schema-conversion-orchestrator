export enum SchemaLanguage {
  JsonSchema = "JsonSchema",
  MdModels = "MdModels",
  LinkMl = "LinkMl",
  Dtd = "Dtd",
  OntologyRdf = "OntologyRdf",
  Xsd = "Xsd",
  Owl_TTL = "Owl_TTL",
  Owl_XML = "Owl_XML",
  Owl_OBO = "Owl_OBO",
  Owl_OFN = "Owl_OFN",
  Protobuf = "Protobuf",
  GraphQL = "GraphQL",
  SHACL_TTL = "SHACL_TTL",
  SHACL_JSON_LD = "SHACL_JSON_LD",
  Mermaid = "Mermaid",
  Shex = "Shex",
  SqlAlchemy = "SqlAlchemy",
}

export interface Converter {
  name: string;
  sourceLanguage: SchemaLanguage;
  targetLanguage: SchemaLanguage;
  convert: (schema: string) => Promise<string>;
  // Underlying npm package that performs the conversion. `library` must be a
  // resolvable package name so its version can be read from its package.json;
  // `libraryUrl` is a human-facing link (e.g. npm/GitHub page).
  library?: string;
  libraryUrl?: string;
}
