# Constants classes
class MathConstants:
    PI = 3.14159

class AppConfig:
    MAX_SIZE = 100
    MIN_SIZE = 10

class PhysicalConstants:
    HBAR_EVS = 6.582119569e-16  # eV s


# ConstantsManagement class
class ConstantsManagement:
    def __init__(self):
        # Set constants from separate classes as attributes
        for cls in [MathConstants, AppConfig]:
            for key, value in cls.__dict__.items():
                if not key.startswith("__"):
                    self.__dict__.update(**{key: value})

    def __setattr__(self, name, value):
        raise TypeError("Constants are immutable")

# Create an instance of ConstantsManagement
constants_manager = ConstantsManagement()

# Accessing constants
print(constants_manager.PI)  # Output: 3.14159
print(constants_manager.MAX_SIZE)  # Output: 100

# Attempting to modify constants raises a TypeError
#constants_manager.PI = 3.14  # Raises TypeError: Constants are immutable

# from proyect.constants import ConstantsManagement
# self.constants = ConstantsManagement()
# self.constants.PI