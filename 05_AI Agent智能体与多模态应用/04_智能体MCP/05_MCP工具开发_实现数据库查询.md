# MCP 工具开发 - 实现数据库查询

## 准备环境

```bash
pip install pymysql fastmcp
```

---

## MCP 服务端 (server_chart.py)

```python
import pymysql
from fastmcp import FastMCP

mcp = FastMCP("mysql-server")

# MySQL 连接配置（按你自己的改）
DB_CONFIG = {
  "host": "localhost",
  "user": "root",
  "password": "123456",
  "database": "test",
  "charset": "utf8mb4"
}

def get_conn():
  return pymysql.connect(**DB_CONFIG)

@mcp.tool()
def query_user(min_age: int):
  """
   查询年龄 >= min_age 的用户
   """
  conn = get_conn()
  cursor = conn.cursor(pymysql.cursors.DictCursor)

  sql = "SELECT id, name, age FROM user WHERE age >= %s"
  cursor.execute(sql, (min_age,))
  rows = cursor.fetchall()

  cursor.close()
  conn.close()

  return rows

if __name__ == "__main__":
  mcp.run(
    transport="http",
    port=4001
  )
```

---

## MCP 客户端

```python
import asyncio
from fastmcp import Client

async def main():
  async with Client("http://localhost:4001/mcp") as client:
    tools = await client.list_tools()
    print("tools:", tools)

    result = await client.call_tool(
      "query_user",
      arguments={"min_age": 18}
    )
    print("result:", result)

asyncio.run(main())
```