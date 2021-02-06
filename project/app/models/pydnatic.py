from pydantic import AnyHttpUrl, BaseModel


class SwapCodeIn(BaseModel):
    code: str
    redirect_uri: AnyHttpUrl
