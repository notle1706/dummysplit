from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.filters import Text
from config import API_BOT_TOKEN, DESCRIPTION, PAYER, AMOUNT, SPLIT, SELECT_MEMBERS, UNEQUAL_SPLIT
from handlers.start_handler import start
from handlers.info_handler import status, all_expenses
from handlers.expense_handler import (
    add_expense,
    collect_description,
    select_payer,
    collect_amount,
    handle_split,
    select_members,
    collect_unequal_split,
)

def main():
    application = Application.builder().token(API_BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_expense)],
        states={
            DESCRIPTION: [MessageHandler(Text(), collect_description)],
            PAYER: [CallbackQueryHandler(select_payer)],
            AMOUNT: [MessageHandler(Text(), collect_amount)],
            SPLIT: [CallbackQueryHandler(handle_split)],
            SELECT_MEMBERS: [CallbackQueryHandler(select_members)],
            UNEQUAL_SPLIT: [MessageHandler(Text(), collect_unequal_split)],
        },
        fallbacks=[CommandHandler("join", start)],
    )

    application.add_handler(CommandHandler("join", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("all_expenses", all_expenses))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
