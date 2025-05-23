# import ngrok python sdk
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import time

from alphasignal.services.order_manager import OrderManager
from alphasignal.services.service import initialize_database  # Added import

load_dotenv()

if __name__ == "__main__":
    initialize_database()  # Initialize database to create necessary tables
    order_manager = OrderManager()

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"Starting order processing: {current_time}", flush=True)
            asyncio.run(order_manager.process_orders())
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if now.second % 30 == 0:
                print(f"Finished order processing: {current_time}", flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Closing processor")
