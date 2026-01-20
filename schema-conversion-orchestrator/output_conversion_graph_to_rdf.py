from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from converter import ConversionGraph


def conversion_graph_to_rdf(conversion_graph: ConversionGraph, output_path):
    EX = Namespace("http://example.org/conversions/")

    g = Graph()
    g.bind("ex", EX)
    g.bind("rdfs", RDFS)

    # define a class and a property for conversions
    CONVERSION = EX.Conversion
    HAS_NAME = EX.name
    HAS_SOURCE = EX.sourceLanguage
    HAS_TARGET = EX.targetLanguage

    for source, converters in conversion_graph.items():
        for converter in converters:
            src = string_normalize(str(converter.source_language))
            tgt = string_normalize(str(converter.target_language))

            # create URIs for languages
            src_uri = EX[f"language/{src}"]
            tgt_uri = EX[f"language/{tgt}"]

            # add label for readability
            g.add((src_uri, RDFS.label, Literal(src)))
            g.add((tgt_uri, RDFS.label, Literal(tgt)))

            # create a conversion node (reified edge)
            conv_uri = EX[f"conversion/{string_normalize(converter.name)}"]

            g.add((conv_uri, RDF.type, CONVERSION))
            g.add((conv_uri, HAS_NAME, Literal(converter.name)))
            g.add((conv_uri, HAS_SOURCE, src_uri))
            g.add((conv_uri, HAS_TARGET, tgt_uri))

    # serialize as Turtle to file
    g.serialize(output_path, format="turtle")


# replace intermediate whitespaces by underline and trim and avoid other issues to make it a valid URI fragment
def string_normalize(s: str) -> str:
    return "_".join(s.strip().split())
