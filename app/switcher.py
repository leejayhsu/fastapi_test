# # Modules from the Python Standard Library
# from collections import OrderedDict
# from datetime import date
# import json
# from typing import Callable, cast, Dict, Tuple, Union
# import datetime


# # Third Party modules from the public PyPI
# import requests

# # Internal modules from either Artifactory or the current project
# from app.models import CBWResultModel
# from app.schemas import CbwKycPostSchema, PersonaKycPostSchema
# from app.cbw import (
#     add_cbw_fields,
#     make_cbw_payload,
#     process_result,
#     validate_cbw_response,
# )
# from app.errors import CBWError
# from app.types import CbwResponseDict, PersonDict
# from baas_core.app import db
# from baas_core.core_config import INTERSERVICE_HOST
# from bond_logger import bond_logger

# CBW_URI = "https://connectors.cbwpayments.com/gateway/rpc"


# def do_cbw_kyc(
#     brand_id: str, person_data: dict, config: dict, **kwargs
# ) -> Tuple[dict, int]:
#     """
#     This handles the cbw flow. Only supports first time kyc. CBW doesn't allow re-run
#     1. Mall make_cbw_payload() util function --> returns a payload in jsonrpc2.0 format
#     2. Send the request to CBW
#     3. Call validate_cbw_response() util function to run marshmallow
#         (catches ValidationError and raises CBWError instead)
#     4. Call process_result() util function (judges if kyc passed based on brand configs)
#     5. If failed, include reasons
#     6. Return HTTP response
#     """
#     try:
#         request_payload: dict = kwargs["payload"]
#     except KeyError:
#         bond_logger.critical("payload was not passed to do_cbw_kyc()")
#         raise CBWError("error occured while initializing kyc")

#     add_cbw_fields(person_data, request_payload)
#     payload: str = make_cbw_payload(person_data)
#     r = requests.post(url=CBW_URI, data=payload)
#     cbw_response_json = r.json()

#     if r.status_code > 300:
#         raise CBWError("KYC provider could not be reached")

#     # if cbw response is good, validate the payload
#     result = validate_cbw_response(cbw_response_json)

#     # TODO: write something for when response is
#     # {'id': '872d9e6e-5ee2-4e99-b98b-fa63d2521b8a', 'error': {'errorDescription': 'Reference ID already exist', 'code': '32001', 'message': '1002:Reference ID already exist'}}
#     # or maybe check this immediately on the POST

#     kyc_status, kyc_results = process_result(result, config)

#     response: CbwResponseDict = {
#         "person_id": person_data["person_id"],
#         "kyc_status": kyc_status,
#     }
#     if kyc_status == "failed":
#         response["reasons"] = kyc_results

#     # Response should be added to the model.
#     cbw_data = result["cbw_data"]
#     cbw_data["person_id"] = person_data["person_id"]
#     cbw_data["brand_id"] = brand_id

#     new_cbw_result = CBWResultModel(**cbw_data)
#     db.session.add(new_cbw_result)
#     db.session.commit()
#     response["person_id"] = person_data["person_id"]
#     return marshal(response, kyc_programmatic_response_cbw, skip_none=True), 201


# def validate_payload(kyc_vendor: str, payload: dict) -> dict:
#     """
#     A utility method that has a switch to decide which marshmallow schema
#     to validate the incoming request body.
#     """
#     schema_switcher = {"cbw": CbwKycPostSchema}
#     schema = schema_switcher[kyc_vendor]()
#     return PayloadValidation().payload_validation(payload, schema)


# """
# A pythonic switch-case.
# Example usage: kyc_switcher["persona](brand_id, person_data)
# """
# kyc_switcher: Dict[str, Callable] = {"cbw": do_cbw_kyc}
