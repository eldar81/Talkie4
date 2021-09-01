import random
from aiogram.utils import callback_data
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, callback_query
from config import admin_ids

# ВХОД В БОТА
from loader import dp

letsgo_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Поехали 🚀", callback_data="step1")
        ]
    ]
)

# ПОДТВЕРЖДЕНИЕ ПРАВИЛЬНОСТИ АНКЕТЫ
bio_is_correct = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все верно 👍", callback_data="bio_is_ok"),
            InlineKeyboardButton(text="Заполнить заново", callback_data='rewrite_anketa')
        ]
    ]
)

# ЗАДАТЬ СВОЙ ПОЛ
bio_gender = InlineKeyboardMarkup(row_width=1,
                                  inline_keyboard=[
                                      [InlineKeyboardButton(text="Мужской 🙋‍♂️", callback_data="male")],
                                      [InlineKeyboardButton(text="Женский 🙋‍♀️", callback_data="female")]
                                  ]
                                  )

# ВЫБРАТЬ ПОЛ СОБЕСЕДНИКА
gender_of_companion = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужского", callback_data="gender_of_companion_male")],
        [InlineKeyboardButton(text="Женского", callback_data="gender_of_companion_female")],
        [InlineKeyboardButton(text="Не важно", callback_data="gender_of_companion_both")]
    ]
)


# МЕНЮ PRIFILE
profile_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Изменить профиль ✍️", callback_data="change_my_profile")],
        [InlineKeyboardButton(text="Все верно 👍", callback_data="menu")]
    ]
)


# PROFILE ЧТО ИЗМЕНИТЬ
change_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Имя", callback_data="change_profile_name")],
        [InlineKeyboardButton(text="Пол", callback_data="change_profile_gender")],
        [InlineKeyboardButton(text="Возраст", callback_data="change_profile_age")],
        [InlineKeyboardButton(text="Интересы", callback_data="change_profile_hobby")],
        [InlineKeyboardButton(text="Пожелания к собеседнику", callback_data="change_profile_compreq")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]
    ]
)


# ПОДМЕНЮ PRIFILE
profile_submenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="change_my_profile")],
        [InlineKeyboardButton(text="В главное меню", callback_data="menu")]
    ]
)


# МЕНЮ HELP
help_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Бот работает странно/не работает 🤖", callback_data="bot_bug")],
        [InlineKeyboardButton(text="Не могу с чем-то разобраться 🧐", callback_data="need_help")],
        [InlineKeyboardButton(text="Пожаловаться на пользователя 🚔", callback_data="need_help")],
        [InlineKeyboardButton(text="Другое", callback_data="need_help")],
    ]
)


support_callback = CallbackData("ask_support", "messages", "user_id", "as_user")
cancel_support_callback = CallbackData("cancel_support", "user_id")


async def check_support_available(support_id):
    state = dp.current_state(chat=support_id, user=support_id)
    state_str = str(
        await state.get_state()
    )
    if state_str == "in_support":
        return
    else:
        return support_id


async def get_support_manager():
    random.shuffle(admin_ids)
    for support_id in admin_ids:
        # Проверим если оператор в данное время не занят
        support_id = await check_support_available(support_id)

        # Если такого нашли, что выводим
        if support_id:
            return support_id
    else:
        return


async def support_keyboard(messages, user_id=None):
    if user_id:
        # Есле указан второй айдишник - значит эта кнопка для оператора

        contact_id = int(user_id)
        as_user = "no"
        text = "Ответить"

    else:
        # Есле не указан второй айдишник - значит эта кнопка для пользователя
        # и нужно подобрать для него оператора

        contact_id = await get_support_manager()
        as_user = "yes"
        if messages == "many" and contact_id is None:
            # Если не нашли свободного оператора - выходим и говорим, что его нет
            return False
        elif messages == "one" and contact_id is None:
            contact_id = random.choice(admin_ids)

        if messages == "one":
            text = "Рассказать о проблеме"
        else:
            text = "Написать оператору"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=text,
            callback_data=support_callback.new(
                messages=messages,
                user_id=contact_id,
                as_user=as_user
            )
        )
    )

    if messages == "many":
        # Добавляем кнопку завершения сеанса, если передумали звонить в поддержку
        keyboard.add(
            InlineKeyboardButton(
                text="Завершить сеанс",
                callback_data=cancel_support_callback.new(
                    user_id=contact_id
                )
            )
        )
    return keyboard


def cancel_support(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить сеанс",
                    callback_data=cancel_support_callback.new(
                        user_id=user_id
                    )
                )
            ]
        ]
    )