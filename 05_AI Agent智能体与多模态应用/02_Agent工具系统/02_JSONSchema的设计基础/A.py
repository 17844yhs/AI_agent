# 数据库查询函数的Schema设计
database_query_schema = {
  "name": "query_database",
  "description": "执行数据库查询操作",
  "parameters": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "description": "要查询的表名",
        "enum": ["users", "products", "orders"]
       },
      "columns": {
        "type": "array",
        "description": "要查询的列名列表",
        "items": {"type": "string"},
        "minItems": 1
       },
      "conditions": {
        "type": "object",
        "description": "查询条件",
        "properties": {
          "column": {"type": "string"},
          "operator": {
            "type": "string",
            "enum": ["=", ">", "<", ">=", "<=", "LIKE", "IN"]
           },
          "value": {
            "oneOf": [
               {"type": "string"},
               {"type": "number"},
               {"type": "boolean"}
             ]
           }
         }
       },
      "limit": {
        "type": "integer",
        "description": "查询结果限制数量",
        "minimum": 1,
        "maximum": 1000,
        "default": 100
       }
     },
    "required": ["table", "columns"]
   }
}
​
# 文件处理函数的Schema设计
file_operation_schema = {
  "name": "file_operation",
  "description": "执行文件操作",
  "parameters": {
    "type": "object",
    "properties": {
      "operation": {
        "type": "string",
        "enum": ["read", "write", "delete", "move"],
        "description": "文件操作类型"
       },
      "file_path": {
        "type": "string",
        "description": "文件路径",
        "pattern": "^(/[^/]+)+$"
       },
      "content": {
        "type": "string",
        "description": "写入的文件内容（write操作时必需）"
       },
      "encoding": {
        "type": "string",
        "enum": ["utf-8", "ascii", "latin-1"],
        "default": "utf-8",
        "description": "文件编码"
       }
     },
    "required": ["operation", "file_path"],
    "allOf": [
       {
        "if": {"properties": {"operation": {"const": "write"}}},
        "then": {"required": ["content"]}
       }
     ]
   }
}
