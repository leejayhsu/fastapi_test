# # Modules from the Python Standard Library
# import base64
# import copy
# from datetime import date
# import hashlib
# import os
# import json
# import time
# from typing import cast, Tuple
# import uuid
# from uuid import UUID

# # Third Party modules from the public PyPI
# from ecdsa import SigningKey, NIST256p
# from ecdsa.util import sigencode_der
# from marshmallow import ValidationError

# # Internal modules from either Artifactory or the current project
# from app.schemas import ValidCBWSchema
# from app.validations import PayloadValidation
# from app.constants import CBW_API_KEY, CBW_CREDENTIAL
# from app.errors import CBWError
# from bond_logger import bond_logger


# def add_cbw_fields(person_data: dict, request_payload: dict) -> None:
#     """
#     adds cbw specific fields from request body into person_data
#     marshmallow rejects unknown keys be default, so this should be safe

#     since person_id is already supplied from person_data, pop that from request payload
#     before assigning new keys to the person_data dict
#     """
#     bond_logger.info("Adding CBW Fields to person_data")
#     cbw_fields: dict = request_payload.copy()
#     cbw_fields.pop("person_id")
#     bond_logger.info("adding cbw fields to person_data dict")
#     for key, value in cbw_fields.items():
#         person_data[key] = value
#         bond_logger.info(f"added {key} to person_data")


# def make_message(person_data: dict) -> dict:
#     """
#     Create params for the cbw payload.
#     "ssn" must be in "###-##-####" format
#     "createdDate" must be epoch time in milliseconds
#     "refId" is the only place we can use person_id, must not have dashes

#     dics are directly accessed if field is required by schema
#     otherwise use a .get()
#     """
#     person_id: UUID = person_data["person_id"]
#     bond_logger.info(f"Creating CBW params for Person Id {person_id}")
#     address: dict = person_data["addresses"][0]
#     dob: date = person_data["dob"]
#     message = {
#         "name": {
#             "type": "INDIVIDUAL",
#             "firstName": person_data["first_name"],
#             "lastName": person_data["last_name"],
#         },
#         "ssn": person_data["ssn"],
#         "currentAddress": {
#             "streetAddress1": address["street"],
#             "city": address["city"],
#             "region": address["state"],
#             "postalCode": address["zip_code"],
#             "country": address["country"],
#         },
#         "dob": {"day": dob.day, "month": dob.month, "year": dob.year},
#         "createdDate": int(time.time() * 1000),
#         "optInId": "2294682050",  # determined by Bond
#         "refId": str(person_id).replace("-", ""),
#     }
#     if person_data.get("middle_name"):
#         message["name"]["middleName"] = person_data["middle_name"]
#     if address.get("street2"):
#         message["currentAddress"]["streetAddress2"] = address["street2"]
#     if person_data.get("ip"):
#         message["ip"] = person_data["ip"]
#     if person_data.get("phone"):
#         message["phone"] = person_data["phone"]
#     if person_data.get("phone_country_code"):
#         message["phoneDialingCode"] = person_data["phone_country_code"]
#     if person_data.get("email"):
#         message["email"] = person_data["email"]
#     return message


# def make_pem(key: str) -> bytes:
#     """
#     This is hacky way to make the signature work.
#     Don't know how to make the SigningKey without starting with a PEM
#     """
#     return f"-----BEGIN EC PRIVATE KEY-----\n{key}\n-----END EC PRIVATE KEY-----\n".encode()


# def sign_message(message: dict) -> str:
#     """
#     Sign the message with ecdsa + sha256
#     """
#     sk1 = SigningKey.from_pem(make_pem(CBW_API_KEY))
#     sk2 = SigningKey.from_string(sk1.to_string(), curve=NIST256p)
#     signature = sk2.sign_deterministic(
#         json.dumps(message, separators=(",", ":")).encode(),
#         hashfunc=hashlib.sha256,
#         sigencode=sigencode_der,
#     )
#     signature = base64.b64encode(signature).decode("utf-8")
#     return signature


# def make_cbw_payload(person_data: dict) -> str:
#     """
#     1. Make message (object containing person info)
#     2. Create signature by signing the previously created message
#     3. Make and return cbw_payload using jsonrpc2.0 spec (as a json string)
#     """
#     person_id = person_data["person_id"]
#     bond_logger.info(f"Creating CBW payload for Person Id {person_id}")
#     message = make_message(person_data)
#     signature = sign_message(message)

#     params: dict = {}
#     params["api"] = {}

#     params["api"]["credential"] = CBW_CREDENTIAL
#     params["api"]["signature"] = signature
#     params["payload"] = message

#     cbw_payload = {"id": str(uuid.uuid4()), "method": "kyc.check", "params": params}
#     return json.dumps(cbw_payload, separators=(",", ":"))


# def validate_cbw_response(payload: dict) -> dict:
#     """
#     Validate cbw response is valid. If not, re-raise the marshmallow ValidationError as a CBWError
#     (seems to make more sense to present this as a CBWError than an Input error)
#     """
#     try:
#         bond_logger.info("Validating CBW Response")
#         schema = ValidCBWSchema()
#         cbw_response = PayloadValidation().payload_validation(payload, schema)
#         return cbw_response["result"]
#     except ValidationError as e:
#         bond_logger.error(f"CBW payload invalid. Reasons = {e.messages}")
#         raise CBWError("Invalid CBW Response Data", extra=e.messages)


# def ofac_passed(data: dict, settings: dict) -> str:
#     """
#     Execute ofac threshold checks
#     Each service will probably have it's own function for this kind of threshold check
#     """
#     if (
#         data["optionsEnabled"]["stringSimilarity"] * 100
#         < settings["ofac_similarity_threshold"]
#     ):
#         return "failed"
#     return "passed"


# def process_result(result: dict, config: dict) -> Tuple[str, dict]:
#     """
#     Using brand settings, determine if overall kyc has passed
#     If kyc fails, populate the "service results" dict with the pass/fail status of each
#     cbw validation service.
#     """
#     # other services haven't been tested yet
#     service_switch = {"ofac": ofac_passed}

#     if result["kycStatus"]["kycStatus"] != "SERVICE_GOOD":
#         raise CBWError("CBW service not available")
#     del result["kycStatus"]["kycStatus"]

#     service_results: dict = {}
#     kyc_status: str = "passed"
#     settings: dict = config["kyc_settings"]

#     for service_name, status in result["kycStatus"].items():

#         if status == "SERVICE_GOOD":
#             service = service_name.replace("Status", "")
#             service_result = service_switch[service](
#                 data=result[service], settings=settings
#             )
#             service_results[f"{service}_status"] = service_result

#             # if this isn't performant, consider using booleans/ints and
#             # serialize these to "pass/fail" with flask_restplus
#             if service_result != "passed":
#                 kyc_status = "failed"

#     return kyc_status, service_results
