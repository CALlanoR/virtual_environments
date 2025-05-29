import jsonschema
from jsonschema import validate

schema = {
    "type": "object",
    "properties": {
        "reportTypeId": {
            "type": "integer"
        },
        "tables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        }
                    },
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "operatorId": {
                                    "type": "integer", 
                                    "enum": [1, 2, 3, 4]
                                },
                                "dataTypeId": {
                                    "type": "integer"
                                },
                                "fieldId": {
                                    "type": "integer"
                                },
                                "value": {}
                            },
                            "required": [
                                "id", 
                                "operatorId",
                                "dataTypeId",
                                "fieldId",
                                "value"
                            ],
                            "allOf": [
                                {
                                    "if": {"properties": {"operatorId": {"const": 1}}},
                                    "then": {"properties": {"value": {"type": "boolean"}}}
                                },
                                {
                                    "if": {"properties": {"operatorId": {"const": 2}}},
                                    "then": {"properties": {"value": {"type": "array", "items": {"type": "string"}}}}
                                },
                                {
                                    "if": {"properties": {"operatorId": {"const": 3}}},
                                    "then": {"properties": {"value": {"type": "number"}}}
                                },
                                {
                                    "if": {"properties": {"operatorId": {"const": 4}}},
                                    "then": {"properties": {"value": {"type": "string"}}}
                                }
                            ]
                        }
                    }
                },
                "required": ["id", "fields", "filters"]
            }
        }
    },
    "required": ["reportTypeId", "tables"]
}


json_example = {
    "reportTypeId": 2,
    "tables": [
        {
            "id": 8 ,
            "fields": [3,6,8],
            "filters": [
                {
                    "id": 30,
                    "operatorId": 1,
                    "dataTypeId": 0,
                    "fieldId": 15,
                    "value": False
                }
            ]
        },
         {
            "id": 9 ,
            "fields": [4,7,9],
            "filters": [
                {
                    "id": 31,
                    "operatorId": 2,
                    "dataTypeId": 0,
                    "fieldId": 16,
                    "value": ["a", "b", "c"]
                }
            ]
        },
         {
            "id": 10 ,
            "fields": [5,8,10],
            "filters": [
                {
                    "id": 32,
                    "operatorId": 3,
                    "dataTypeId": 0,
                    "fieldId": 17,
                    "value": 123.45
                }
            ]
        },
         {
            "id": 11 ,
            "fields": [6,9,11],
            "filters": [
                {
                    "id": 33,
                    "operatorId": 4,
                    "dataTypeId": 0,
                    "fieldId": 18,
                    "value": "some text"
                }
            ]
        }
    ]
}


try:
    validate(instance=json_example, schema=schema)
    print("JSON is valid")
except jsonschema.exceptions.ValidationError as e:
    print("JSON is invalid")
    print(e)