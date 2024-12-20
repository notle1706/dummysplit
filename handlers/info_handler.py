from telegram import Update
from telegram.ext import ContextTypes
from utils import get_group_members, load_debts
import os
import json

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    members = get_group_members(chat_id)
    expense_file = f"./data/{chat_id}/debts.json"

    expense = load_debts(expense_file)

    if expense == []:
        await update.message.reply_text("All settled up!")
    else:
        expense_text = "\n".join([f"*{exp[1]}* _owes_ *{exp[0]}:* _{exp[2]}_" for exp in expense])
        await update.message.reply_text(f"*Current status:*\n{expense_text}", parse_mode="Markdown")

async def all_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    file_path = f"./data/{chat_id}/expenses.json"

    if not os.path.exists(file_path):
        await update.message.reply_text("No expenses have been recorded yet.")
        return

    try:
        # Read and parse the JSON file
        with open(file_path, 'r') as file:
            expenses = json.load(file)

        if not expenses:
            await update.message.reply_text("No expenses have been recorded yet.")
            return

        # Generate the message
        message = "*All Recorded Expenses:*\n\n"
        for i, expense in enumerate(expenses, start=1):
            message += (
                f"{i}. {expense['date']}\n"
                f"*Description:* {expense['description']}\n"
                f"*Payer:* {expense['payer']}\n"
                f"*Amount:* {expense['amount']}\n"
                f"*Debts:* \n{expense['debts']}\n\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"An error occurred while reading expenses: {e}")