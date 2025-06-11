# from datetime import datetime
# from typing import Optional
# from pydantic import BaseModel
# from enum import Enum


from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, validator
import json




class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    
    
    
class AuditAction(str, Enum):
    ISSUE = "issue"
    VERIFY = "verify"
    VERIFY_FAILED = "verify_failed"
    INVALIDATE = "invalidate"
    REVOKE = "revoke"
    
    
    
class TokenAuditCreate(BaseModel):
    user_id: str
    token_type: str
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error: Optional[str] = None
    token_jti: Optional[str] = None
    
    
    
    # @validator('additional_data', pre=True)
    # def parse_additional_data(cls, v):
    #     if isinstance(v, str):
    #         try:
    #             return json.loads(v)
    #         except json.JSONDecodeError:
    #             return None
    #     return v
    
    
 

# class TokenAuditCreate(TokenAuditCreate):
#     def to_db_dict(self):
#         data = self.dict()
#         if data['additional_data'] is not None:
#             data['additional_data'] = json.dumps(data['additional_data'])
#         return data


class TokenAudit(TokenAuditCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }