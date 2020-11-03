import time
import uuid
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from pydantic import ValidationError
from app import models, schemas
from app.crud import create_brand, get_brand, get_kyc_config
from app.database import SessionLocal, engine
from app.errors import (
    CBWError,
    KYCProviderError,
    http_exception_handler,
    kyc_provider_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from pydantic import SecretStr
from app.middleware import ResponseTime
from app.schemas import ConfigDict, ProgrammaticPayload, TestDict
from app.utils import get_brand_id, verify_person

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(ResponseTime)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(KYCProviderError, kyc_provider_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/kyc/programmatic", status_code=201)
def create_item(
    payload: ProgrammaticPayload, db: Session = Depends(get_db)
) -> JSONResponse:
    brand_id: str = str(uuid.uuid4())
    create_brand(db, brand_id, "cbw")
    auth_data: Dict[str, str] = {"OrgId": brand_id}
    # this is stuff dec would do

    # brand_id: str = get_brand_id(auth_data)
    kyc_vendor: str = get_brand(db, brand_id).kyc_vendor
    kyc_config: dict = get_kyc_config(brand_id, kyc_vendor)
    config = ConfigDict(kyc_vendor=kyc_vendor, kyc_config=kyc_config)

    # stub
    person_id = str(uuid.uuid4())

    person_data = verify_person(person_id)
    # .json() returns a json string (lots of \'s)
    # .dict() returns what you expect
    # returning the pydantic model also works

    print(type(person_data.addresses[0].address_id))
    print(f"the middle name is: {person_data.middle_name}")
    if person_data.middle_name == "danger":
        print("without .get_secret_value() we can compare it")
    else:
        print("without .get_secret_value() we can NOT compare it")
    if person_data.middle_name.get_secret_value() == "danger":
        print("able to compare if using get_secret_value")
    else:
        print("even with .get we can't compare it")
    # print(person_data.middle_name + "asdf")

    # when assigning a pydantic model's attribute, it checks type
    y: str = person_data.first_name

    # when assigning a pydantic mode's secret, it doesn't check type
    x = person_data.middle_name
    print("printing the value of x")
    print(f"x (without .get_s_v= {x}")
    print(f"x.get_secret_value() = {x.get_secret_value()}")
    print("concating 'asdf' to middle_name.get_secret_value")
    print(person_data.middle_name.get_secret_value() + "asdf")
    return person_data
    raise KYCProviderError()
    # response: dict
    # status: int
    # response, status = kyc_switcher[kyc_vendor](
    #     brand_id=brand_id,
    #     person_data=person_data,
    #     payload=payload,
    #     config=config,
    # )

    # return response, status