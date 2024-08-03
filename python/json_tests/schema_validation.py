import json
from jsonschema import validate, ValidationError

# https://python-jsonschema.readthedocs.io/en/latest/validate/#the-basics
# https://json-schema.org/learn/miscellaneous-examples

schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "role": {"type": "string", "maxLength": 4},
        "clientId": {"type": "integer", "minimum": 0},
        "code": {"type": "string", "pattern": "^[A-Z]{3}-\\d{3}$"}
    },
    "required": ["clientId", "role", "email"],
    "additionalProperties": False
}

data = '''
{
    "role": "USER",
    "clientId": 30,
    "email": "carlos.llano@sourcemeridian.com",
    "code": "ABC-1234"
}
'''

json_data = json.loads(data)

try:
    validate(instance=json_data,
             schema=schema)
    print("JSON data is valid.")
except ValidationError as e:
        # print(e.schema_path)
        print("Invalid JSON payload: " + e.json_path + " reason: " + e.schema.get("error_msg", e.message))
