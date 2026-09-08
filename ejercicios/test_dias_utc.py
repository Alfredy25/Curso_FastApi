from datetime import datetime
from datetime import UTC
from zoneinfo import ZoneInfo

fecha_utc = datetime.now(UTC)
print("Fecha UTC: ",fecha_utc)
print(fecha_utc.tzinfo)

fecha_mexico = fecha_utc.astimezone(
    ZoneInfo("America/Mexico_City")
)

print("Fecha México", fecha_mexico)
print(fecha_mexico.tzinfo)