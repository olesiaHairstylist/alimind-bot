from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

HELP_TEXT = (
    "Справка\n\n"
    "/start — открыть меню\n"
    "/search — поиск по каталогу (результаты листаются ◀️/▶️)\n"
    "/cancel — отменить ввод (например, во время поиска)\n\n"
    "Открыть карточку:\n"
    "• отправьте ID в сообщении (например, GOV_ASAT)\n"
    "• или напишите: ID: <id>\n\n"
    "Если бот пишет «Не понял запрос» — используйте /start или /search.\n"
    "\n"
    "🤖 AI-помощник\n\n"
    "Вы можете задать вопрос свободным текстом\n"
    "и получить один ответ на основе данных справочника.\n\n"
    "Команда:\n"
    "/ai\n\n"
    "ℹ️ Это отдельный платный режим.\n"
    "Цена: 3 € за один запрос.\n"
    "Один запрос = один ответ.\n"
    "Если данных нет — AI честно сообщит об этом.\n"
    "\n"
    "🤖 AI Assistant\n\n"
    "You can ask a free-text question\n"
    "and receive one answer based on the directory data.\n\n"
    "Command:\n"
    "/ai\n\n"
    "ℹ️ This is a separate paid mode.\n"
    "Price: 3 € per request.\n"
    "One request = one answer.\n"
    "If there is no data, the AI will say so directly."
)

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode=None)
