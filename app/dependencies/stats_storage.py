from collections import deque
from datetime import datetime, timedelta
from app.dependencies.url import UrlID
from app.metaclasses import SingletonMeta


class RoughStats:
    def __init__(self) -> None:
        self._count: int = 0
        self._clean_from_time: datetime = datetime.utcnow().replace(
            second=0, microsecond=0)
        self._data: list[int] = [0 for _ in range(24 * 60)]

    def inc(self) -> None:
        now = datetime.utcnow().replace(second=0, microsecond=0)
        self._delete_expired(now)
        self._count += 1
        self._data[self._calc_idx(time=now)] += 1

    def get(self) -> int:
        self._delete_expired(
            datetime.utcnow().replace(second=0, microsecond=0))
        return self._count

    def _delete_expired(self, now: datetime) -> None:
        while self._count != 0 and self._clean_from_time <= now:
            idx = self._calc_idx(self._clean_from_time)
            self._count -= self._data[idx]
            self._data[idx] = 0
            self._clean_from_time += timedelta(minutes=1)

        self._clean_from_time = now + timedelta(minutes=1)

    def _calc_idx(self, time: datetime) -> int:
        return time.hour * 60 + time.minute


class AccurateStats:
    def __init__(self) -> None:
        self._data: deque[datetime] = deque()

    def inc(self) -> None:
        now = datetime.utcnow()
        self._delete_expired(now)
        self._data.append(now)

    def get(self) -> int:
        self._delete_expired(datetime.utcnow())
        return len(self._data)

    def _delete_expired(self, now: datetime) -> None:
        end_of_window: datetime = now - timedelta(days=1)
        while len(self._data) != 0 and self._data[0] < end_of_window:
            self._data.popleft()


class StatsStorage(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._data_rough: dict[UrlID, RoughStats] = {}
        self._data_accurate: dict[UrlID, AccurateStats] = {}

    def inc(self, url_id: UrlID) -> None:
        self._data_rough.setdefault(url_id, RoughStats()).inc()
        self._data_accurate.setdefault(url_id, AccurateStats()).inc()

    def get_rough(self, url_id: UrlID) -> int:
        return self._data_rough.get(url_id, RoughStats()).get()

    def get_accurate(self, url_id: UrlID) -> int:
        return self._data_accurate.get(url_id, AccurateStats()).get()


async def get_stats_storage() -> StatsStorage:
    return StatsStorage()
