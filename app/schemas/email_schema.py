from pydantic import BaseModel

class EmailRequest(BaseModel):
    email: str

class EmailResponse(BaseModel):
    email: str
    status: str
    
class EmailValidationReport(BaseModel):
    email: str
    status: str
    score: int
    syntax: bool
    domain: bool
    domain_active: bool
    freemail: bool
    role_based: bool
    alias_forward: bool
    blacklisted: bool
    spf: bool
    dkim: bool
    dmarc: bool
    catchall: bool | None = None
    smtp: bool | None = None
    greylist_retry: bool | None = None
