# test_batch_send.py
import asyncio
from app.sender import LotusClient

async def send_batch():
    lotus_client = LotusClient()
    events = [
        {
            'user_id': 'customer123',
            'event_name': 'api_call',
            'properties': {
                'region': 'US',
                'mb_used': 150
            },
            'observe_id': 'c9799bf9-e5c9-4007-8d10-0663d045d23c',
            'created_at': "2024-10-01T21:58:14.193Z"
        },
        {
            'user_id': 'customer124',
            'event_name': 'api_call',
            'properties': {  # Обязательно присутствует
                'region': 'EU',
                'mb_used': 200
            },
            'observe_id': 'd9799bf9-e5c9-4007-8d10-0663d045d24d',
            'created_at': "2024-10-01T22:00:00.000Z"
        },
        # Добавьте больше событий по необходимости
    ]
    try:
        await lotus_client.track_events_batch(events)
        print("Batch events sent successfully.")
    except Exception as e:
        print(f"Error sending batch events: {e}")
    finally:
        await lotus_client.close()

if __name__ == "__main__":
    asyncio.run(send_batch())
