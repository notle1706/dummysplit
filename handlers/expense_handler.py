from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, PAYER, AMOUNT, SPLIT, SELECT_MEMBERS, UNEQUAL_SPLIT, group_members
from utils import get_group_members, toggle_member_selection, store_debts, package_and_store_expense

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    members = get_group_members(chat_id)

    if not members:
        await update.message.reply_text("No members found. Ask members to use /join first.")
        return ConversationHandler.END

    # Initialize selected members to include all members at the start of a new expense
    context.user_data['selected_members'] = members
    await update.message.reply_text("What’s the description of the expense?")
    return DESCRIPTION

async def collect_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    members = get_group_members(chat_id)
    context.user_data["description"] = update.message.text

    keyboard = [
        [InlineKeyboardButton(f"{member}", callback_data=f"payer_{member}")] for member in members
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Who paid for this expense?", reply_markup=reply_markup)

    return PAYER


async def select_payer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    members = get_group_members(chat_id)
    
    # Store the split type in context
    payer = query.data.split("_")[1]
    context.user_data['payer'] = payer
    await query.edit_message_text(f"Payer selected: {payer}. How much did it cost?")
    return AMOUNT

async def collect_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["amount"] = round(float(update.message.text), 2)
        keyboard = [
            [InlineKeyboardButton("Equal", callback_data="equal")],
            [InlineKeyboardButton("Unequal", callback_data="unequal")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Is it an equal split?", reply_markup=reply_markup)
        return SPLIT
    except ValueError:
        await update.message.reply_text("Please enter a valid number for the amount.")
        return AMOUNT

async def handle_split(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    members = get_group_members(chat_id)
    
    # Store the split type in context
    context.user_data['split_type'] = query.data  # 'equal' or 'unequal'

    selected_members = context.user_data.get("selected_members", members.copy())
    context.user_data["selected_members"] = selected_members

    keyboard = [
        [InlineKeyboardButton(f"{member} ✅", callback_data=f"toggle_{member}")] for member in members
    ] + [[InlineKeyboardButton("Done", callback_data="done")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select members involved in the expense:", reply_markup=reply_markup)
    return SELECT_MEMBERS

async def select_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    selected_members = context.user_data['selected_members']
    members = get_group_members(chat_id)

    # Handle member toggling
    if query.data.startswith("toggle_"):
        member = query.data.split("_")[1]
        toggle_member_selection(selected_members, member)

        # Update the inline keyboard to reflect current selections
        keyboard = [
            [InlineKeyboardButton(
                f"{member} {'✅' if member in selected_members else ''}",
                callback_data=f"toggle_{member}"
            )] for member in members
        ] + [[InlineKeyboardButton("Done", callback_data="done")]]  # Add "Done" button

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select members involved in the expense:", reply_markup=reply_markup)

    # Handle completion when "Done" is clicked
    elif query.data == "done":
        if not selected_members:
            await query.edit_message_text("No members selected. Please select members.")
            return SELECT_MEMBERS

        context.user_data['selected_members'] = selected_members  # Save selected members

        if context.user_data.get('split_type') == 'equal':
            # Handle the equal split scenario
            selected_members = context.user_data.get('selected_members', [])
            payer = context.user_data.get('payer', "")
            
            amount = context.user_data.get('amount', 0)
            num_members = len(selected_members)

            # Calculate the share per member
            share_per_member = round(amount / num_members, 2)

            # Create the expense list
            expense = []
            for member in selected_members:
                if member != payer:
                    expense.append([payer, member, share_per_member])

            # Display the generated expense list
            expense_text = "\n".join([f"*{exp[1]}* _owes_ *{exp[0]}*: *{exp[2]}*" for exp in expense])
            await query.edit_message_text(f"*Expense split:*\n{expense_text}", parse_mode="Markdown")

            expense_text = "\n".join([f"*{exp[1]}:* _{exp[2]}_" for exp in expense])
            await package_and_store_expense(chat_id, context.user_data["description"], payer, amount, expense_text)

            # End the conversation after processing the expense
            await store_debts(expense, chat_id)

        # Check if unequal split was chosen
        if context.user_data.get('split_type') == 'unequal':
            member_list = "\n".join(selected_members)
            await query.edit_message_text(
                f"Please enter the share for each member (in order) as separate lines:\n\n{member_list}"
            )
            return UNEQUAL_SPLIT

        return ConversationHandler.END

async def collect_unequal_split(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        # Parse user input
        input_text = update.message.text.strip()
        shares = [float(share.strip()) for share in input_text.split("\n")]
        total_amount = context.user_data['amount']

        # Validate the number of shares matches the selected members
        selected_members = context.user_data['selected_members']
        if len(shares) != len(selected_members):
            await update.message.reply_text(
                f"Number of shares doesn't match the number of members. Please provide exactly {len(selected_members)} shares."
            )
            return UNEQUAL_SPLIT

        if sum(shares) != total_amount:
            await update.message.reply_text(
                f"The shares do not add up to the total amount ({total_amount}). Please try again."
            )
            return UNEQUAL_SPLIT

        # Map shares to members
        context.user_data['shares'] = dict(zip(selected_members, shares))
        payer = context.user_data['payer']

        expense = []
        for member in selected_members:
            if member != payer:
                expense.append([payer, member, context.user_data['shares'][member]])

        # Display the result
        expense_text = "\n".join([f"*{exp[1]}* _owes_ *{exp[0]}*: *{exp[2]}*" for exp in expense])
        await update.message.reply_text(f"*Expense split:*\n{expense_text}", parse_mode="Markdown")

        expense_text = "\n".join([f"*{exp[1]}:* _{exp[2]}_" for exp in expense])
        await package_and_store_expense(chat_id, context.user_data["description"], payer, total_amount, expense_text)
        await store_debts(expense, chat_id)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "Please enter valid numbers for the shares, with each share on a new line."
        )
        return UNEQUAL_SPLIT
