from datetime import datetime, timedelta
from pydantic import BaseModel

class VoData(BaseModel):
    vo_mp4_link: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    vo_mp3_link: str | None = None
    vo_title: str = "-"
    author: str = "-"
    contributors: str = "-"
    series_title: str = "-"
    duration: timedelta = timedelta(seconds=0)
    recorded_on: datetime = datetime.now()
