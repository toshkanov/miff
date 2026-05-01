import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from uptimer import start_uptimer
import asyncio
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "7957317193:AAHIUCEdcY1Vp6W40gQAG-JntSVIj50FN_g"
GROUP_CHAT_ID = "-1003618737257"
MANAGER_CODE = "5566"

# ===================== HOLATLAR =====================
(REG_ROLE, REG_NAME, REG_PHONE, REG_MANAGER_CODE,
 CONTRACT_PHOTO, CONTRACT_CLIENT_NAME, CONTRACT_CLIENT_PHONE,
 CONTRACT_ADDRESS, CONTRACT_PRODUCT) = range(9)

# ===================== MA'LUMOTLAR =====================
operators = {}
contracts = {}

# ===================== YORDAMCHI =====================
def get_operator(user_id):
    return operators.get(user_id)

def get_today_str():
    return datetime.now().strftime("%d.%m.%Y")

def operator_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📝 Shartnoma tuzish", callback_data="new_contract")
    ]])

def manager_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Shartnoma tuzish", callback_data="new_contract")],
        [InlineKeyboardButton("👥 Operatorlarim", callback_data="my_operators")]
    ])

# ===================== /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    op = get_operator(user_id)

    if op:
        if op["role"] == "manager":
            await update.message.reply_text(
                f"👔 Xush kelibsiz, *{op['name']}*!",
                parse_mode="Markdown",
                reply_markup=manager_menu()
            )
        else:
            await update.message.reply_text(
                f"👷 Xush kelibsiz, *{op['name']}*!",
                parse_mode="Markdown",
                reply_markup=operator_menu()
            )
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("👷 Operator", callback_data="role_operator"),
        InlineKeyboardButton("👔 Menejer", callback_data="role_manager")
    ]])
    await update.message.reply_text(
        "🤖 *Xush kelibsiz!*\n\nRolingizni tanlang:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return REG_ROLE

# ===================== ROL TANLASH =====================
async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "role_operator":
        context.user_data["role"] = "operator"
        await query.edit_message_text("👷 Ismingizni kiriting:")
        return REG_NAME
    else:
        context.user_data["role"] = "manager"
        await query.edit_message_text("👔 Menejer kodini kiriting:")
        return REG_MANAGER_CODE

# ===================== OPERATOR RO'YXAT =====================
async def reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("📱 Telefon raqamingizni kiriting:")
    return REG_PHONE

async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = context.user_data["name"]
    phone = update.message.text.strip()

    operators[user_id] = {
        "name": name,
        "phone": phone,
        "role": "operator",
        "registered_at": datetime.now()
    }
    contracts[user_id] = []

    await update.message.reply_text(
        f"✅ *Ro'yxatdan o'tdingiz!*\n👤 {name}\n📱 {phone}",
        parse_mode="Markdown",
        reply_markup=operator_menu()
    )
    return ConversationHandler.END

# ===================== MENEJER KIRISH =====================
async def reg_manager_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text.strip()

    if code != MANAGER_CODE:
        await update.message.reply_text("❌ Noto'g'ri kod! Qayta kiriting:")
        return REG_MANAGER_CODE

    operators[user_id] = {
        "name": "Ibodat",
        "phone": "+998900011194",
        "role": "manager",
        "registered_at": datetime.now()
    }
    contracts[user_id] = []

    await update.message.reply_text(
        "✅ *Xush kelibsiz, Ibodat!*\n📱 +998900011194",
        parse_mode="Markdown",
        reply_markup=manager_menu()
    )
    return ConversationHandler.END

# ===================== SHARTNOMA =====================
async def new_contract_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if not get_operator(user_id):
        await query.edit_message_text("❌ Avval ro'yxatdan o'ting! /start")
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["in_contract"] = True
    await query.edit_message_text("📸 Mahsulot rasmini yuboring:")
    return CONTRACT_PHOTO

async def contract_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Rasm yuboring:")
        return CONTRACT_PHOTO
    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("👤 Mijoz ismini kiriting:")
    return CONTRACT_CLIENT_NAME

async def contract_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_name"] = update.message.text.strip()
    await update.message.reply_text("📱 Mijoz telefon raqamini kiriting:")
    return CONTRACT_CLIENT_PHONE

async def contract_client_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["client_phone"] = update.message.text.strip()
    await update.message.reply_text("🏠 Manzilni kiriting:")
    return CONTRACT_ADDRESS

async def contract_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text.strip()
    await update.message.reply_text("📦 Mahsulot nomini kiriting:")
    return CONTRACT_PRODUCT

async def contract_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data["product"] = update.message.text.strip()
    op = get_operator(user_id)
    today = get_today_str()

    contract = {
        "date": datetime.now(),
        "client_name": context.user_data["client_name"],
        "client_phone": context.user_data["client_phone"],
        "address": context.user_data["address"],
        "product": context.user_data["product"],
        "photo": context.user_data["photo"],
        "operator_name": op["name"],
    }

    if user_id not in contracts:
        contracts[user_id] = []
    contracts[user_id].append(contract)

    caption = (
        f"👤 *Mijoz:* {contract['client_name']}\n\n"
        f"📱 *Tel:* {contract['client_phone']}\n\n"
        f"🏠 *Manzil:* {contract['address']}\n\n"
        f"📦 *Mahsulot:* {contract['product']}\n\n"
        f"👷 *Operator:* {op['name']}\n\n"
        f"📅 *Sana:* {today}"
    )

    try:
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=contract["photo"],
            caption=caption,
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            "✅ *Shartnoma muvaffaqiyatli yuborildi!*",
            parse_mode="Markdown",
            reply_markup=manager_menu() if op["role"] == "manager" else operator_menu()
        )
    except Exception as e:
        logging.error(f"Gruppaga yuborishda xato: {e}")
        await update.message.reply_text(
            f"❌ Gruppaga yuborishda xato: {e}\n\nGruppa ID: {GROUP_CHAT_ID}\nBot gruppada admin ekanligini tekshiring!"
        )

    return ConversationHandler.END

