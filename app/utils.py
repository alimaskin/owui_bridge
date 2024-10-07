# app/utils.py

import datetime
import decimal

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, datetime.datetime):
        if obj.tzinfo is None:
            # Предполагаем UTC, если нет информации о часовом поясе
            return obj.isoformat() + 'Z'
        else:
            # Конвертируем в UTC и добавляем 'Z'
            return obj.astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj
