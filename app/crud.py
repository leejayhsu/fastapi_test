from sqlalchemy.orm import Session

from app.models import BrandModel
from app.schemas import Brand


def get_brand(db: Session, brand_id: str) -> BrandModel:
    """
    retrieves a brand from the brand table
    """
    return db.query(BrandModel).filter(BrandModel.brand_id == brand_id).first()


def create_brand(db: Session, brand_id: str, kyc_vendor: str) -> BrandModel:
    """
    creates a brand in the brand table
    """
    new_brand = BrandModel(brand_id=brand_id, kyc_vendor=kyc_vendor)
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand


def get_kyc_config(brand_id: str, kyc_vendor: str) -> dict:
    return {
        "validation": "default",
        "ofac_similarity_threshold": 75,
        "ip_risk_threshold": 75,
        "mobile_first_name_threshold": 75,
        "mobile_last_name_threshold": 75,
        "mobile_address_threshold": 75,
        "email_risk_threshold": 500,
        "email_domain_risk_threshold": 3,
    }