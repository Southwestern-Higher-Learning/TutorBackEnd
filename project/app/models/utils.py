from typing import List, Optional, Type

from fastapi import Query, Request
from pydantic import BaseModel
from tortoise import models, queryset


class PaginateModel:
    def __init__(self, model: Type[models.Model], py_model: "Type[BaseModel]"):
        self.model = model
        self.py_model = py_model

    # Called on Depends(...)
    def __call__(
        self,
        request: Request,
        _sort: str = "id",
        _order: str = "asc",
        _start: int = 0,
        _end: int = 20,
        id: Optional[List[int]] = Query(None),
    ) -> queryset.QuerySet[models.Model]:
        filters = self.py_model.parse_obj(request.query_params)
        filters_dict = filters.dict(exclude_unset=True)
        if id is not None:
            filters_dict["id__in"] = id
        order = _sort
        if _order.lower() == "desc":
            order = "-" + order
        return (
            self.model.filter(**filters_dict)
            .order_by(order)
            .offset(_start)
            .limit(_end - _start)
            .distinct()
        )
