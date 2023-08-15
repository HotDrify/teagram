from typing import Union, Type
from functools import partial

ALLOWED_TYPES = Union[int, str, bool, None]

class ValidationError(Exception):
    """
    Вызывается если конвертирование значения прошло неудачно
    Raises if the value conversion fails
    """

class Validator:
    def __init__(self, type):
        self.type: Type = type

class Integer(Validator):
    """
    Целое число/Integer
    
    Args:
        minimum (``int``, optional):
            Минимальное значение/Minimum value
        
        maximum (``int``, optional):
            Максимальное значение/Maximum value
    """

    def __init__(
        self,
        *,
        minimum: int = None,
        maximum: int = None
    ):
        super().__init__(partial(
            self._valid,
            minimum=minimum,
            maximum=maximum
        ))

    @staticmethod
    def _valid(value: ALLOWED_TYPES, *, minimum: int = None, maximum: int = None) -> Union[int, None]:
        try:
            value = int(str(value).strip())
        except ValueError:
            raise ValidationError('Значение должно быть цифрой / Value must be a number')

        if minimum and value < minimum:
            raise ValidationError('Значение должно быть больше минимума / Value must be greater than minimum')
        
        if maximum and value > maximum:
            raise ValidationError('Значение должно быть меньше максимума / Value must be lower than maximum')
        
        return value

class String(Validator):
    """
    Строка/String
    
    Args:
        min_len (``int``, optional):
            Минимальная длина строки/Minimum length of string
        
        max_len (``int``, optional):
            Максимальная длина строки/Maximum length of string
    """

    def __init__(
        self,
        *,
        min_len: int = None,
        max_len: int = None
    ):
        super().__init__(partial(
            self._valid,
            min_len=min_len,
            max_len=max_len
        ))

    @staticmethod
    def _valid(value: ALLOWED_TYPES, *, min_len: int = None, max_len: int = None) -> Union[str, None]:
        try:
            value = str(value)
        except ValueError:
            raise ValidationError('Значение должно быть строкой / Value must be a string')

        if min_len and len(value) < min_len:
            raise ValidationError('Длина должно быть больше минимума / Length must be greater than minimum')
        
        if max_len and len(value) > max_len:
            raise ValidationError('Длина должна быть меньше максимума / Length must be lower than maximum')
        
        return value
            


class Boolean(Validator):
    """Логическое значение/Logic value"""

    def __init__(self):
        super().__init__(self._valid)

    @staticmethod
    def _valid(value: ALLOWED_TYPES) -> bool:
        true = [True, 'true', 'yes', 'on', '1', 1]
        false = [False, 'false', 'no', 'off', "0", 0]

        try:
            value = str(value).lower()

            if value not in true + false:
                raise ValidationError('Передаваемое значение должно быть логическим / Passed value must be a boolean')
        except TypeError:
            raise ValidationError('Передаваемое значение должно быть логическим / Passed value must be a boolean')

        return value in true