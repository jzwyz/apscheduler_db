from datetime import date, timedelta, datetime, timezone
import calendar
from zoneinfo import ZoneInfo

# 数字 -> 月份全称
MONTHS_FULL = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

def get_date_ranges(target_date):
    year = target_date.year
    month = target_date.month
    quarter = (month - 1) // 3 + 1

    # **年范围**
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    year_days = (year_end - year_start).days + 1

    # **找到该年的第一个周日**
    first_sunday = year_start + timedelta(days=(6 - year_start.weekday() + 1) % 7)
    if first_sunday.year != year:  
        first_sunday += timedelta(days=7)  # 确保在今年

    last_saturday = year_end - timedelta(days=(year_end.weekday() + 1) % 7)
    total_weeks = ((last_saturday - first_sunday).days + 1) // 7

    # **季度范围**
    quarter_start_month = {1: 1, 2: 4, 3: 7, 4: 10}
    quarter_end_month = {1: 3, 2: 6, 3: 9, 4: 12}
    quarter_start = date(year, quarter_start_month[quarter], 1)
    quarter_end = date(year, quarter_end_month[quarter], calendar.monthrange(year, quarter_end_month[quarter])[1])
    quarter_days = (quarter_end - quarter_start).days + 1

    # **月范围**
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    month_days = (month_end - month_start).days + 1

    # **周范围（周日为第一天）**
    weekday = target_date.weekday()  # 0=Monday, 6=Sunday
    week_start = target_date - timedelta(days=(weekday + 1) % 7)
    week_end = week_start + timedelta(days=6)
    week_days = 7

    # **确定 week_number 和 所属年份**
    if week_start < first_sunday:
        week_year = year - 1
        prev_year_last_sunday = first_sunday - timedelta(days=7)
        week_number = ((week_start - prev_year_last_sunday).days // 7) + 1
    else:
        week_year = year
        week_number = ((week_start - first_sunday).days // 7) + 1

    return {
        "year": {
            "start": year_start, "end": year_end, "days": year_days, "total_weeks": total_weeks
        },
        "quarter": {
            "start": quarter_start, "end": quarter_end, "days": quarter_days, "year": 0, "quarter": 0, "month": 0, "week": 0, "day": target_date
        },
        "month": {
            "start": month_start, "end": month_end, "days": month_days
        },
        "week": {
            "start": week_start, "end": week_end, "days": week_days,
            "week_number": f"{week_year}W{week_number}"
        }
    }

def last_year(year: int = 0):
    target_date = date - timedelta(days=365*year)
    date_range = get_date_ranges(target_date)
    return date_range['year']

def last_quarter(quarter: int = 0):
    target_date = date - timedelta(days=90*quarter)
    date_range = get_date_ranges(target_date)
    return date_range['quarter']

def last_month(month: int = 0):
    target_date = date - timedelta(days=30*month)
    date_range = get_date_ranges(target_date)
    return date_range['month']

def last_week(week: int = 0):
    target_date = date - timedelta(weeks=week)
    date_range = get_date_ranges(target_date)
    return date_range['week']

def timestamp_to_date(ts: int):
    ts_date = date.fromtimestamp(ts / 1000)
    return ts_date

def get_days_range(last_day: int = 0, days: int = 0):
    '''
    获取日期范围

    last_day: 往前推N天
    days: 抓取N天数据
    '''
    end_date = date.today() - timedelta(days=last_day)
    start_date = end_date - timedelta(days=days)
    return [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]

def get_datetime_tz(tz: str = 'UTC'):
    return datetime.now(tz=ZoneInfo(tz))