class PSETransactionCreate(BaseModel):
    customer_id: int
    account_id: int
    amount: float
    currency: str = "COP"
    return_url_success: Optional[str] = None
    return_url_failure: Optional[str] = None
    metadata: Optional[dict] = None

class PSETransactionOut(BaseModel):
    id: int
    internal_order_id: str
    customer_id: int
    account_id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_tx_id: Optional[str] = None
    provider_reference: Optional[str] = None
    payment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True  

class PSECallbackIn(BaseModel):
    internal_order_id: str
    status: str                    
    provider_tx_id: Optional[str] = None
    provider_reference: Optional[str] = None
    raw_payload: Optional[dict] = None

class PSETransferCreate(BaseModel):
    source_account_id: int
    destination_bank: str
    destination_account: str
    amount: float
    description: str | None = None


class PSETransferResponse(BaseModel):
    id: int
    source_account_id: int
    destination_bank: str
    destination_account: str
    amount: float
    description: str | None
    status: str
    created_at: str

    class Config:
        from_attributes = True