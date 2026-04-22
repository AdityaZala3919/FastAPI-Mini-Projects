from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_snake, to_pascal
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

class RoleEnum(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    MAINTAINER = "maintainer"
    VIEWER = "viewer"

class User(BaseModel):
    """
    ═══════════════════════════════════════════════════════════════════════════
    ConfigDict EXPLANATION:
    ═══════════════════════════════════════════════════════════════════════════
    
    EXTRA TYPES (How to handle extra fields not defined in the model):
    ────────────────────────────────────────────────────────────────────────
    • 'ignore'  → Extra fields are silently ignored (default behavior)
    • 'forbid'  → Raises ValidationError if extra fields are provided
    • 'allow'   → Extra fields are stored in __pydantic_extra__ dict
    
    ALIAS_GENERATOR TYPES (Automatic field name transformation):
    ────────────────────────────────────────────────────────────────────────
    • to_camel   → snake_case → camelCase (first_name → firstName)
    • to_pascal  → snake_case → PascalCase (first_name → FirstName)
    • to_snake   → Any format → snake_case (firstName → first_name)
    • Custom function → Define your own transformation logic
    • AliasGenerator() → Different rules for validation vs serialization
    
    HOW ALIAS_GENERATOR WORKS:
    Your Python fields use snake_case (PEP 8 convention).
    alias_generator automatically converts them to match external API formats.
    
    Example:
      Field name: first_name
      With to_camel: Generated alias becomes "firstName"
      Input data {'firstName': 'John'} matches the alias
      You access it as: response.first_name
    ═══════════════════════════════════════════════════════════════════════════
    """
    
    model_config = ConfigDict(
        # ─────────────────────────────────────────────────────────────────────
        # STRING TRANSFORMATIONS
        # ─────────────────────────────────────────────────────────────────────
        str_to_lower=True,
        # Automatically converts all string values to lowercase during validation
        # Example: "AdityaZala" → "adityazala"
        # Note: Only affects string type fields, not aliases
        
        str_max_length=30,
        # Sets maximum length for all string fields (unless overridden per field)
        # Example: A string with 31+ chars will fail validation
        
        # ─────────────────────────────────────────────────────────────────────
        # EXTRA FIELDS HANDLING
        # ─────────────────────────────────────────────────────────────────────
        extra="forbid",
        # Options: "allow", "forbid", "ignore"
        # "forbid"  → Raises error if unknown fields are provided
        #             Example: {'unknown_field': 'value'} → ValidationError
        # "ignore"  → Unknown fields are silently discarded (default)
        # "allow"   → Unknown fields stored in __pydantic_extra__ dict
        
        # ─────────────────────────────────────────────────────────────────────
        # ENUM HANDLING
        # ─────────────────────────────────────────────────────────────────────
        use_enum_values=True,
        # When True: Serialization outputs enum values, not enum names
        # Example with RoleEnum:
        #   Without: model_dump() → {'role': <RoleEnum.admin: 'admin'>}
        #   With:    model_dump() → {'role': 'admin'}  (just the value)
        
        # ─────────────────────────────────────────────────────────────────────
        # ALIAS GENERATOR (Field name transformation)
        # ─────────────────────────────────────────────────────────────────────
        alias_generator=to_camel,
        # Automatically generates aliases for all fields using to_camel
        # to_camel: snake_case → camelCase
        #   phone_no → phoneNo
        #   email_address → emailAddress
        #   user_id → userId
        # 
        # Alternative options:
        #   to_pascal  → FirstName, PhoneNo, EmailAddress
        #   to_snake   → (usually for converting FROM camelCase TO snake)
        # 
        # Benefits:
        # • Eliminates need for Field(alias='...') on every field
        # • Automatically matches external API naming conventions
        # • Your Python code stays PEP 8 compliant (snake_case)
        
        # ─────────────────────────────────────────────────────────────────────
        # VALIDATION MODES (When to accept field names vs aliases)
        # ─────────────────────────────────────────────────────────────────────
        validate_by_alias=True,
        # If True: Accepts input using generated aliases
        # Example: {'phoneNo': '1234567890'} ✓ Works (matches generated alias)
        # If False: Would only accept {'phone_no': '1234567890'} ✗
        
        validate_by_name=True,
        # If True: Accepts input using the actual Python field name
        # Example: {'phone_no': '1234567890'} ✓ Works (uses field name)
        # If False: Would only accept {'phoneNo': '1234567890'} ✗
        #
        # COMBINATION BEHAVIOR:
        # Both True:  Accepts BOTH aliases AND field names (most flexible)
        # Example:
        #   {'phoneNo': '1234567890'}   ✓ Works (alias)
        #   {'phone_no': '1234567890'}  ✓ Works (field name)
        #
        # Only validate_by_alias=True:  Only aliases accepted
        # Only validate_by_name=True:   Only field names accepted
    )
    
    id: UUID
    name: str
    password: str
    age: int
    email: str
    phone_no: str
    # ↑ Note: Field name is 'phone_no' (snake_case - Python convention)
    #   With to_camel alias_generator, accepts input as 'phoneNo' (camelCase)
    
    role: Optional[RoleEnum] = Field(
        default=RoleEnum.VIEWER, validate_default=True
    )
    # ↑ If not provided, defaults to VIEWER
    #   use_enum_values=True will serialize as 'viewer' (the enum value)

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE: Using the User model with ConfigDict settings
# ═══════════════════════════════════════════════════════════════════════════

user_dict = {
    # INPUT DATA uses camelCase (from external API, e.g., JavaScript frontend)
    "id": uuid4(),
    "name": "AdityaZala",
    # ↑ This will be converted to "adityazala" by str_to_lower=True
    
    "password": "Aditya3919",
    "age": 21,
    "email": "adityazala@gmail.com",
    "phoneNo": "1234567890",
    # ↑ Uses 'phoneNo' (camelCase) - matches the generated alias from to_camel
    #   Without alias_generator, you'd need Field(alias='phoneNo')
    
    "role": "admin"
    # ↑ Input as string, will be converted to enum value by use_enum_values=True
}

# ─────────────────────────────────────────────────────────────────────────
# VALIDATION: Pydantic processes the input dict
# ─────────────────────────────────────────────────────────────────────────
parsed = User.model_validate(user_dict)
# What happens:
# 1. 'phoneNo' key matches phone_no field via to_camel alias ✓
# 2. "AdityaZala" is converted to "adityazala" by str_to_lower ✓
# 3. "admin" is converted to RoleEnum.ADMIN ✓
# 4. No unknown fields (extra='forbid' is satisfied) ✓

# print(parsed.model_json_schema())
# print(parsed.model_dump_json())
print(parsed)

output = parsed.model_dump()
# ─────────────────────────────────────────────────────────────────────────
# SERIALIZATION OUTPUT (without by_alias=True):
# ─────────────────────────────────────────────────────────────────────────
# {
#     'id': UUID(...),
#     'name': 'adityazala',        ← Lowercase (str_to_lower=True)
#     'password': 'aditya3919',    ← Lowercase (str_to_lower=True)
#     'age': 21,
#     'email': 'adityazala@gmail.com',
#     'phoneNo': '1234567890',     ← Uses alias (default serialization)
#     'role': 'admin'              ← Enum value (use_enum_values=True)
# }
#
# Note: By default, model_dump() uses aliases if alias_generator is set.
# To get field names instead: model_dump(by_alias=False)

print(output)