class Syntax:
    keywords = [
            "let",
            "end",
            "cls",
            "if",
            "then",
            "else",
            "endif"
            "for",
            "to",
            "next",
            "proc",
            "pend",
            "dim",
            "while",
            "wend",
            "do",
            "loop",
            "select",
            "case",
            "return",
            "and",
            "or",
            "type",
            "field",
            "tend",
            "new",
            "ptr"
        ]

    data_types = [
        "void",
        "char",    # 8  bits   [−127, +127]
        "uchar",   # 8  bits   [0, 255]
        "short",   # 16 bits   [−32767, +32767]
        "ushort",  # 16 bits   [0, 65535]
        "int",     # 32 bits   [-2147483648, 2147483647]
        "uint",    # 32 bits   [0, 4,294,967,295 ]
        "long",    # 64 bits   [-9223372036854775808, 9223372036854775807]
        "ulong",   # 64 bits   [0 to 18446744073709551615]
        "float",   # 32 bits   [1.2E-38 to 3.4E+38] (6 decimal places)
        "double",   # 64 bits   [2.3E-308 to 1.7E+308] (15 decimal places)
        "string",
        "size"
    ]

    numeric_data_types = [
        "char",  
        "uchar", 
        "short", 
        "ushort",
        "int",   
        "uint",  
        "long",  
        "ulong", 
        "size",
        "float",
        "double"
    ]

    none_float_numeric_data_types = [
        "char",  
        "uchar", 
        "short", 
        "ushort",
        "int",   
        "uint",  
        "long",  
        "ulong", 
        "size"
    ]

    float_numeric_data_types = [
        "float",
        "double"    
    ]

    numeric_type_hierarchy = {
        "char": 1,
        "uchar": 2,
        "short": 3,
        "ushort": 4,
        "int": 5,
        "uint": 6,
        "size": 7,
        "long": 8,
        "ulong": 9,
        "float": 10,
        "double": 11
    }

    numeric_data_type_ranges = {
        "char": (-128, 127),
        "uchar": (0, 255),
        "short": (-32768, 32767),
        "ushort": (0, 65535),
        "int": (-2147483648, 2147483647),
        "uint": (0, 4294967295),
        "long": (-9223372036854775808, 9223372036854775807),
        "ulong": (0, 18446744073709551615)
    }

   
