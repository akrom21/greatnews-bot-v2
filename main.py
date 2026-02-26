import os
import re
import asyncio
import aiosqlite
from typing import Optional, Dict

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()

# ========= ENV =========
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "Greatnews_academy").strip().lstrip("@")

CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME}"   # knopka uchun
CHANNEL_CHAT = f"@{CHANNEL_USERNAME}"               # obuna tekshirish uchun
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@akrom_GN").strip()
OFFICE_MAP_URL = os.getenv("OFFICE_MAP_URL", "https://maps.app.goo.gl/L5PAc4TSfgpcAveA7").strip()
ADMIN_ID = int((os.getenv("ADMIN_ID", "") or "0").strip() or "0")

DB_PATH = "greatnews_v2.db"
PHONE_RE = re.compile(r"^\+998\d{9}$")

UZ, RU = "uz", "ru"

def tme(username_with_at: str) -> str:
    return f"https://t.me/{username_with_at.lstrip('@')}"

T: Dict[str, Dict[str, str]] = {
    UZ: {
        "choose_lang": "Tilni tanlang 👇",
        "sub_need": "Davom etish uchun rasmiy kanalimizga obuna bo‘ling 👇",
        "sub_btn": "📣 Kanalga o‘tish",
        "sub_check": "✅ Obuna bo‘ldim",
        "sub_no": "Hali obuna bo‘lmagansiz ❌",
        "welcome": "Xush kelibsiz! Bo‘limni tanlang 👇",

        "menu_course": "📚 Kursga yozilish",
        "menu_partner": "🤝 Hamkorlik",
        "menu_results": "🏆 Natijalar",
        "menu_support": "👨‍💻 Support",
        "menu_about": "ℹ️ Biz haqimizda",
        "menu_why": "🔥 Nega aynan biz?",
        "menu_vip": "💎 VIP kanal",

        "course_intro": (
            "📚 <b>Kursga yozilish</b>\n\n"
            "🎓 Ta’lim: <b>TEKIN</b>\n"
            "📈 Amaliyot: risk-management bilan\n"
            "💼 Keyin: depozit qilib birga ishlaymiz\n"
            "💰 Foyda: <b>50/50</b>\n\n"
            "✅ Boshlash uchun pastdagi tugmani bosing:"
        ),
        "start_apply": "📝 Arizani boshlash",
        "cancel": "❌ Bekor qilish",
        "back_menu": "⬅️ Menyu",

        "ask_name": "Ism va familiyangizni kiriting (masalan: Akrom Jumanazarov):",
        "ask_age": "Yoshingizni kiriting (faqat raqam). <b>Minimum 18+</b>.",
        "age_bad": "Yosh noto‘g‘ri. Iltimos, faqat raqam kiriting.",
        "age_under": "Kechirasiz, minimal yosh <b>18+</b>.",
        "ask_phone": "Telefon raqamingizni shu formatda yuboring:\n<b>+998901234567</b>",
        "phone_bad": "Telefon raqam formati noto‘g‘ri.\nTo‘g‘ri format: <b>+998901234567</b>",
        "ask_mode": "Qaysi formatda qatnashasiz?",
        "mode_online": "🌐 Onlayn",
        "mode_offline": "🏢 Offlayn",
        "office_btn": "📍 Ofis lokatsiya (Maps)",

        "done_user": "✅ Ariza qabul qilindi! Admin tez orada bog‘lanadi.",
        "done_admin_title": "📥 <b>YANGI ARIZA</b>",

        "partner_text": (
            "🤝 <b>Hamkorlik</b>\n\n"
            f"Aloqa: <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "results_text": (
            "🏆 <b>Natijalar</b>\n\n"
            "Real natijalar kanalda:\n"
            f"👉 <a href='{tme(CHANNEL_USERNAME)}'>{CHANNEL_USERNAME}</a>"
        ),
        "support_text": (
            "👨‍💻 <b>Support</b>\n\n"
            f"👤 {SUPPORT_USERNAME}\n"
            "📞 +998909995818\n"
            f"👉 <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "vip_text": (
            "💎 <b>VIP kanal</b>\n\n"
            "VIP — yopiq imkoniyatlar (signal, strategiya, jamoa).\n"
            "Kirish uchun yozing:\n"
            f"👉 <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "about_text": (
            "ℹ️ <b>Biz haqimizda</b>\n\n"
            "Biz kurs sotmaymiz — biz <b>odamni natijaga olib boramiz</b>.\n\n"
            "🎓 Ta’lim: <b>TEKIN</b>\n"
            "💼 Depozit bilan birga ishlaymiz\n"
            "💰 Foyda: <b>50/50</b>\n\n"
            "⚠️ Muhim:\n"
            "Biz hammani qabul qilmaymiz — intizom va mas’uliyat kerak.\n\n"
            "🔒 Bu yo‘l ‘tez boyish’ emas.\n"
            "Bu — tizim, jamoa va real o‘sish."
        ),
        "why_text": (
            "🔥 <b>Nega aynan biz?</b>\n\n"
            "❌ Biz tez boyishni va’da qilmaymiz.\n"
            "❌ Biz shunchaki signal tashlab ketmaymiz.\n\n"
            "✅ Biz jarayon beramiz:\n"
            "O‘rganish → Amaliyot → Birga savdo → Natija\n\n"
            "✅ Jamoa + mentor\n"
            "✅ Risk-management va psixologiya\n\n"
            "Agar siz mas’uliyatni ola olsangiz — siz bizga mos kelasiz."
        ),
    },
    RU: {
        "choose_lang": "Выберите язык 👇",
        "sub_need": "Чтобы продолжить, подпишитесь на наш официальный канал 👇",
        "sub_btn": "📣 Перейти в канал",
        "sub_check": "✅ Я подписался",
        "sub_no": "Вы ещё не подписаны ❌",
        "welcome": "Добро пожаловать! Выберите раздел 👇",

        "menu_course": "📚 Записаться на курс",
        "menu_partner": "🤝 Сотрудничество",
        "menu_results": "🏆 Результаты",
        "menu_support": "👨‍💻 Поддержка",
        "menu_about": "ℹ️ О нас",
        "menu_why": "🔥 Почему именно мы?",
        "menu_vip": "💎 VIP канал",

        "course_intro": (
            "📚 <b>Запись на курс</b>\n\n"
            "🎓 Обучение: <b>БЕСПЛАТНО</b>\n"
            "📈 Практика с risk-management\n"
            "💼 Далее: депозит и совместная торговля\n"
            "💰 Прибыль: <b>50/50</b>\n\n"
            "✅ Нажмите кнопку ниже, чтобы начать анкету:"
        ),
        "start_apply": "📝 Начать анкету",
        "cancel": "❌ Отмена",
        "back_menu": "⬅️ Меню",

        "ask_name": "Введите имя и фамилию:",
        "ask_age": "Введите возраст (только цифры). <b>Минимум 18+</b>.",
        "age_bad": "Возраст указан неверно. Введите только цифры.",
        "age_under": "Извините, минимальный возраст <b>18+</b>.",
        "ask_phone": "Отправьте номер в формате:\n<b>+998901234567</b>",
        "phone_bad": "Неверный формат номера.\nПравильно: <b>+998901234567</b>",
        "ask_mode": "Выберите формат участия:",
        "mode_online": "🌐 Онлайн",
        "mode_offline": "🏢 Офлайн",
        "office_btn": "📍 Локация офиса (Maps)",

        "done_user": "✅ Анкета принята! Администратор скоро свяжется с вами.",
        "done_admin_title": "📥 <b>НОВАЯ АНКЕТА</b>",

        "partner_text": (
            "🤝 <b>Сотрудничество</b>\n\n"
            f"Контакт: <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "results_text": (
            "🏆 <b>Результаты</b>\n\n"
            "Реальные результаты в канале:\n"
            f"👉 <a href='{tme(CHANNEL_USERNAME)}'>{CHANNEL_USERNAME}</a>"
        ),
        "support_text": (
            "👨‍💻 <b>Поддержка</b>\n\n"
            f"👤 {SUPPORT_USERNAME}\n"
            "📞 +998909995818\n"
            f"👉 <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "vip_text": (
            "💎 <b>VIP канал</b>\n\n"
            "VIP — закрытые возможности (сигналы, стратегии, комьюнити).\n"
            "Напишите для доступа:\n"
            f"👉 <a href='{tme(SUPPORT_USERNAME)}'>{SUPPORT_USERNAME}</a>"
        ),
        "about_text": (
            "ℹ️ <b>О нас</b>\n\n"
            "Мы не продаём курс — мы <b>доводим до результата</b>.\n\n"
            "🎓 Обучение: <b>БЕСПЛАТНО</b>\n"
            "💼 Депозит и совместная торговля\n"
            "💰 Прибыль: <b>50/50</b>\n\n"
            "⚠️ Важно:\n"
            "Мы берём не всех — нужна дисциплина и ответственность.\n\n"
            "🔒 Это не про «быстро разбогатеть».\n"
            "Это — система, команда и реальный рост."
        ),
        "why_text": (
            "🔥 <b>Почему именно мы?</b>\n\n"
            "❌ Мы не обещаем быстрых денег.\n"
            "❌ Мы не просто кидаем сигналы.\n\n"
            "✅ Мы даём процесс:\n"
            "Обучение → Практика → Совместная торговля → Результат\n\n"
            "✅ Команда + ментор\n"
            "✅ Risk-management и психология\n\n"
            "Если вы готовы брать ответственность — вы нам подходите."
        ),
    },
}

