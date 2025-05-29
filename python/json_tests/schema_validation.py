import json
from jsonschema import validate, ValidationError

# https://python-jsonschema.readthedocs.io/en/latest/validate/#the-basics
# https://json-schema.org/learn/miscellaneous-examples

schema = {
    "$schema": "http://json-schema.org/draft/2019-09/schema#",
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "taskId": {
            "type": "string",
            "format": "uuid",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
        },
        "status": {
            "enum": ["Running", "Failed", "Estimated"]
        },
        "role": {"type": "string", "maxLength": 4},
        "clientId": {"type": "integer", "minimum": 0},
        "code": {"type": "string", "pattern": "^[A-Z]{3}-\\d{3}$"}
    },
    "required": ["clientId", "role", "email", "status"],
    "additionalProperties": False
}

data = '''
    {
        "role": "USER",
        "clientId": 30,
        "email": "carlos.llano@sourcemeridian.com",
        "code": "ABC-1236",
        "status": "Running",
        "taskId": "c03a2c84-038d-4745-854a-5f9933aa6542"
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
