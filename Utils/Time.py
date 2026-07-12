from datetime import datetime, timezone, timedelta

def format_time(dt):
    if dt is None:
        return "Not scheduled"
    return dt.strftime("%Y-%m-%d %I:%M %p")

def humanize_time(dt):
    if dt is None:
        return "Not scheduled"

    now = datetime.now(timezone.utc)
    diff = dt - now

    seconds = int(diff.total_seconds())

    if seconds <= 0:
        return "now"

    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    return "in " + " ".join(parts)

def pretty_time(dt):
    if dt is None:
        return "Not scheduled"

    absolute = dt.strftime("%I:%M %p on %b %d")
    relative = humanize_time(dt)

    return f"{relative} ({absolute})"

def discord_time(dt):
    if dt is None:
        return "Not scheduled"
    
    ts = int(dt.timestamp())
    return f"<t:{ts}:R> (<t:{ts}:F>)"

def round_nearest_hour(time: datetime) -> datetime:
    return (time.replace(second=0, microsecond=0, minute=0, hour=time.hour) + timedelta(hours=time.minute//30))