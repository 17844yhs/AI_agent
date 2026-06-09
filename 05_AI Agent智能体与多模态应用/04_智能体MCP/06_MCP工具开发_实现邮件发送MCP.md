## 编写 MCP Server

```python
from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.header import Header

mcp = FastMCP("email-mcp")
```

## 定义一个 MCP Tool

```python
from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.header import Header

mcp = FastMCP("email-mcp")


@mcp.tool()
def send_email(
  to: str,
  subject: str,
  content: str
) -> str:
  """
   发送一封邮件

   参数:
   - to: 收件人邮箱
   - subject: 邮件标题
   - content: 邮件正文
   """

  smtp_server = "smtp.qq.com"
  smtp_port = 465
  sender = "877910962@qq.com"
  password = "YOUR_PASSWORD" # ⚠️不是邮箱登录密码

  msg = MIMEText(content, "plain", "utf-8")
  msg["From"] = sender
  msg["To"] = to
  msg["Subject"] = Header(subject, "utf-8")

  try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
      server.login(sender, password)
      server.sendmail(sender, [to], msg.as_string())
    return "邮件发送成功"
  except Exception as e:
    return f"邮件发送失败: {e}"

if __name__ == "__main__":
  mcp.run(transport="http", port=4001)
```

## 客户端调用

```python
"""
client 的 Docstring
1、创建MCP客户端
2、链接MCP server
3、查询有哪些工具
4、调用工具
"""
import asyncio
from fastmcp import Client

async def main():
  async with Client("http://localhost:4001/mcp") as client:
    tools = await client.list_tools()
    print(tools)

    result = await client.call_tool(
      "send_email",
      arguments={
        "to": "18587781058@163.com",
        "subject": "MCP 测试邮件",
        "content": "这是一封通过 FastMCP 发送的邮件"
       }
     )
    print(result)

asyncio.run(main())
```