from pydantic import BaseModel, field_validator, AfterValidator, BeforeValidator, PlainValidator
from uuid import UUID, uuid4
from typing import Optional, Any, Annotated
from typing_extensions import Self
from enum import Enum

class RoleEnum(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    MAINTAINER = "maintainer"
    VIEWER = "viewer"

def is_email(email: str) -> str:
    if "@gmail.com" not in email:
        raise ValueError("Invalid email")
    return email

def remove_space_name(s: str):
    return s.strip()

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters')
    if not any(c.isupper() for c in password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not any(c.isdigit() for c in password):
        raise ValueError('Password must contain at least one digit')
    return password

class User(BaseModel):
    id: UUID
    name: Annotated[str, BeforeValidator(remove_space_name)]
    password: Annotated[str, PlainValidator(validate_password)]
    password_repeat: Annotated[str, PlainValidator(validate_password)]
    age: int
    email: Annotated[str, AfterValidator(is_email)]
    phone_no: str
    role: Optional[RoleEnum]
    
    @field_validator('phone_no', mode='before')
    @classmethod
    def validate_phone_no_before(cls, v):
        return v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
    
    @field_validator('age', mode='after')
    @classmethod
    def validate_age(cls, v):
        if not (18 <= v <= 100):
            raise ValueError('Age must be between 18 and 100')
        return v
    

user_dict = {
    "id": uuid4(),
    "name": "  AdityaZala  ",
    "password": "Aditya3919",
    "password_repeat": "Aditya3919",
    "age": 21,
    "email": "adityazala@gmail.com",
    "phone_no": "1234567890",
    "role": "admin"
}

parsed = User.model_validate(user_dict)
output = parsed.model_dump()

print(output)