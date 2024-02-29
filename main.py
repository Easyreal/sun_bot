from main.app import bot
from main.database.orm_model import db_start
import time

if __name__ == "__main__":
    db_start()
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue