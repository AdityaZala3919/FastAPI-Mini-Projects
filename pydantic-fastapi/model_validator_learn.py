from pydantic import BaseModel, model_validator
from pydantic.alias_generators import to_camel, to_snake, to_pascal
from uuid import UUID, uuid4
from typing import Optional, Any
from typing_extensions import Self
from enum import Enum

class RoleEnum(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    MAINTAINER = "maintainer"
    VIEWER = "viewer"

class User(BaseModel):
    id: UUID
    name: str
    password: str
    password_repeat: str
    age: int
    email: str
    phone_no: str
    role: Optional[RoleEnum]
    
    @model_validator(mode='after')
    def check_passwords(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords dont match")
        return self
    
    @model_validator(mode='before')
    def correct_phone_no(cls, data):
        data["phone_no"] = "+91-"+data["phone_no"]
        return data
    
    @model_validator(mode='before')
    def check_card_number_not_present(cls, data):
        if 'card_number' in data:
            raise ValueError("'card_number' should not be included")
        return data

user_dict = {
    "id": uuid4(),
    "name": "AdityaZala",
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