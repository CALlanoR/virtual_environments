import json

login_response_schema = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "userRol": {"type": "string"},
        "userId": {"type": "integer"},
        "clientApis": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "agreementAccepted": {"type": "boolean"},
        "capabilities": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "tagsList": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["token", "userRol", "userId"]
}

def convert_schema_to_string(schema):
    properties = schema["properties"]
    _required = schema.get("required", [])
    lines = []

    for prop, details in properties.items():
        prop_type = details["type"]
        if prop_type == "array":
            item_type = details["items"]["type"]
            line = f"{prop}::[{item_type}]"
        else:
            line = f"{prop}::{prop_type}"

        lines.append(line)

    return "\n".join(lines)

LOGINRESPONSE = convert_schema_to_string(login_response_schema)
print(LOGINRESPONSE)
