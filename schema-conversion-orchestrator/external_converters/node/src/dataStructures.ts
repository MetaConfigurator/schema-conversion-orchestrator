export enum SchemaLanguage {
  JsonSchema = "JsonSchema",
  MdModels = "MdModels",
  LinkMl = "LinkMl",
  Dtd = "Dtd",
  OntologyRdf = "OntologyRdf",
  Xsd = "Xsd",
  Owl = "Owl",
  Protobuf = "Protobuf",
  GraphQL = "GraphQL",
  JsonLD = "JsonLD",
  SHACL = "SHACL",
  PythonLinkMl = "Python_LinkMl",
  PythonPydantic = "Python_Pydantic",
  Julia_MdModels = "Julia_MdModels",
  Java_LinkMl = "Java_LinkMl",
  Mermaid = "Mermaid",
  Rust_MdModels = "Rust_MdModels",
  TypeScript_MdModels = "TypeScript_MdModels",
  Shex = "Shex",
  Docs_LinkMl = "Docs_LinkMl",
  SqlAlchemy = "SqlAlchemy",
}

export interface Converter {
  name: string;
  sourceLanguage: SchemaLanguage;
  targetLanguage: SchemaLanguage;
  convert: (schema: string) => Promise<string>;
}
