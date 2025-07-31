from rdflib import Graph, URIRef, Literal, namespace
import re
from .namespace import rdf
from sys import exit
from urllib.parse import urlparse

class ToRDF:
    def __init__(self):
        pass

    def to_rdf(self, subject_template, class_map, columns, output_graph_dict: dict) -> dict[str: tuple[Graph, str, str]]:
        if class_map is None:
            print("ToRDF.to_rdf: No class map found in the configuration file.")
            exit(1)

        if columns is None:
            print("ToRDF.to_rdf: No columns found in the configuration file.")
            exit(1)

        if not isinstance(columns, list):
            print("ToRDF.to_rdf: Columns must be a list.")
            exit(1)
        
        for obj, column_name, predicate, datatype, language, split_by, template, logical_target_tuple in columns:
            logical_target_obj, target, serialization, data_dump = logical_target_tuple
            output_graph = self._create_output_graph(output_graph_dict, data_dump, serialization)

            _subject_template_URI = URIRef(subject_template)

            if isinstance(class_map['rdf_class'], list):
                self._add_class_map_list(_subject_template_URI, class_map['rdf_class'], output_graph)
            else:
                self._add_class_map(_subject_template_URI, class_map['rdf_class'], output_graph)

            if obj is not None:
                self._add_triple(_subject_template_URI, predicate, obj, datatype, language, split_by, template, output_graph)
            else:
                self._add_triple(_subject_template_URI, predicate, column_name, datatype, language, split_by, template, output_graph)

    def _add_class_map(self, subject_map, class_map, graph: Graph):
        graph.add((URIRef(subject_map), URIRef(rdf.type), class_map))

    def _add_class_map_list(self, subject_map, class_map_list, graph: Graph) -> URIRef:
        if not isinstance(class_map_list, list):
            print("ToRDF._add_class_map_list: Class map must be a list.")
            exit(1)
        
        for class_map in class_map_list:
            self._add_class_map(subject_map, class_map, graph)

    def _add_subject_map_list(self, subject_map, class_map, graph: Graph) -> URIRef:
        node = None

        for class_item in class_map:
            node = self._add_subject_map_when_no_duplicates(subject_map, class_item, graph)

        return node

    def _add_subject_map_when_no_duplicates(self, subject_map, class_map, graph: Graph) -> URIRef:
        if self._contains_triple(graph, subject_map, URIRef(rdf.type), class_map):
            return URIRef(subject_map)

        # Create a URI node with the row ID as the ID
        node = URIRef(subject_map)
        graph.add((node, URIRef(rdf.type), class_map))
        return node

    def _create_output_graph(self, graph_dict: dict, data_dump: URIRef, serialization):
        if data_dump in graph_dict:
            return graph_dict[data_dump][0]
        
        output_graph = Graph()
        graph_dict[data_dump] = (output_graph, serialization)
        return output_graph

    def _add_triple(self, subject, predicate, obj, datatype, language, split_by, template, output_graph):
        assert subject is not None, "ToRDF._add_triple: Subject cannot be None."

        match = self._find_template_match(template)[1]
        if obj == "" or obj is None:
            return

        # add url
        if match and split_by is not None:
            values = obj.replace('\n', '').split(split_by)
            for value in values:
                objectNode = URIRef(template.format(**{match: value}))
                output_graph.add((subject, predicate, objectNode))
            return

        if match:
            # Create a URI node with the row ID as the ID
            objectNode = URIRef(template.format(**{match: obj}))
            output_graph.add((subject, predicate, objectNode))
            return

        # add literal
        if split_by:
            # Split the cell value by the specified delimiter
            values = obj.replace('\n', '').split(split_by)
            for value in values:
                # Add a triple for each value
                cell_value = self._format_cell_value(value, datatype, language)
                self._add_by_datatype(output_graph, subject, predicate, cell_value, datatype, language)
        else:
            # Add a single triple for the cell value
            self._add_by_datatype(output_graph, subject, predicate, obj, datatype, language)

    def _contains_triple(self, graph, subject, predicate, object):
        return any(True for _ in graph.triples((subject, predicate, object)))

    def _add_by_datatype(self, graph, subject, predicate, object, datatype, language):
        if datatype == namespace.XSD.anyURI:
            graph.add((subject, predicate, URIRef(object)))
        else:
            try :
                graph.add((subject, predicate, Literal(object, datatype=datatype, lang=language)))
            except:
                print("Error: ", object, ", datatype: ", datatype, ", language: ", language, "\n")
                exit(1)

    def _format_cell_value(self, value, datatype, language):
        return Literal(value.replace("\n", " ").strip(), datatype=datatype, lang=language)

    def _is_uri(self, string) -> bool:
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    def _find_template_match(self, template):
        if template is None:
            return None, None, None

        match = re.match(r"(.*)\{(.*)\}(.*)", template)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return None, None, None

    def _get_id_template(self, template):
        # The pattern checks for anything between curly braces
        pattern = r'\{(.*?)\}'
        match = re.search(pattern, template)
        return match.group(1) if match else None