"""Build a small synthetic Apple Health-shaped export.xml entirely in memory."""
from datetime import datetime, timedelta
from io import BytesIO
from xml.etree.ElementTree import Element, ElementTree, SubElement

import numpy as np

from src.generator import generate

DEFAULT_SEED = 17
DAYS = 35


def build_synthetic_export(seed: int = DEFAULT_SEED) -> bytes:
    """Return export.xml bytes for one generated synthetic patient (no real person's data)."""
    root = Element("HealthData", {"locale": "en_US"})
    patient = generate(seed, patients=1, cycles=1)[0]
    for day in range(DAYS):
        date = str(patient["period_start"] + np.timedelta64(day, "D"))
        records = [
            ("HKQuantityTypeIdentifierAppleSleepingWristTemperature", "degC", 36.4 + float(patient["temperature"][day])),
            ("HKQuantityTypeIdentifierRestingHeartRate", "count/min", 62 + float(patient["rhr"][day])),
            ("HKQuantityTypeIdentifierHeartRateVariabilitySDNN", "ms", 48 + float(patient["hrv"][day]) * 4),
            ("HKQuantityTypeIdentifierStepCount", "count", float(patient["steps"][day])),
        ]
        for typ, unit, value in records:
            SubElement(root, "Record", {"type": typ, "unit": unit, "value": f"{value:.3f}",
                                        "startDate": date + " 23:00:00 +0530", "endDate": date + " 23:59:00 +0530"})
        sleep_start = datetime.strptime(date + " 22:30:00 +0530", "%Y-%m-%d %H:%M:%S %z")
        for stage, hours in (("Core", 3.4), ("Deep", 1.1), ("REM", 1.5), ("Awake", .4)):
            sleep_end = sleep_start + timedelta(hours=hours)
            SubElement(root, "Record", {"type": "HKCategoryTypeIdentifierSleepAnalysis",
                                        "value": "HKCategoryValueSleepAnalysis" + ("Awake" if stage == "Awake" else "Asleep" + stage),
                                        "startDate": sleep_start.strftime("%Y-%m-%d %H:%M:%S %z"),
                                        "endDate": sleep_end.strftime("%Y-%m-%d %H:%M:%S %z")})
            sleep_start = sleep_end
        if day == 0:
            record = SubElement(root, "Record", {"type": "HKCategoryTypeIdentifierMenstrualFlow", "value": "2",
                                                 "startDate": date + " 08:00:00 +0530", "endDate": date + " 08:01:00 +0530"})
            SubElement(record, "MetadataEntry", {"key": "HKMetadataKeyMenstrualCycleStart", "value": "true"})
    buffer = BytesIO()
    ElementTree(root).write(buffer, encoding="utf-8", xml_declaration=True)
    return buffer.getvalue()
