import pandas as pd
from datetime import datetime
from telebot.types import Message 
import os

new_record = pd.DataFrame([{
    'tg_nick': [],
    'motion': [],
    'api': [],
    'date': [],
    'time': [],
    'api_answer': []
}])
new_record = new_record.drop(index=0)
def log_call(func):
    def wrap(message: Message, *args, **kwargs):
        return_list = func(message, *args, **kwargs) or ["NONE", "NONE", "NONE"]
        tg_nick = message.from_user.username or "No_name"
        date = datetime.now().date()
        time = datetime.now().time().strftime('%H:%M:%S')
        motion = return_list[0] if len(return_list) > 0 else "NONE"
        try:
            api = return_list[1] if len(return_list) > 1 else "NONE"
            api_answer = str(return_list[2]) if len(return_list) > 2 else "NONE"
        except (IndexError, TypeError):
            api = "NONE"
            api_answer = "NONE"
        new_record.loc[len(new_record.index)] = [tg_nick, motion, api, date, time, api_answer]
        new_record.to_csv('logs.csv', index=True, index_label='id')
        return return_list
    return wrap