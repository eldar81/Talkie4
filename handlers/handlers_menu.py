import logging
import sqlite3

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards import letsgo_button, bio_is_correct, bio_gender, gender_of_companion
from loader import dp, db
from FMS import Ankena


@dp.callback_query_handler(text='menu')
async def what_to_change(call: CallbackQuery):
    await call.answer(cache_time=5)
    await call.message.answer(text="Ты в главном меню\n\n"
                                   "Чтобы воспользоваться функционалом бота напиши '/' или нажми на кнопку 'Меню'",
                              disable_notification = True)
    await call.message.edit_reply_markup()