from typing import Any

class Validate:

    @staticmethod
    def not_null(object:Any, err_msg: str = 'the value cannot be None') -> None:
        if not object:
            raise ValueError(err_msg)

    @staticmethod
    def not_empty(object: str, err_msg: str = 'the value cannot be None') -> None:
        Validate.not_null(object, err_msg)
        object = object.strip()
        if len(object) == 0:
            raise ValueError(err_msg)