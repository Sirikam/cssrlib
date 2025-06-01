class sCType:
    CLOCK = "clock"
    ORBIT = "orbit"
    CBIAS = "cbias"
    PBIAS = "pbias"
    HCLOCK = "hclock"

class gtime_t:
    def __str__(self):
        return "gtime_t_instance"  # Replace with meaningful string representation if needed

class local_corr:
    """ class for local corrections """

    def __init__(self):
        self.inet = -1
        self.inet_ref = -1
        self.ng = -1
        self.pbias = {}
        self.cbias = {}
        self.iode = None
        self.dorb = None
        self.dclk = None
        self.hclk = None
        self.stec = None
        self.trph = None
        self.trpw = None
        self.ci = None
        self.ct = None
        self.quality_trp = None
        self.quality_stec = None
        self.sat_n = []
        self.t0 = {}
        self.cstat = 0            # status for receiving CSSR message
        self.t0s = {}
        sc_t = [sCType.CLOCK, sCType.ORBIT, sCType.CBIAS, sCType.PBIAS,
                sCType.HCLOCK]
        for sc in sc_t:
            self.t0s[sc] = gtime_t()

# Recursive function to print attributes
def print_object_variables(obj, prefix=""):
    """
    Recursively print all attributes of an object, including nested objects.
    """
    if hasattr(obj, "__dict__"):  # If the object has attributes
        for key, value in vars(obj).items():
            if isinstance(value, (dict, list, tuple, set)):
                print(f"{prefix}{key}: {type(value).__name__} ({len(value)})")
                print_object_variables(value, prefix + f"{key}.")
            elif hasattr(value, "__dict__"):  # If it's a nested object
                print(f"{prefix}{key}: {type(value).__name__}")
                print_object_variables(value, prefix + f"{key}.")
            else:  # It's a basic type
                print(f"{prefix}{key}: {value}")
    elif isinstance(obj, dict):  # If the object is a dictionary
        for key, value in obj.items():
            if isinstance(value, (dict, list, tuple, set)):
                print(f"{prefix}{key}: {type(value).__name__} ({len(value)})")
                print_object_variables(value, prefix + f"{key}.")
            elif hasattr(value, "__dict__"):  # Nested object
                print(f"{prefix}{key}: {type(value).__name__}")
                print_object_variables(value, prefix + f"{key}.")
            else:  # Basic type
                print(f"{prefix}{key}: {value}")
    elif isinstance(obj, list):  # Handle lists
        for index, value in enumerate(obj):
            if isinstance(value, (dict, list, tuple, set)):
                print(f"{prefix}[{index}]: {type(value).__name__} ({len(value)})")
                print_object_variables(value, prefix + f"[{index}].")
            elif hasattr(value, "__dict__"):  # Nested object
                print(f"{prefix}[{index}]: {type(value).__name__}")
                print_object_variables(value, prefix + f"[{index}].")
            else:  # Basic type
                print(f"{prefix}[{index}]: {value}")
    else:  # Basic type or unknown
        print(f"{prefix}: {obj}")

# Recursive function to write attributes to a file
def write_object_variables(obj, file, prefix=""):
    """
    Recursively write all attributes of an object, including nested objects, to a file.
    """
    if hasattr(obj, "__dict__"):  # If the object has attributes
        for key, value in vars(obj).items():
            if isinstance(value, (dict, list, tuple, set)):
                file.write(f"{prefix}{key}: {type(value).__name__} ({len(value)})\n")
                write_object_variables(value, file, prefix + f"{key}.")
            elif hasattr(value, "__dict__"):  # If it's a nested object
                file.write(f"{prefix}{key}: {type(value).__name__}\n")
                write_object_variables(value, file, prefix + f"{key}.")
            else:  # It's a basic type
                file.write(f"{prefix}{key}: {value}\n")
    elif isinstance(obj, dict):  # If the object is a dictionary
        for key, value in obj.items():
            if isinstance(value, (dict, list, tuple, set)):
                file.write(f"{prefix}{key}: {type(value).__name__} ({len(value)})\n")
                write_object_variables(value, file, prefix + f"{key}.")
            elif hasattr(value, "__dict__"):  # Nested object
                file.write(f"{prefix}{key}: {type(value).__name__}\n")
                write_object_variables(value, file, prefix + f"{key}.")
            else:  # Basic type
                file.write(f"{prefix}{key}: {value}\n")
    elif isinstance(obj, list):  # Handle lists
        for index, value in enumerate(obj):
            if isinstance(value, (dict, list, tuple, set)):
                file.write(f"{prefix}[{index}]: {type(value).__name__} ({len(value)})\n")
                write_object_variables(value, file, prefix + f"[{index}].")
            elif hasattr(value, "__dict__"):  # Nested object
                file.write(f"{prefix}[{index}]: {type(value).__name__}\n")
                write_object_variables(value, file, prefix + f"[{index}].")
            else:  # Basic type
                file.write(f"{prefix}[{index}]: {value}\n")
    else:  # Basic type or unknown
        file.write(f"{prefix}: {obj}\n")
