import re
from typing import Optional, Union, List
from datetime import date
from uuid import UUID
from pydantic import BaseModel, ValidationError, validator, SecretStr

digits_dashes = "^[0-9-]*$"

from pydantic.dataclasses import dataclass


class TestTest(BaseModel):
    optional_thing: Optional[str]

    class Config:
        extra = "forbid"


class ProgrammaticPayload(BaseModel):
    person_id: UUID
    ssn: str
    test: Optional[TestTest]

    @validator("ssn")
    def validate_v_format(cls, v):
        print(f"===== the value being validated is {v}")
        print(len(v))
        if len(v) != 9 and len(v) != 11:
            raise ValueError("must be in ######### or ###-##-#### format")
        if not re.match(digits_dashes, v):
            raise ValueError("must be in ######### or ###-##-#### format")
        if v.isdigit():
            v = "-".join([v[:3], v[3:5], v[5:]])
            return v
        else:
            return v

    class Config:
        extra = "forbid"


class Brand(BaseModel):
    brand_id: UUID
    kyc_vendor: str

    class Config:
        orm_mode = True


class KYCConfigDict(BaseModel):
    validation: str
    ofac_similarity_threshold: int
    ip_risk_threshold: int
    mobile_first_name_threshold: int
    mobile_last_name_threshold: int
    mobile_address_threshold: int
    email_risk_threshold: int
    email_domain_risk_threshold: int


class ConfigDict(BaseModel):
    kyc_vendor: str
    kyc_config: KYCConfigDict


class TestDict(BaseModel):
    first: str
    second: str





# if using dataclass
# class MyConfig:
#     extra = "ignore"
#     validate_assignment = True
#     json_encoders = {
#         SecretStr: lambda v: v.get_secret_value() if v else None,
#     }


# @dataclass(config=MyConfig)
class PersonDict(BaseModel):
    """
    person_id: str
    \nfirst_name: str
    \nmiddle_name: SecretStr
    \nlast_name: str
    \ndob: date
    \naddresses: List[AddressDict]
    \nssn: Optional[str]
    \nphone: Optional[str]
    \nphone_country_code: Optional[str]
    \nip: Optional[str]
    \nemail: Optional[str]
    """

    person_id: str
    first_name: str
    middle_name: SecretStr
    last_name: str
    dob: date
    addresses: List[AddressDict]
    ssn: Optional[str]
    phone: Optional[str]
    phone_country_code: Optional[str]
    ip: Optional[str]
    email: Optional[str]

    @validator("first_name")
    def val(cls, first_name):
        if first_name == "bob":
            raise ValueError("bob is not allowed")
        return first_name

    # if subclassing BaseModel
    class Config:
        extra = "ignore"
        # validate_assignment decides if your validator decs should run when you assign
        # a variable to one of the schema's attributes
        # i.e. if you do person.first_name = "bob" after instnaitatng person as a pydantic model
        validate_assignment = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }

class AddressDict(BaseModel):
    street: str
    street2: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str


address = AddressDict({
    "street": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "11111",
    "country": "US"
})

