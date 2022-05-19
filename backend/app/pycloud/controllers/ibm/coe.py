from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class TermsConditions(BaseModel):
    required: bool
    accepted: bool
    timestamp: datetime


class OrganizationRegion(BaseModel):
    guid: str
    region: str


class Linkage(BaseModel):
    origin: str
    state: str


class PaymentMethod(BaseModel):
    type: str
    started: datetime
    ended: datetime
    currencyCode: str
    anniversaryDay: int


class SubscriptionHistory(BaseModel):
    type: str
    state: str
    startTime: datetime
    endTime: Optional[datetime]
    currencyCode: str
    countryCode: str
    billingCountryCode: str
    billingSystem: str

    # Bluemix returns an empty string if not present, convert to None
    @validator('endTime', pre=True)
    def end_time_default(cls, v):
        if v == "":
            return None


class Subscription(BaseModel):
    type: str
    state: str
    payment_method: PaymentMethod
    subscription_id: str
    part_number: str
    subscriptionTags: List[str]
    payg_pending_timestamp: datetime
    history: List[SubscriptionHistory]
    current_state_timestamp: datetime
    softlayer_account_id: str
    billing_system: str


class COEDescription(BaseModel):
    name: str
    type: str
    state: str
    owner: str
    owner_userid: str
    owner_unique_id: str
    owner_iam_id: str
    customer_id: str
    country_code: str
    currency_code: str
    billing_country_code: str
    isIBMer: bool
    terms_and_conditions: TermsConditions
    tags: List[str]
    organizations_region: List[OrganizationRegion]
    linkages: List[Linkage]
    bluemix_subscriptions: List[Subscription]
    subscription_id: str
    configuration_id: str
    onboarded: int
    offer_template: str
    origin: str
    boundary: str
    pending_boundary: str
