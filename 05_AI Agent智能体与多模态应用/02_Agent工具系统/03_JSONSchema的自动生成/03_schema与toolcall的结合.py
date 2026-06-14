from pydantic import BaseModel, Field
from typing import List, Optional

class DatabaseQuery(BaseModel):
    table: str = Field(description="要查询的表名", json_schema_extra=["users", "products", "orders"])
    columns: List[str] = Field(description="要查询的列名列表", min_length=1)
    where_clause: Optional[str] = Field(default=None, description="WHERE条件")
    limit: int = Field(default=100, description="返回记录数量", ge=1, le=1000)
    order_by: Optional[str] = Field(default=None, description="排序字段")

def query_database(params: DatabaseQuery) -> dict:
    """执行数据库查询"""
    # 实现查询逻辑
    return {"status": "success", "data": []}

# 自动生成工具定义
def create_tool_definition(func, param_model):
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or f"Execute {func.__name__}",
            "parameters": param_model.model_json_schema()
        }
    }


# 使用示例
tools = [create_tool_definition(query_database, DatabaseQuery)]