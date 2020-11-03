import uuid
from typing import Optional

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud import get_brand
from app.schemas import PersonDict
from app.stubs import person_response


def get_brand_id(auth_data: dict) -> Optional[str]:
    """
    Retrieves the brand_id from the supplied baas_auth data or raises an unauthorized exception if not found
    OrgId will be a string from auth decorator
    Returns:
        brand_id: Bond's internal Brand ID
    """
    if auth_data != None and "OrgId" in auth_data:
        brand_id = auth_data["OrgId"]
        return brand_id
    else:
        raise HTTPException(status_code=404, detail="brand_id not found")


def verify_person(person_id: str) -> PersonDict:
    """
    Check that the person exists in baas_person
    and return the baas_person response payload
    """
    # headers = {
    #     "Identity": headers.get("Identity"),
    #     "Authorization": headers.get("Authorization"),
    # }

    # bond_logger.info(f"Getting person {person_id} from {INTERSERVICE_HOST.PERSON}")

    # r = requests.get(
    #     url=f"{INTERSERVICE_HOST.PERSON}/{person_id}",
    #     headers=headers,
    # )

    # if r.status_code > 300:
    # bond_logger.error(
    #     f"Error encountered getting Person {person_id}. Error was {r.text}"
    # )
    # raise NotFound
    # person_data = PayloadValidation().payload_validation(r.json(), schema)
    return PersonDict(**person_response(person_id))
