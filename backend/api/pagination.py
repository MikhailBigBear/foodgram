"""Модуль настраивает пагинацию для API."""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Пагинатор с фиксированным размером страницы.

    Поддерживает limit параметр.

    Атрибуты:
    - page_size: количество элементов по умолчанию.
    - page_size_query_param: имя параметра для указания размера страницы.
    - max_page_size: максимальное количество элементов на странице.
    """

    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 100
