"""Модуль содержит пользовательские поля сериализаторов для API."""

import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображений в формате base64."""

    def to_internal_value(self, data):
        """
        Преобразует входное значение во внутреннее представление.

        Данная функция принимает на вход либо строку в формате base64,
        либо файловый объект и преобразует его во внутреннее представление
        приложения для дальнейшей обработки.
        """
        if data is None or (isinstance(data, str) and not data.strip()):
            return None

        if isinstance(data, str) and data.startswith("data:image"):
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                decoded_file = base64.b64decode(imgstr)
                filename = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(decoded_file, name=filename)
            except Exception:
                raise serializers.ValidationError(
                    "Неверный формат изображения."
                )
        return super().to_internal_value(data)
