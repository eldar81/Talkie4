from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loader import dp


@dp.message_handler(Command("library"))
async def library_command(message: Message):
    await message.answer("Команда Talkie ведет <a href='https://letstalkie.ru/library'>Базу Знаний</a> об общении, эффективной коммуникации и уверенности в себе.\n\n"
                         "Читайте и применяйте на практике! "
                         "А если у нас нет материала на интересную вам тему, вы можете предложить ее в форме на сайте.",
                         disable_notification=True)
