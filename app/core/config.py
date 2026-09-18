from __future__ import annotations

import os
from enum import Enum


class DataMode(str, Enum):
    LOCAL = "LOCAL"
    AWS = "AWS"


class Settings:
    @property
    def physica_data_mode(self) -> DataMode:
        mode = os.getenv("PHYSICA_DATA_MODE", "LOCAL").upper()
        if mode == "AWS":
            return DataMode.AWS
        return DataMode.LOCAL

    @property
    def aws_region(self) -> str | None:
        return os.getenv("AWS_REGION")

    @property
    def aws_iot_endpoint(self) -> str | None:
        return os.getenv("AWS_IOT_ENDPOINT")

    @property
    def aws_iot_thing_name(self) -> str | None:
        return os.getenv("AWS_IOT_THING_NAME")

    @property
    def aws_iot_topic_prefix(self) -> str:
        return os.getenv("AWS_IOT_TOPIC_PREFIX", "physica")

    @property
    def bedrock_model_id(self) -> str | None:
        return os.getenv("BEDROCK_MODEL_ID")


settings = Settings()