# ========= DB =========
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'uz',
                username TEXT,
                first_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lang TEXT,
                name TEXT,
                age INTEGER,
                phone TEXT,
                mode TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def set_user_lang(user_id: int, lang: str, username: Optional[str], first_name: Optional[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users(user_id, lang, username, first_name)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang, username=excluded.username, first_name=excluded.first_name
        """, (user_id, lang, username, first_name))
        await db.commit()

async def get_user_lang(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row and row[0] in (UZ, RU) else UZ

async def save_application(user_id: int, lang: str, name: str, age: int, phone: str, mode: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO applications(user_id, lang, name, age, phone, mode)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (user_id, lang, name, age, phone, mode))
        await db.commit()

# ========= UI =========
def kb_lang() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
    ])

def kb_sub(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["sub_btn"], url=tme(CHANNEL_USERNAME))],
        [InlineKeyboardButton(text=T[lang]["sub_check"], callback_data="sub:check")],
    ])

def kb_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["menu_course"], callback_data="menu:course")],
        [InlineKeyboardButton(text=T[lang]["menu_partner"], callback_data="menu:partner")],
        [InlineKeyboardButton(text=T[lang]["menu_results"], callback_data="menu:results")],
        [InlineKeyboardButton(text=T[lang]["menu_support"], callback_data="menu:support")],
        [InlineKeyboardButton(text=T[lang]["menu_about"], callback_data="menu:about")],
        [InlineKeyboardButton(text=T[lang]["menu_why"], callback_data="menu:why")],
        [InlineKeyboardButton(text=T[lang]["menu_vip"], callback_data="menu:vip")],
    ])

def kb_back(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["back_menu"], callback_data="menu:home")]
    ])

def kb_course_entry(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["start_apply"], callback_data="course:apply")],
        [InlineKeyboardButton(text=T[lang]["back_menu"], callback_data="menu:home")]
    ])

def kb_mode(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["mode_online"], callback_data="mode:on")],
        [InlineKeyboardButton(text=T[lang]["mode_offline"], callback_data="mode:off")],
        [InlineKeyboardButton(text=T[lang]["cancel"], callback_data="apply:cancel")],
    ])

def kb_office(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T[lang]["office_btn"], url=OFFICE_MAP_URL)],
        [InlineKeyboardButton(text=T[lang]["back_menu"], callback_data="menu:home")]
    ])

# ========= Subscription =========
async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

# ========= FSM =========
class Apply(StatesGroup):
    name = State()
    age = State()
    phone = State()
    mode = State()

# ========= Bot =========
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(T[UZ]["choose_lang"], reply_markup=kb_lang(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("lang:"))
async def set_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split(":")[1]
    if lang not in (UZ, RU):
        lang = UZ
    await set_user_lang(cb.from_user.id, lang, cb.from_user.username, cb.from_user.first_name)
    await state.clear()

    if not await is_subscribed(bot, cb.from_user.id):
        await cb.message.answer(T[lang]["sub_need"], reply_markup=kb_sub(lang), parse_mode="HTML")
    else:
        await cb.message.answer(T[lang]["welcome"], reply_markup=kb_menu(lang), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "sub:check")
async def sub_check(cb: CallbackQuery):
    lang = await get_user_lang(cb.from_user.id)
    if not await is_subscribed(bot, cb.from_user.id):
        await cb.answer(T[lang]["sub_no"], show_alert=True)
        return
    await cb.message.answer(T[lang]["welcome"], reply_markup=kb_menu(lang), parse_mode="HTML")
    await cb.answer()

# ========= Menu =========
async def gate_or_menu(cb: CallbackQuery) -> Optional[str]:
    lang = await get_user_lang(cb.from_user.id)
    if not await is_subscribed(bot, cb.from_user.id):
        await cb.message.answer(T[lang]["sub_need"], reply_markup=kb_sub(lang), parse_mode="HTML")
        return None
    return lang

@dp.callback_query(F.data == "menu:home")
async def menu_home(cb: CallbackQuery):
    lang = await get_user_lang(cb.from_user.id)
    if not await is_subscribed(bot, cb.from_user.id):
        await cb.message.answer(T[lang]["sub_need"], reply_markup=kb_sub(lang), parse_mode="HTML")
    else:
        await cb.message.answer(T[lang]["welcome"], reply_markup=kb_menu(lang), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "menu:course")
async def menu_course(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["course_intro"], reply_markup=kb_course_entry(lang), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "menu:partner")
async def menu_partner(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["partner_text"], reply_markup=kb_back(lang), parse_mode="HTML", disable_web_page_preview=True)
    await cb.answer()

@dp.callback_query(F.data == "menu:results")
async def menu_results(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["results_text"], reply_markup=kb_back(lang), parse_mode="HTML", disable_web_page_preview=True)
    await cb.answer()

@dp.callback_query(F.data == "menu:support")
async def menu_support(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["support_text"], reply_markup=kb_back(lang), parse_mode="HTML", disable_web_page_preview=True)
    await cb.answer()

@dp.callback_query(F.data == "menu:about")
async def menu_about(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["about_text"], reply_markup=kb_back(lang), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "menu:why")
async def menu_why(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["why_text"], reply_markup=kb_back(lang), parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "menu:vip")
async def menu_vip(cb: CallbackQuery):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await cb.message.answer(T[lang]["vip_text"], reply_markup=kb_back(lang), parse_mode="HTML", disable_web_page_preview=True)
    await cb.answer()

# ========= Apply flow =========
@dp.callback_query(F.data == "course:apply")
async def apply_start(cb: CallbackQuery, state: FSMContext):
    lang = await gate_or_menu(cb)
    if not lang:
        await cb.answer()
        return
    await state.clear()
    await state.update_data(lang=lang)
    await state.set_state(Apply.name)
    await cb.message.answer(T[lang]["ask_name"], parse_mode="HTML")
    await cb.answer()

@dp.callback_query(F.data == "apply:cancel")
async def apply_cancel(cb: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(cb.from_user.id)
    await state.clear()
    await cb.message.answer(T[lang]["welcome"], reply_markup=kb_menu(lang), parse_mode="HTML")
    await cb.answer()

@dp.message(Apply.name)
async def apply_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or await get_user_lang(message.from_user.id)

    name = (message.text or "").strip()
    if len(name) < 3:
        await message.answer(T[lang]["ask_name"], parse_mode="HTML")
        return

    await state.update_data(name=name)
    await state.set_state(Apply.age)
    await message.answer(T[lang]["ask_age"], parse_mode="HTML")

@dp.message(Apply.age)
async def apply_age(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or await get_user_lang(message.from_user.id)

    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer(T[lang]["age_bad"], parse_mode="HTML")
        return

    age = int(raw)
    if age < 18:
        await message.answer(T[lang]["age_under"], parse_mode="HTML")
        await state.clear()
        await message.answer(T[lang]["welcome"], reply_markup=kb_menu(lang), parse_mode="HTML")
        return

    await state.update_data(age=age)
    await state.set_state(Apply.phone)
    await message.answer(T[lang]["ask_phone"], parse_mode="HTML")

@dp.message(Apply.phone)
async def apply_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or await get_user_lang(message.from_user.id)

    phone = (message.text or "").strip()
    if not PHONE_RE.fullmatch(phone):
        await message.answer(T[lang]["phone_bad"], parse_mode="HTML")
        return

    await state.update_data(phone=phone)
    await state.set_state(Apply.mode)
    await message.answer(T[lang]["ask_mode"], reply_markup=kb_mode(lang), parse_mode="HTML")

@dp.callback_query(F.data.startswith("mode:"))
async def apply_mode(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang") or await get_user_lang(cb.from_user.id)

    key = cb.data.split(":")[1]
    mode = T[lang]["mode_online"] if key == "on" else T[lang]["mode_offline"]

    final = await state.get_data()
    name = final.get("name", "")
    age = int(final.get("age", 0))
    phone = final.get("phone", "")

    await save_application(cb.from_user.id, lang, name, age, phone, mode)

    await cb.message.answer(
        T[lang]["done_user"],
        reply_markup=kb_menu(lang),
        parse_mode="HTML"
    )

    if key == "off":
        await cb.message.answer(
            "📍",
            reply_markup=kb_office(lang)
        )

    if ADMIN_ID:
        user_link = (
            f"https://t.me/{cb.from_user.username}"
            if cb.from_user.username
            else f"ID: {cb.from_user.id}"
        )

        admin_msg = (
            f"{T[lang]['done_admin_title']}\n\n"
            f"👤 Ism: <b>{name}</b>\n"
            f"🎂 Yosh: <b>{age}</b>\n"
            f"📞 Telefon: <b>{phone}</b>\n"
            f"📍 Format: <b>{mode}</b>\n"
            f"🌍 Til: <b>{'UZ' if lang == 'uz' else 'RU'}</b>\n\n"
            f"🔗 User: {user_link}"
        )

        try:
            await bot.send_message(
                ADMIN_ID,
                admin_msg,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception:
            pass

    await state.clear()
    await cb.answer()


# ================== MAIN ==================

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
