from typing import Any

from app.schemas.common import PageData, SuccessResponse

def success(data: Any = None, message: str = "success"):
  return SuccessResponse(
      data=data,
      message=message
  )

def page_success(items, total, message: str = "success"):
  return SuccessResponse(
      data=PageData(
          data=items,
          total=total
      ),
      message=message
  )

def error(message: str = "error", code: int = 400, data: Any = None ):
  return {
    "code": code,
    "message": message,
    "data": data
  }

