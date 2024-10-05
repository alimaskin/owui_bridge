import lotus

# Устанавливаем API-ключ
lotus.api_key = 'NesKnxXp.qNQR8DE6IxmnTh6LeA69yKkuE4umzCZp'
lotus.host = 'http://127.0.0.1'
# Включаем отладочный режим, если необходимо
lotus.debug = True

# Отправляем одно событие
try:
    response = lotus.track_event(
        customer_id='customer123',
        event_name='api_call',
        properties={
            'region': 'US',
            'mb_used': 150
        },
        idempotency_id='c9799bf9-e5c9-4007-8d10-0663d045d23c',
        time_created="2024-10-01T21:58:14.193Z"
    )
    print("Event sent successfully:", response)
except Exception as e:
    print("Error sending event:", e)
