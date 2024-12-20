import json
import os
from datetime import datetime

def get_group_members(chat_id):
    from config import group_members
    return list(group_members.get(chat_id, []))

def toggle_member_selection(selected_members, member):
    if member in selected_members:
        selected_members.remove(member)
    else:
        selected_members.append(member)

def simplify_debts(debts):
    # Calculate balances for each person
    balances = {}
    for lender, borrower, amount in debts:
        balances[lender] = balances.get(lender, 0) + amount
        balances[borrower] = balances.get(borrower, 0) - amount

    # Lists of people who owe money (debtor) and who are owed money (creditor)
    debtors = []
    creditors = []
    
    for person, balance in balances.items():
        if balance < 0:
            debtors.append((person, abs(balance)))  # Owe money
        elif balance > 0:
            creditors.append((person, balance))  # Is owed money

    # Simplify the debts
    simplified_debts = []
    
    while debtors and creditors:
        debtor, debt_amount = debtors.pop()
        creditor, credit_amount = creditors.pop()
        
        transfer_amount = min(debt_amount, credit_amount)
        simplified_debts.append((creditor, debtor, transfer_amount))
        
        if debt_amount > credit_amount:
            debtors.append((debtor, debt_amount - transfer_amount))
        elif credit_amount > debt_amount:
            creditors.append((creditor, credit_amount - transfer_amount))


    return simplified_debts

# Function to load debts from a JSON file
def load_debts(json_file):
    try:
        with open(json_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # If the file does not exist or is empty, return an empty list

# Function to save debts to a JSON file
def save_debts(debts, json_file):
    with open(json_file, 'w') as file:
        json.dump(debts, file, indent=4)

# Function to add a new expense and update the debt
async def store_debts(expense_details, chat_id):
    file_path = f'./data/{chat_id}/debts.json'

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
    # Create the file by opening it in write mode
        with open(file_path, 'w') as file:
        # Initialize an empty list or any structure you want
            file.write('[]')  # You can start with an empty list in the file\


    debts = load_debts(file_path)    
    
    # Add new debt to the list (for now, we assume expense_details is in the format: (debtor, creditor, amount))
    debts.extend(expense_details)

    # Simplify the debts
    simplified_debts = simplify_debts(debts)
    
    # Save the simplified debts to the JSON file
    save_debts(simplified_debts, file_path)

def store_expense(expense_details, chat_id):
    # File path to store expenses
    file_path = f"./data/{chat_id}/expenses.json"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Read existing expenses or initialize a new list
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            expenses = json.load(file)
    else:
        expenses = []

    # Append the new expense
    expenses.append(expense_details)

    # Write back to the file
    with open(file_path, 'w') as file:
        json.dump(expenses, file, indent=4)

async def package_and_store_expense(chat_id, description, payer, amount, debts):
    expense_details = {
        "date": f"*{datetime.now().strftime('%d-%m-%Y')}*",
        "description": description,
        "payer": payer,
        "amount": amount,
        "debts": debts
    }
    store_expense(expense_details, chat_id)

