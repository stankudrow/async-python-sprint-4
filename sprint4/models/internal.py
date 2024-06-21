from datetime import datetime

import pydantic


START_TIME: datetime = datetime.now()


class BaseStatistics(pydantic.BaseModel):
    started_at: datetime
    current_time: datetime = pydantic.Field(default_factory=datetime.now)


class ServiceStatistics(BaseStatistics):
    started_at: datetime = START_TIME
