from uuid import uuid4


def person_response(person_id: str) -> dict:
    return {
        "person_id": person_id,
        "bond_brand_id": "f727ec42-e916-4cef-895b-266b950d8170",
        "first_name": "Test",
        "middle_name": "danger",
        "last_name": "User",
        "dob": "2000-12-01",
        "addresses": [
            {
                "address_id": str(uuid4()),
                "address_type": "residential",
                "street": "123 Main St.",
                "street2": "Suit 600",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "12345-1234",
                "country": "US",
            }
        ],
    }
