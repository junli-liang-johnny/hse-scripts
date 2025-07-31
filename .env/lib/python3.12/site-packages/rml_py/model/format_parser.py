from .namespace import formats

class FormatParser:
    def parse(self, format):
        if format == formats.Turtle:
            return 'turtle'
        else:
            print("Unknown format: ", format)
            raise ValueError('Unknown format')