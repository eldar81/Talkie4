from datetime import datetime
import logging
import sqlite3
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards import letsgo_button, bio_is_correct, bio_gender, gender_of_companion
from loader import dp, db
from FMS import Ankena


@dp.message_handler(Command("start"))
async def send_welcome(message: Message):
    try:
        db.add_user(id=message.from_user.id,
                    name=message.from_user.full_name)
        await message.answer(text="Привет! Меня зовут Talkie. Я помогу тебе прокачать навык общения  😃",
                             reply_markup=letsgo_button)
    except sqlite3.IntegrityError as err:
        print(err)
        await message.answer(text="Команда не распознана\n"
                                  "Воспользуйтся меню или напишите '/'")


@dp.callback_query_handler(text='step1')
async def start_step_0(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    await call.message.answer("🤖 Здорово! Чтобы я смог подобрать тебе собеседника, заполни короткую анкету\n\n",
                              disable_notification=True)
    await call.message.answer("❔Вопрос 1/5\n\n"
                              "Как тебя зовут?",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await Ankena.Name.set()


@dp.callback_query_handler(text='rewrite_anketa')
async def start_step_0(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    await call.message.answer("❔Вопрос 1/5\n\n"
                              "Как тебя зовут?",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await Ankena.Name.set()


@dp.callback_query_handler(text='step1')
async def start_step_1(call: CallbackQuery):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    await call.message.answer("Здорово! Чтобы я смог подобрать тебе собеседника, заполни короткую анкету\n\n"
                              "❔Вопрос 1/5\n\n"
                              "Как тебя зовут?",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await Ankena.Name.set()


@dp.message_handler(state=Ankena.Name)
async def start_step_2(message: Message, state: FSMContext):
    answer = message.text
    await state.update_data({"bio_name": answer})
    await message.answer(text="❔2/5\n\n"
                              "Сколько тебе лет?",
                         disable_notification=True)
    await Ankena.Age.set()



@dp.message_handler(state=Ankena.Age)
async def start_step_3(message: Message, state: FSMContext):
    answer = message.text
    if re.match(r'[1-9]{1}[0-9]{1}', answer) and len(answer) == 2:
        await state.update_data({"bio_age": int(answer)})
        await message.answer(text="❔3/5\n\n"
                              "Твой пол?",
                         reply_markup=bio_gender,
                         disable_notification=True
                         )
        await Ankena.Gender.set()
    else:
        await message.answer(text="❔Напиши свой возраст цифрами. Например:\n\n"
                                  "<i>22</i>",
                             disable_notification=True)
        await Ankena.Age.set()





@dp.callback_query_handler(state=Ankena.Gender)
async def start_step_4(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    answer_to_db = 0
    if callback_data == "male":
     answer_to_db = 1
    await state.update_data({"bio_gender": answer_to_db})
    await call.message.answer(text="❔4/5\n\n"
                                   "Расскажи, чем ты увлекаешься. Перечисли интересы через запятую. Например:\n\n"
                                   "<i>Фортепиано, шахматы, картины по номерам</i>",
                              disable_notification=True)
    await Ankena.Hobby.set()
    await call.message.edit_reply_markup()


@dp.message_handler(state=Ankena.Hobby)
async def start_step_5(message: Message, state: FSMContext):
    answer = message.text
    await state.update_data({"bio_hobby": answer})
    await message.answer("❔5/5\n\n"
                         "Скажи, какого пола нам найти для тебя собеседника?",
                              reply_markup=gender_of_companion,
                              disable_notification=True)
    await Ankena.Comp_req.set()



@dp.callback_query_handler(state=Ankena.Comp_req)
async def start_step_6(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    data = await state.get_data()
    bio_name = data.get("bio_name")
    bio_age = data.get("bio_age")
    bio_gender = data.get("bio_gender")
    bio_hobby = data.get("bio_hobby")
    callback_data = call.data
    logging.info(f"call = {callback_data}")
    answer = 2
    if callback_data == "gender_of_companion_male":
        answer = 1
    elif callback_data == "gender_of_companion_female":
        answer = 0
    bio_gender_letters = "Женский"
    bio_req_letters = "Нет"
    if bio_gender == 1:
        bio_gender_letters = "Мужской"
    if answer == 1:
        bio_req_letters = "Только мужского пола"
    elif answer == 0:
        bio_req_letters = "Только женского пола"

    await state.update_data({"bio_companion_requirements": answer})
    await call.message.answer(text=f"Отлично! Давай проверим твою анкету\n\n"
                              f"<strong>Имя:</strong> {bio_name}\n"
                              f"<strong>Возраст:</strong> {bio_age}\n"
                              f"<strong>Пол:</strong> {bio_gender_letters}\n"
                              f"<strong>Интересы:</strong> {bio_hobby}\n"
                              f"<strong>Пожелание к собеседнику:</strong> {bio_req_letters}\n\n"
                              f"Все верно?",
                         reply_markup=bio_is_correct,
                              disable_notification=True)
    await call.message.edit_reply_markup()
    logging.info(await state.get_data())
    await state.reset_state(with_data=False)


@dp.callback_query_handler(text="bio_is_ok")
async def start_step_7(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=5)
    data = await state.get_data()
    try:
        db.update_user_anketa(Bio_name=data.get("bio_name"),
                              Bio_age=data.get("bio_age"),
                              Bio_gender=data.get("bio_gender"),
                              Bio_hobby=data.get("bio_hobby"),
                              Bio_companion_requirements=data.get("bio_companion_requirements"),
                              id=call.from_user.id)
    except sqlite3.IntegrityError as err:
        print(err)
    print(db.select_all_users())

    tt = 16 * 60 + 29
    h = datetime.utcnow().time().hour
    m = datetime.utcnow().time().minute
    ts = h * 60 + m
    if ts > tt:
        await call.message.answer(text="Отлично! Теперь ты полностью готов(-а) к началу тренировок в Talie 🥳\n\n"
                                       "Пары для встреч формируются каждый день в 19:30 по МСК. "
                                       "Завтра я пришлю тебе первую пару.\n\n"
                                       "У Talkie есть <a href='https://letstalkie.ru/library'>База Знаний</a> об общении. "
                                       "Там много полезного и интересного материала 😊\n\n"
                                       "Также, обязательно прочитай небольшую <a href='https://telegra.ph/Kak-provesti-pervuyu-vstrechu-v-Talkie-08-23'>инструкцию</a> к первой встречи. "
                                       "Она поможет сделать ее комфортнее и интереснее 😉",
                                  disable_notification=True)
    else:

        await call.message.answer(text="Отлично! Теперь ты полностью готов(-а) к началу тренировок в Talie 🥳\n\n"
                                   "Пары для встреч формируются каждый день в 19:30 по МСК. "
                                   "Дождись этого времени и бот пришлет анкету твоего первого напарника.\n\n"
                                   "У Talkie есть <a href='https://letstalkie.ru/library'>База Знаний</a> об общении. "
                                   "Там много полезного и интересного материала 😊\n\n"
                                   "Также, обязательно прочитай небольшую <a href='https://telegra.ph/Kak-provesti-pervuyu-vstrechu-v-Talkie-08-23'>инструкцию</a> к первой встречи. "
                                   "Она поможет сделать ее комфортнее и интереснее 😉",
                              disable_notification=True)
    await call.message.edit_reply_markup()
    await state.finish()
