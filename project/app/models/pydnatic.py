from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class SwapCodeIn(BaseModel):
    code: str
    redirect_uri: AnyHttpUrl


class NormalUserUpdate(BaseModel):
    description: Optional[str]
    is_tutor: Optional[bool]
