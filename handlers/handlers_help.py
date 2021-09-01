from loader import dp, bot
from keyboards import help_menu, support_keyboard, support_callback, check_support_available, get_support_manager, \
    cancel_support, cancel_support_callback
from aiogram.types import Message, CallbackQuery, ContentTypes
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext



@dp.message_handler(Command("support"))
async def check_profile(message: Message):
    await message.answer(text="Привет! С какой проблемой ты столкнулся(-ась)?",
                         reply_markup=help_menu)


@dp.callback_query_handler(text="bot_bug")
async def ask_support(call: CallbackQuery):
    text = "Чтобы отправить тех. поддержке сообщение об ошибке, нажмите кнопку ниже"
    keyboard = await support_keyboard(messages="one")
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(support_callback.filter(messages="one"))
async def send_to_support(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    user_id = int(callback_data.get("user_id"))
    await call.message.answer("Пришлите ваше сообщение, которым вы хотите поделиться")
    await state.set_state("wait_for_support_message")
    await state.update_data(second_id=user_id)


@dp.message_handler(state="wait_for_support_message", content_types=ContentTypes.ANY)
async def get_support_message(message: Message, state: FSMContext):
    data = await state.get_data()
    second_id = data.get("second_id")

    await bot.send_message(second_id,
                           f"Вам письмо! Вы можете ответить нажав на кнопку ниже")
    keyboard = await support_keyboard(messages="one", user_id=message.from_user.id)
    await message.copy_to(second_id, reply_markup=keyboard)

    await message.answer("Сообщение отправлено в поддержку. Оператор скоро ответит")
    await state.reset_state()



# ---------------------------------------------------



@dp.callback_query_handler(text="need_help")
async def ask_support_call(call: CallbackQuery):
    text = "Для связи с оператором нажмите на кнопку ниже"
    keyboard = await support_keyboard(messages="many")
    if not keyboard:
        await call.message.answer("К сожалению, сейчас нет свободных операторов. Попробуйте позже.")
        return
    await call.message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="yes"))
async def send_to_support_call(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_text("Вы обратились в техподдержку. Оператор подключается. Подождите 20-30 секунд.")

    user_id = int(callback_data.get("user_id"))
    if not await check_support_available(user_id):
        support_id = await get_support_manager()
    else:
        support_id = user_id

    if not support_id:
        await call.message.edit_text("К сожалению, сейчас нет свободных операторов. Попробуйте позже.")
        await state.reset_state()
        return

    await state.set_state("wait_in_support")
    await state.update_data(second_id=support_id)

    keyboard = await support_keyboard(messages="many", user_id=call.from_user.id)

    await bot.send_message(support_id,
                           f"С вами хочет связаться пользователь {call.from_user.full_name}",
                           reply_markup=keyboard
                           )


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="no"))
async def answer_support_call(call: CallbackQuery, state: FSMContext, callback_data: dict):
    second_id = int(callback_data.get("user_id"))
    user_state = dp.current_state(user=second_id, chat=second_id)

    if str(await user_state.get_state()) != "wait_in_support":
        await call.message.edit_text("К сожалению, пользователь уже передумал.")
        return

    await state.set_state("in_support")
    await user_state.set_state("in_support")

    await state.update_data(second_id=second_id)

    keyboard = cancel_support(second_id)
    keyboard_second_user = cancel_support(call.from_user.id)

    await call.message.edit_text("Вы на связи с пользователем!\n"
                                 "Чтобы завершить общение нажмите на кнопку.",
                                 reply_markup=keyboard
                                 )
    await bot.send_message(second_id,
                           "Техподдержка на связи! Расскажите, что случилось.\n\n"
                           "<i>Чтобы завершить общение нажмите на кнопку.</i>",
                           reply_markup=keyboard_second_user
                           )


@dp.message_handler(state="wait_in_support", content_types=ContentTypes.ANY)
async def not_supported(message: Message, state: FSMContext):
    data = await state.get_data()
    second_id = data.get("second_id")

    keyboard = cancel_support(second_id)
    await message.answer("Дождитесь ответа оператора или отмените сеанс", reply_markup=keyboard)


@dp.callback_query_handler(cancel_support_callback.filter(), state=["in_support", "wait_in_support", None])
async def exit_support(call: CallbackQuery, state: FSMContext, callback_data: dict):
    user_id = int(callback_data.get("user_id"))
    second_state = dp.current_state(user=user_id, chat=user_id)

    if await second_state.get_state() is not None:
        data_second = await second_state.get_data()
        second_id = data_second.get("second_id")
        if int(second_id) == call.from_user.id:
            await second_state.reset_state()
            await bot.send_message(user_id, "Сеанс техподдержки был завершен.")

    await call.message.edit_text("Вы завершили сеанс")
    await state.reset_state()