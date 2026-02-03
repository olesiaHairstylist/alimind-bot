# services/migration_short_term.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DISCLAIMER_PATH = DOCS_DIR / "DISCLAIMER.md"

# Если хотите — можно ссылаться на файл PDF по имени.
# В Telegram-ответе мы НЕ отдаём PDF целиком, а указываем источник.
SHORT_TERM_PDF_NAME = "short_term_requirements.pdf"


@dataclass(frozen=True)
class ShortTermContext:
    city: str
    province: str
    permit_type: str        # "Краткосрочный" или "Семейный"
    status: str             # "турист" и т.п.
    docs_on_hand: str
    purpose: str
    extra: str


# Структура требований — фиксируем как данные (стабильно, без парсинга PDF).
GENERAL_DOCS = [
    "Форма заявления на ВНЖ (подписанная заявителем/представителем)",
    "Паспорт/заменяющий документ + копии страниц с данными и визой (если есть); оригинал предъявляется на собеседовании",
    "2 биометрические фотографии (белый фон, не старше 6 месяцев, стандарты ICAO)",
    "Квитанция об уплате сбора за ВНЖ (если применимо)",
    "Квитанция об уплате сбора за однократную визу (если применимо)",
    "Действующая медицинская страховка на срок запрашиваемого ВНЖ",
    "Подтверждение достаточных финансовых средств на период пребывания",
    "Документы об адресе (справка о месте жительства + подтверждение коммунальным счётом/договором)",
    "Документ о месте фактического проживания (собственность/нот. аренда/отель/обязательство принимающего и т.д.)",
    "UETS (национальный электронный адрес уведомлений) — для лиц старше 18 лет",
]

TOURISM_EXTRA = [
    "Информация/документ о программе путешествия и месте проживания",
    "Подтверждение достаточного и регулярного дохода (допустимые варианты перечислены в официальном перечне)",
]

FAMILY_EXTRA = [
    "Документы о легальном пребывании родственника первой степени в Турции (ВНЖ/работа/иное разрешение)",
    "Документы, подтверждающие родство (например, брак/рождение) — с учётом требований к апостилю/легализации и переводу при выдаче за пределами Турции",
]

NOT_SPECIFIED = [
    "Единый формат подтверждения финансовых средств (указан перечень допустимых вариантов, без одного обязательного шаблона)",
    "Абсолютные суммы «достаточного дохода» в цифрах (в документе описан принцип достаточности)",
    "Приоритетность одного допустимого документа над другим",
]


def _read_md(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def render_short_term_answer(ctx: ShortTermContext, *, include_practice: bool = True) -> str:
    # 1) Заголовок
    lines: list[str] = []
    lines.append("📄 Документированный разбор требований")
    lines.append("Краткосрочный ВНЖ (туризм / семейные основания)")
    lines.append("")

    # 2) Входные данные (коротко, чтобы пользователь видел “под меня”)
    lines.append("🧾 Данные запроса (как понято):")
    lines.append(f"• Город/провинция: {ctx.city}, {ctx.province}")
    lines.append(f"• Тип: {ctx.permit_type}")
    lines.append(f"• Текущий статус: {ctx.status}")
    lines.append(f"• Документы на руках: {ctx.docs_on_hand}")
    lines.append(f"• Цель: {ctx.purpose}")
    lines.append(f"• Дополнительно: {ctx.extra}")
    lines.append("")

    # 3) Официально требуется
    lines.append("1) Что требует государство (официально)")
    lines.append("Общие документы:")
    for item in GENERAL_DOCS:
        lines.append(f"— {item}")
    lines.append("")

    # 4) Дополнительно по цели/основанию
    # У вас scope: туристы + семейный/краткосрочный. Мы выводим оба блока, но без лишних типов.
    lines.append("2) Дополнительно по цели пребывания")
    lines.append("Туризм:")
    for item in TOURISM_EXTRA:
        lines.append(f"— {item}")
    lines.append("")
    lines.append("Семейные основания (если заявляете семейную связь):")
    for item in FAMILY_EXTRA:
        lines.append(f"— {item}")
    lines.append("")

    # 5) Что не указано
    lines.append("3) Что официально не указано")
    for item in NOT_SPECIFIED:
        lines.append(f"— {item}")
    lines.append("")

    # 6) Практика — отдельно и помечено как неофициальное
    if include_practice:
        lines.append("4) Практика (неофициально)")
        lines.append("— В ходе рассмотрения могут запросить дополнительную информацию/документы.")
        lines.append("— Требования к подтверждению адреса/дохода могут уточняться в управлении миграции по месту подачи.")
        lines.append("")

    # 7) Источник
    lines.append("5) Источник (официально)")
    lines.append(f"— Официальный перечень документов для подачи на краткосрочный ВНЖ (PDF: {SHORT_TERM_PDF_NAME})")
    lines.append("")

    # 8) Дисклеймер
    disclaimer = _read_md(DISCLAIMER_PATH)
    if disclaimer:
        lines.append("⚠️ Важно")
        lines.append(disclaimer)

    return "\n".join(lines)
