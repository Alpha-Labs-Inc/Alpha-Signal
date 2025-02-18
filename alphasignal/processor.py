# import ngrok python sdk
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import time

from alphasignal.services.order_manager import OrderManager

load_dotenv()

if __name__ == "__main__":
    order_manager = OrderManager()

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"Starting order processing: {current_time}")
            asyncio.run(order_manager.process_orders())

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"Finished order processing: {current_time}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing processor")
