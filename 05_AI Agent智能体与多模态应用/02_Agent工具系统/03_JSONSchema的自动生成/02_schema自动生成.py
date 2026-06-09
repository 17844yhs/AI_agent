from enum import Enum
from typing import Optional,List
import json

from pydantic import BaseModel,Field,field_validator

class Priority(str,Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGHT = 'hight'

class TaskCreate(BaseModel):
    title:str = Field(description='任务标题',min_length=1,max_length=200)
    description : Optional[str] = Field(default=None,description='任务描述',max_length=2000)
    priority : Priority=Field(description='优先级')
    tags:List[str]=Field(default_factory=list,description='标题列表',max_length=10)

    @field_validator('title')
    @classmethod  # ← 必须要有
    def title_not_empty(cls,v):
        if not v.strip():
            raise ValueError('标题不能为空')
        return v.strip()

schema = TaskCreate.model_json_schema()
# print(schema)

print(json.dumps(schema,indent=2,ensure_ascii=False))
# indent=2	让输出换行 + 缩进，方便人阅读调试