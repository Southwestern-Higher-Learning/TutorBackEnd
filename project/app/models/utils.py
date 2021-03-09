from typing import Type

from fastapi import Request
from pydantic import BaseModel
from tortoise import models, queryset


class PaginateModel:
    def __init__(self, model: Type[models.Model], py_model: "Type[BaseModel]"):
        self.model = model
        self.py_model = py_model

    # Called on Depends(...)
    def __call__(
        self, request: Request, _sort: str, _order: str, _start: int = 0, _end: int = 20
    ) -> queryset.QuerySet[models.Model]:
        filters = self.py_model.parse_obj(request.query_params)
        order = _sort
        if _order.lower() == "desc":
            order = "-" + order
        return (
            self.model.filter(**filters.dict(exclude_unset=True))
            .order_by(order)
            .offset(_start)
            .limit(_end - _start)
        )
