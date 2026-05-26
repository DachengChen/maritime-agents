from dataclasses import dataclass

from app.models.scheduled_task import ScheduleType

WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


@dataclass
class ParsedSchedule:
    schedule_type: str
    schedule_time: str
    schedule_day_of_week: int | None


def parse_schedule(raw_schedule: str) -> ParsedSchedule:
    parts = raw_schedule.strip().split()
    if len(parts) < 2:
        raise ValueError("Schedule format must be 'daily HH:MM' or 'weekly Monday HH:MM'")

    frequency = parts[0].lower()
    if frequency == ScheduleType.DAILY.value and len(parts) == 2:
        return ParsedSchedule(schedule_type=frequency, schedule_time=parts[1], schedule_day_of_week=None)

    if frequency == ScheduleType.WEEKLY.value and len(parts) == 3:
        day = parts[1].lower()
        if day not in WEEKDAY_INDEX:
            raise ValueError("Invalid weekday in weekly schedule")
        return ParsedSchedule(schedule_type=frequency, schedule_time=parts[2], schedule_day_of_week=WEEKDAY_INDEX[day])

    raise ValueError("Schedule format must be 'daily HH:MM' or 'weekly Monday HH:MM'")