# ===================== OPERATORLAR RO'YXATI =====================
async def my_operators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    op = get_operator(user_id)
    if not op or op["role"] != "manager":
        await query.edit_message_text("❌ Sizda bu huquq yo'q.")
        return

    op_list = [(uid, data) for uid, data in operators.items() if data["role"] == "operator"]

    if not op_list:
        await query.edit_message_text(
            "👥 Hozircha ro'yxatdan o'tgan operator yo'q.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="back_manager")]])
        )
        return

    keyboard = []
    for uid, data in op_list:
        keyboard.append([InlineKeyboardButton(f"👷 {data['name']}", callback_data=f"op_{uid}")])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_manager")])

    await query.edit_message_text(
        f"👥 *Operatorlar ro'yxati* ({len(op_list)} ta):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def operator_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    op_uid = int(query.data.replace("op_", ""))
    op_data = operators.get(op_uid)

    if not op_data:
        await query.edit_message_text("❌ Topilmadi.")
        return

    fifteen_ago = datetime.now() - timedelta(days=15)
    recent = [c for c in contracts.get(op_uid, []) if c["date"] >= fifteen_ago]

    text = (
        f"👷 *{op_data['name']}*\n"
        f"📱 {op_data['phone']}\n\n"
        f"📋 *Oxirgi 15 kun:* {len(recent)} ta shartnoma\n"
    )
    for i, c in enumerate(recent, 1):
        text += f"\n{i}. 👤 {c['client_name']} | 📦 {c['product']} | 📅 {c['date'].strftime('%d.%m.%Y')}"

    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="my_operators")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def back_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Nima qilmoqchisiz?", reply_markup=manager_menu())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    op = get_operator(user_id)
    await update.message.reply_text(
        "❌ Bekor qilindi.",
        reply_markup=manager_menu() if op and op["role"] == "manager" else operator_menu()
    )
    return ConversationHandler.END

# ===================== MAIN =====================
async def main_bot():
    # 1. Uptimer serverni ishga tushiramiz (Render o'chib qolmasligi uchun)
    start_uptimer()

    # 2. Telegram Botni sozlaymiz
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(new_contract_start, pattern="^new_contract$"),
        ],
        states={
            REG_ROLE: [CallbackQueryHandler(role_selected, pattern="^role_")],
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone)],
            REG_MANAGER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_manager_code)],
            CONTRACT_PHOTO: [MessageHandler(filters.PHOTO, contract_photo)],
            CONTRACT_CLIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_client_name)],
            CONTRACT_CLIENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_client_phone)],
            CONTRACT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_address)],
            CONTRACT_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contract_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(my_operators, pattern="^my_operators$"))
    app.add_handler(CallbackQueryHandler(operator_detail, pattern="^op_\\d+$"))
    app.add_handler(CallbackQueryHandler(back_manager, pattern="^back_manager$"))

    # 3. Botni ishga tushiramiz
    print("✅ Bot va Uptimer ishga tushdi...")

    # run_polling() o'zi ichkarida asyncio event loopni boshqaradi
    async with app:
        await app.initialize()
        await app.start_polling()
        # Bot to'xtamaguncha kutib turadi
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")