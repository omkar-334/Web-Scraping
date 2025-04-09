from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel


class LocatorType(str, Enum):
    ROLE = "get_by_role"  # name
    TEXT = "get_by_text"
    LABEL = "get_by_label"
    PLACEHOLDER = "get_by_placeholder"
    CSS = "locator"
    XPATH = "locator"


class FilterType(str, Enum):
    TEXT = "has_text"
    NOT_TEXT = "has_not_text"
    CHILD = "has"
    NOT_CHILD = "has_not"
    VISIBLE = "visible"  # bool


class FilterModel(BaseModel):
    filter_type: FilterType
    value: Optional[Union[str, bool]] = None


class LocatorModel(BaseModel):
    type: LocatorType
    value: Union[str, int, float]
    filters: Optional[list[FilterModel]] = None
    exact: Optional[bool] = False
    role_name: Optional[str] = None


def get_element(page, locator: LocatorModel):
    method = getattr(page, locator.type)

    kwargs = {}

    if locator.type == LocatorType.ROLE:
        kwargs["name"] = locator.role_name
    if locator.exact:
        kwargs["exact"] = locator.exact

    func = method(locator.value, **kwargs)

    if locator.filters:
        filter_kwargs = {}

        for filter in locator.filters:
            if filter.filter_type == FilterType.VISIBLE:
                filter_kwargs[filter.filter_type.value] = True  # No argument needed
            elif filter.value is not None:
                filter_kwargs[filter.filter_type.value] = filter.value

        func = func.filter(**filter_kwargs)

    return func
