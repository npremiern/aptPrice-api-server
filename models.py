from pydantic import BaseModel
from decimal import Decimal
from typing import Annotated, Any, Dict

# Decimal 값을 일반 숫자 형식으로 직렬화하는 커스텀 타입
def serialize_decimal(v: Decimal) -> str:
    return str(v)


class ServiceData(BaseModel):
    도로명주소: str
    시도: str
    시군구: str
    읍면: str
    동리: str
    특수지코드: str
    본번: str
    부번: str
    특수지명: str
    단지명: str
    동명: str
    호명: str
    전용면적: str
    공시가격: str
    단지코드: str
    동코드: str
    호코드: str


