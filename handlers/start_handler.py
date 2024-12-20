from telegram import Update
from telegram.ext import ContextTypes
from config import group_members

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    print(f"Received /join command in chat {chat_id} from {user.username}")

    if chat_id not in group_members:
        group_members[chat_id] = set()  # Initialize a set for unique members

    # Add the user to the group members set
    group_members[chat_id].add(user.username) if user.username else user.firstname
    print(f"Members in chat {chat_id}: {group_members[chat_id]}")
    tag = f"@{user.username}" if user.username else user.first_name
    await update.message.reply_text(
        f"Welcome to DummySplit Bot, {tag}!\n"
        f"You've been added to the expense tracker\n"
        f"Use /add to add an expense.\n"
        f"Use /status to view current debts.\n"
        f"Use /all_expenses to view all expenses."
    )
