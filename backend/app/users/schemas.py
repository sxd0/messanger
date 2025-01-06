from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SUserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str


    model_config = ConfigDict(from_attributes=True)




class SUserLogin(BaseModel):
    email: EmailStr
    password: str