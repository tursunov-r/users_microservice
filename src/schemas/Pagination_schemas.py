from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(5, ge=0, le=100, description="Count items per page")
    offset: int = Field(0, ge=0, description="Offset from current page")
