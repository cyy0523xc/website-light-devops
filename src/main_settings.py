from typing import List
from pydantic import BaseModel, Field


class BaseResp(BaseModel):
    status: bool = Field(..., title='操作是否成功', description='操作是否成功')
    msg: str = Field('', title='异常信息', description='异常信息')


class ActionResp(BaseModel):
    status: bool = Field(..., title='操作是否成功', description='操作是否成功')
    msg: str = Field('', title='操作信息', description='操作信息')
