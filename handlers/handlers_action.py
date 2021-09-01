
import asyncio
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from datetime import date
from config import admin_id
from loader import scheduler, dp, db
from algorithm import transfer_users, generate_lists_of_matches, choose_match, transfer_matches


async def no_pair_notification(dp: Dispatcher):
    todaydate = int(str(date.today()).replace("-", ""))
    gen_matches = db.select_all_gen_matches()
    for i in gen_matches:
        if i[8] is None and i[2] == todaydate:
            await dp.bot.send_message(i[1],
                                      "И снова привет! 👋 Мы начали распределять пары.\n\n"
                                      "Совсем скоро пришлю анкету твоего собеседника")


async def no_pairs_admin_notification(dp: Dispatcher):
    todaydate = int(str(date.today()).replace("-", ""))
    gen_matches = db.select_all_gen_matches()
    print(gen_matches)
    c = 0
    list_no_matches = []
    list_no_matches_with_links = []
    for i in gen_matches:
        if i[8] is None and i[2] == todaydate:
            print(f"Start working with: {i[1]}")
            c += 1
            list_no_matches.append(i[1])
    print(list_no_matches)
    for i in list_no_matches:
        i = "<a href='tg://user?id=" + str(i) + "'>😧</a>"
        list_no_matches_with_links.append(i)
    list_no_matches_with_links = str(list_no_matches_with_links)[1:-1]
    print(list_no_matches_with_links)
    await dp.bot.send_message(admin_id,
                              f"Сегодня <b>{c}</b> человек без пары\n\n"
                              f"Вот список: {list_no_matches_with_links}"
                              )



async def send_pairs(dp: Dispatcher):
    todaydate = int(str(date.today()).replace("-", ""))
    matches = db.select_all_matches()
    print(matches)
    for i in matches:
        if i[0][-8:] == str(todaydate):
            user_data = db.select_user(id=i[2])
            gender = "Мужской"
            if user_data[3] == 0:
                gender = "Женский"
            try:
                await dp.bot.send_message(i[1],
                                          f"Привет! Я подобрал тебе пару для тренировки. Это <b>{user_data[2]}</b>\n\n"
                                          f"Вот его/ее анкета:\n"
                                          f"Возраст: {user_data[4]}\n"
                                          f"Пол: {gender}\n"
                                          f"Интересы (это поможет начать беседу): {user_data[5]}\n\n"
                                          f"Напиши <a href='tg://user?id={i[2]}'>{user_data[2]}</a> и договорись о звонке в Skype или Zoom.\n\n"
                                          f"<i>Если не знаешь, с чего начать, можешь скопировать сообщение ниже:</i>")
                await dp.bot.send_message(i[1],
                                          "Привет!👋 Нам выпала встреча в Talkie. Когда тебе будет удобно созвониться?")
                db.set_notification_1(i[1])
                await asyncio.sleep(.05)
            except Exception as e:
                print(f"Ошибка. Пользователь {i[1]}: {e}")
    for i in matches:
        if i[0][-8:] == str(todaydate):
            user_data = db.select_user(id=i[1])
            gender = "Мужской"
            if user_data[3] == 0:
                gender = "Женский"
            try:
                await dp.bot.send_message(i[2],
                                          f"Привет! Я подобрал тебе пару для тренировки. Это <b>{user_data[2]}</b>\n\n"
                                          f"Вот его/ее анкета:\n"
                                          f"Возраст: {user_data[4]}\n"
                                          f"Пол: {gender}\n"
                                          f"Интересы (это поможет начать беседу): {user_data[5]}\n\n"
                                          f"Напиши <a href='tg://user?id={i[1]}'>{user_data[2]}</a> и договорись о звонке в Skype или Zoom.\n\n"
                                          f"<i>Если не знаешь, с чего начать, можешь скопировать сообщение ниже:</i>")
                await dp.bot.send_message(i[2],
                                          "Привет!👋 Нам выпала встреча в Talkie. Когда тебе будет удобно созвониться?")
                db.set_notification_2(i[2])
                await asyncio.sleep(.05)
            except Exception as e:
                print(f"Ошибка. Пользователь {i[2]}: {e}")


def schedule_jobs(h, m):
    scheduler.add_job(transfer_users, "cron", hour=h, minute=m, second=1)
    scheduler.add_job(generate_lists_of_matches, "cron", hour=h, minute=m, second=2)
    scheduler.add_job(choose_match, "cron", hour=h, minute=m, second=3)
    scheduler.add_job(transfer_matches, "cron", hour=h, minute=m, second=4)
    scheduler.add_job(no_pair_notification, "cron",hour=h, minute=m, second=5, args=(dp,))
    scheduler.add_job(send_pairs, "cron", hour=h, minute=m, second=6, args=(dp,))
    scheduler.add_job(no_pairs_admin_notification, "cron", hour=h, minute=m, second=7, args=(dp,))