"""
Demonstration of using parser with match statement.
"""

from ijp import IncrementalJSONParser

# Example JSON data split into chunks
json_chunks = [
    '{"price": 19.99, "itemNo": "3735272", "modulars": [',
    '{"zone": "A", "section": 29, "position": 10},',
    '{"zone": "A", "section": 29, "position": 15}]}'
]

# Initialize the parser with the JSON chunks
parser = IncrementalJSONParser(json_chunks)

# Process each tuple returned by the parser
for path, data_type, value in parser:
    match (path, data_type):
        case (['price'], 'float'):
            print(f"Price found: {value}")
        case (['itemNo'], 'string'):
            print(f"Item number found: {value}")
        case (['modulars', index, 'zone'], 'string') if isinstance(index, int):
            print(f"Modular {index} zone: {value}")
        case (['modulars', index, 'section'], 'int') if isinstance(index, int):
            print(f"Modular {index} section: {value}")
        case (['modulars', index, 'position'], 'int') if isinstance(index, int):
            print(f"Modular {index} position: {value}")
        case (_, 'stringpart'):
            # Handle string parts if needed
            print(f"String part found at {path}: {value}")
        case _:
            print(f"Unhandled data type {data_type} at {path} with value {value}")

# Close the parser
parser.close()
