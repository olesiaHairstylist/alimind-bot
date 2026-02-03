from pathlib import Path
from typing import Optional

from aiogram.types import Message, FSInputFile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"


async def send_object_card(
    message: Message,
    text_html: str,
    photo_rel: Optional[str] = None,
    reply_markup=None,
):
    if photo_rel:
        photo_path = ASSETS_DIR / photo_rel

        if photo_path.exists() and photo_path.stat().st_size > 0:
            await message.answer_photo(
                photo=FSInputFile(str(photo_path)),
                caption=text_html,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return

    await message.answer(
        text_html,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
