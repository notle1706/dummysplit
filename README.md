# Expense Splitter Bot  

A Telegram bot to track and manage group expenses. The bot allows users to add expenses, split them equally or unequally, track debts, and generate a summary of all expenses.

---

## Features
- **Add Expenses**
  - Record an expense with a description, payer, and amount.  
  - Choose to split the expense equally or unequally among selected members.

- **Track Debts**  
  - Automatically calculate and simplify debts for group members.  

- **Expense Summary**  
  - Retrieve a detailed list of all expenses recorded.  

- **Persistence**  
  - All data is saved locally in JSON files. 

---

## Commands
| Command            | Description                                |
|--------------------|--------------------------------------------|
| `/join`            | Register the user to the tracker.          |
| `/add`             | Add a new expense to the tracker.          |
| `/status`          | View simplified debts for the group.       |
| `/all_expenses`    | Generate a summary of all expenses.        |

---
## Requirements

1. Python3 installed with Telegram APIs
2. This project uses `python-dotenv` for environment variables
3. Telegram account and a bot API token from [Botfather](https://t.me/BotFather)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/notle1706/dummysplit.git
   cd dummysplit
   ```
2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Set up environment variables**
   Refer to `example.env` to create a `.env` file
4. **Run the bot**
   ```bash
   python3 main.py
   ```
   And add the bot to the Telegram group.

## Example Usage

1. `/join` to join the expense tracker.
2. Use the `/add` command to add an expense.
3. Provide the description, amount, payer, and split type.
4. Select members involved in the expense.
5. For unequal splits, input the shares in a new-line-separated format.
6. Use the `/status` command to calculate the smallest number of transactions needed to settle debts among members.

## Note

- Since the bot does not have access to messages in the group, users need to reply to the bot in order for the bot to get the messages.
- Bot does not support currencies. Input price as a **number only** instead of symbols and letters.
