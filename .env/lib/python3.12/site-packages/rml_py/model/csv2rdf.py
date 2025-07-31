import csv
from rdflib import Graph
from rdflib.term import URIRef
from sys import exit
from .toRDF import ToRDF

class CSV2RDF(ToRDF):
    def __init__(self, csv_file) -> None:
        super().__init__()
        self.csv_file = csv_file
    
    def process_csv_to_rdf(self, subject_template, class_map, columns, output_graph_dict: dict) -> dict[str: tuple[Graph, str, str]]:
        match = self._find_template_match(subject_template)[1]

        if self.csv_file is None:
            print("CSV2RDF.process_csv_to_rdf: No source file found in the configuration file.")
            exit(1)

        if match is None:
            print("CSV2RDF.process_csv_to_rdf: No match found in the subject template.")
            exit(1)
        
        if class_map is None:
            print("CSV2RDF.process_csv_to_rdf: No class map found in the configuration file.")
            exit(1)

        if columns is None:
            print("CSV2RDF.process_csv_to_rdf: No columns found in the configuration file.")
            exit(1)

        if not isinstance(columns, list):
            print("CSV2RDF.process_csv_to_rdf: Columns must be a list.")
            exit(1)
        
        with open(str(self.csv_file), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create a URI node with the row ID as the ID
                _id_template = self._get_id_template(subject_template)
                _subject_map = subject_template.format(**{match: row[_id_template]})
                # print("columns: ", columns)

                for obj, column_name, predicate, datatype, language, split_by, template, logical_target_tuple in columns:
                    logical_target_obj, target, serialization, data_dump = logical_target_tuple
                    output_graph = self._create_output_graph(output_graph_dict, data_dump, serialization)

                    if isinstance(class_map['rdf_class'], list):
                        _subject = self._add_subject_map_list(_subject_map, class_map['rdf_class'], output_graph)

                    elif isinstance(class_map['rdf_class'], str):
                        _subject = self._add_subject_map_when_no_duplicates(_subject_map, class_map['rdf_class'], output_graph)

                    elif class_map['split_by'] is not None:
                        key = str(class_map['rdf_class_ref'])
                        _class_map_list = list(map(lambda x : URIRef(x), row[key].split(class_map['split_by'])))
                        _subject = self._add_subject_map_list(_subject_map, _class_map_list, output_graph)

                    elif isinstance(class_map['rdf_class_ref'], str):
                        key = str(class_map['rdf_class_ref'])
                        _class_map = URIRef(row[key])
                        _subject = self._add_subject_map_when_no_duplicates(_subject_map, _class_map, output_graph)

                    assert _subject is not None, "CSV2RDF.process_csv_to_rdf: No subject found in the configuration file."
                    assert isinstance(_subject, URIRef), "CSV2RDF.process_csv_to_rdf: Subject must be a URIRef."
                    
                    if obj is not None: 
                        self._add_triple(_subject, predicate, obj, datatype, language, split_by, template, output_graph)
                    else:
                        self._add_triple(_subject, predicate, row[str(column_name)], datatype, language, split_by, template, output_graph)

        return output_graph_dict