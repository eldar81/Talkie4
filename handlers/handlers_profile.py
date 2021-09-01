import logging
import sqlite3
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils import callback_data

from keyboards import profile_menu, change_profile, profile_submenu, bio_gender, gender_of_companion
from loader import dp, db


@dp.message_handler(Command("profile"))
async def check_profile(message: Message):
    try:
        user = db.select_user(id=message.from_user.id)
        gender = "Мужской"
        req = "Нет"
        if user[3] == 0:
            gender = "Женский"
        if user[6] == 1:
            req = "Только мужского пола"
        elif user[6] == 0:
            req = "Только женского пола"
        await message.answer(text=f"Ваш профиль в Talkie:\n\n"
                                  f"<b>Имя:</b> {user[2]}\n"
                                  f"<b>Пол:</b> {gender}\n"
                                  f"<b>Возраст:</b> {user[4]}\n"
                                  f"<b>Интересы:</b> {user[5]}\n"
                                  f"<b>Пожелание к собеседнику:</b> {req}\n",
                             reply_markup=profile_menu,
                             disable_notification=True
                             )
    except:
        await message.answer("У тебя еще нет профиля\n\n"
                             "Напиши /start, чтобы начать 😉")


@dp.callback_query_handler(text="back_to_profile")
async def check_profile(call: CallbackQuery):
    user = db.select_user(id=call.from_user.id)
    gender = "Мужской"
    req = "Нет"
    if user[3] == 0:
        gender = "Женский"
    if user[6] == 1:
        req = "Только мужского пола"
    elif user[6] == 0:
        req = "Только женского пола"
    await call.message.answer(text=f"Твой профиль в Talkie:\n\n"
                              f"<b>Имя:</b> {user[2]}\n"
                              f"<b>Пол:</b> {gender}\n"
                              f"<b>Возраст:</b> {user[4]}\n"
                              f"<b>Интересы:</b> {user[5]}\n"
                              f"<b>Пожелание к собеседнику:</b> {req}\n",
                         reply_markup=profile_menu,
                         disable_notification=True
                         )
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text='change_my_profile')
async def what_to_change(call: CallbackQuery):
    await call.answer(cache_time=5)
    await call.message.answer(text="Что именно ты хочешь изменить?",
                              reply_markup=change_profile,
                              disable_notification=True)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text='change_profile_name')
async def change_name(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await call.message.answer(text="Введи имя",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state("change_profile_name")


@dp.message_handler(state="change_profile_name")
async def changed_name(message: Message, state: FSMContext):
    answer = message.text
    db.update_user_name(id=message.from_user.id,
                        Bio_name=answer)
    await message.answer(text=f"Имя изменено на: <b>{answer}</b>",
                         reply_markup=profile_submenu)
    await state.finish()


@dp.callback_query_handler(text='change_profile_age')
async def change_age(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await call.message.answer(text="Введи свой возраст",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state("change_profile_age")


@dp.message_handler(state="change_profile_age")
async def changed_age(message: Message, state: FSMContext):
    answer = message.text
    if re.match(r'[1-9]{1}[0-9]{1}', answer) and len(answer) == 2:
        db.update_user_age(id=message.from_user.id,
                       Bio_age=int(answer))
        await message.answer(text=f"Возраст изменен на: <b>{answer}</b>",
                         reply_markup=profile_submenu)
        await state.finish()
    else:
        await message.answer(text="❔Напиши свой возраст цифрами. Например:\n\n"
                                  "<i>22</i>",
                             disable_notification=True)
        await state.set_state("change_profile_age")


@dp.callback_query_handler(text='change_profile_hobby')
async def change_hobby(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await call.message.answer(text="Какие у тебя хобби? Перечисли интересы через запятую. Например:\n\n"
                                   "<i>Фортепиано, шахматы, картины по номерам</i>",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state("change_profile_hobby")


@dp.message_handler(state="change_profile_hobby")
async def changed_hobby(message: Message, state: FSMContext):
    answer = message.text
    db.update_user_hobby(id=message.from_user.id,
                         Bio_hobby=answer)
    await message.answer(text=f"Интересы изменены на: <b>{answer}</b>",
                         reply_markup=profile_submenu)
    await state.finish()


@dp.callback_query_handler(text='change_profile_gender')
async def change_gender(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await call.message.answer(text="Твой пол?",
                              reply_markup=bio_gender,
                              disable_notification=True
                              )
    await call.message.edit_reply_markup()
    await state.set_state("change_profile_gender")


@dp.callback_query_handler(state="change_profile_gender")
async def changed_gender(call: CallbackQuery, state: FSMContext):
    callback_data = call.data
    if callback_data == "male":
        answer = "Мужской"
        answer_to_db = 1
    elif callback_data == "female":
        answer = "Женский"
        answer_to_db = 0
    db.update_user_gender(id=call.from_user.id,
                          Bio_gender=answer_to_db)
    await call.message.answer(text=f"Пол изменен на: <b>{answer}</b>",
                              reply_markup=profile_submenu)
    await call.message.edit_reply_markup()
    await state.finish()


@dp.callback_query_handler(text='change_profile_compreq')
async def change_compreq(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    await call.message.answer("Скажи, какого пола нам найти для тебя собеседника?",
                              reply_markup=gender_of_companion,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.set_state("change_profile_compreq")


@dp.callback_query_handler(state="change_profile_compreq")
async def changed_compreq(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    callback_data = call.data
    answer = "Нет"
    answer_to_db = 2
    if callback_data == "gender_of_companion_male":
        answer = "Только мужского пола"
        answer_to_db = 1
    elif callback_data == "gender_of_companion_female":
        answer = "Только женского пола"
        answer_to_db = 0
    db.update_user_compreq(id=call.from_user.id,
                           Bio_companion_requirements=answer_to_db)
    await call.message.answer(text=f"Ваши пожелания к собеседнику: <b>{answer}</b>",
                              reply_markup=profile_submenu)
    await call.message.edit_reply_markup()
    await state.finish()
