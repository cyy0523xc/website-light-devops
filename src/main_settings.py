
from typing import List
from pydantic import BaseModel, Field


class ReleaseResp(BaseModel):
    """版本发布返回值"""
    msg: str = Field('', title='发布信息', description='发布信息')


class RollbackResp(BaseModel):
    """版本回滚返回值"""
    msg: str = Field('', title='回滚信息', description='回滚信息')