from dotenv import load_dotenv
import os

load_dotenv()
API_BOT_TOKEN = os.getenv('API_KEY')

# Conversation states
DESCRIPTION, PAYER, AMOUNT, SPLIT, SELECT_MEMBERS, UNEQUAL_SPLIT = range(6)

group_members = {}
