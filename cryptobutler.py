import os
from dotenv import load_dotenv
import csv
import logging
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from datetime import datetime

load_dotenv()

TOKEN = os.getenv('TOKEN')
# Create a logger

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the different states of the conversation
ASK_COMPANY, ASK_MEETING_PLACE, ASK_DESCRIPTION, ASK_PRIORITY = range(4)
ASK_MANUAL_USERNAME, ASK_MANUAL_DESCRIPTION, ASK_MANUAL_COMPANY, ASK_MANUAL_MEETING_PLACE, ASK_MANUAL_PRIORITY = range(4, 9)

# Store interactions in a dictionary with user ID as the key
chat_log = {}

# Store the current interaction for a user
current_interaction = {}

def how_to_use(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /howtouse is issued."""
    help_text = """
    🤖 *How to Use This Bot* 🤖

    You can use this bot in two ways:
    1. Forward a message from a chat to the CryptoButler bot directly. The sequence should start right after you share the fwd message. The message should not be from you, otherwise it will just log your username.
    2. Manually add an account using the manual command
    3. These are the datapoints that you can add in:
        date: Auto
        chatname: Auto (unless manual)
        username: Auto (unless manual)
        description: User Input
        company: User Input
        meetingplace: User Input	
        priority: User Input

    4. After any interaction (whether forwarding a message or manually typing it in) a CSV is generated. This is because data will not be stored in any database, and will clear every 24 hours or so. To avoid losing your data, the CSV is generated after every interaction, in case the data clears. 
    5. This bot is in beta

    Here's a list of available commands:
    - `/start`: Start the bot instructions.
    - `/manual`: Manually add an account.
    - `/generatecsv`: Generate a CSV of your data
    - `/clearcsv`: Clear data in your CSV, CAUTION: IRREVERSIBLE
    - `/display`: Display a grid of all your data (truncated)
    - `/howtouse`: Start the bot instructions.

    🌐 *High-Level Explanation*: 🌐
    This bot is designed to serve as a quick Telegram CRM for Crypto Conferences, Events, or workflow. It can help you track multiple interactions at events and generates a CSV that you can use.
    """
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Forward a message to log it or use /manual to manually add data.')
    return ConversationHandler.END

def stray_command(update: Update, context: CallbackContext) -> int:
    """Inform user about stray command and ask to continue or cancel."""
    update.message.reply_text(
        "It seems you've entered a command. Would you like to continue with the current operation or /cancel to stop?")
    return ConversationHandler.END  # You can return the state you want or END if you want to stop the conversation.

def send_csv(update: Update, context: CallbackContext, user_id: int) -> None:
    """Generate and send the CSV for a specific user."""
    if user_id not in chat_log:
        update.message.reply_text("There's no logged data to generate a CSV for.")
        return

    filename = f"{user_id}_logs.csv"
    
    with open(filename, 'w', newline='') as file:
        # Define the fieldnames (headers)
        fieldnames = ["date", "chat_name", "username", "description", "company", "meeting_place", "priority"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for log in chat_log[user_id]:
            writer.writerow(log)

    with open(filename, 'rb') as file:
        update.message.reply_document(document=file, filename=filename)


def forward_handler(update: Update, context: CallbackContext) -> int:
    """Handle forwarded messages and start logging process."""
    user_id = update.message.from_user.id
    if user_id not in chat_log:
        chat_log[user_id] = []
    global current_interaction
    current_interaction = {
        'date': update.message.forward_date.strftime('%Y-%m-%d'),
        'chat_name': update.message.forward_from_chat.title if update.message.forward_from_chat else "Private Chat",
        'username': update.message.forward_from.username if update.message.forward_from else 'N/A'
    }
    update.message.reply_text("Which company does this person work at? Press 's' and then enter to skip.")
    return ASK_COMPANY

def ask_company(update: Update, context: CallbackContext) -> int:
    """Log company and ask where the user met."""
    current_interaction['company'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Where did you meet? Press 's' and then enter to skip.")
    return ASK_MEETING_PLACE

def ask_meeting_place(update: Update, context: CallbackContext) -> int:
    """Log meeting place and ask for a brief description."""
    current_interaction['meeting_place'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Brief description (optional)? Press 's' and then enter to skip.")
    return ASK_DESCRIPTION

def ask_description(update: Update, context: CallbackContext) -> int:
    """Log description (if provided) and ask for priority."""
    current_interaction['description'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Please set the priority (i.e. 1,2,3). Press 's' and then enter to skip.")
    return ASK_PRIORITY

def manual_entry(update: Update, context: CallbackContext) -> int:
    """Start the manual data input process."""
    update.message.reply_text("Please enter the username. (Type 's' and then enter to skip)")
    return ASK_MANUAL_USERNAME

def ask_manual_username(update: Update, context: CallbackContext) -> int:
    """Log username and ask for description."""
    global current_interaction
    current_interaction['date'] = datetime.now().strftime('%Y-%m-%d')
    current_interaction['chat_name'] = ''
    current_interaction['username'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Please enter a description. (Type 's' and then enter to skip)")
    return ASK_MANUAL_DESCRIPTION

def ask_manual_description(update: Update, context: CallbackContext) -> int:
    """Log description and ask for company."""
    current_interaction['description'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Which company does this person work at? (Type 's' and then enter to skip)")
    return ASK_MANUAL_COMPANY

def ask_manual_company(update: Update, context: CallbackContext) -> int:
    """Log company and ask where the user met."""
    current_interaction['company'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Where did you meet? (Type 's' and then enter to skip)")
    return ASK_MANUAL_MEETING_PLACE

def ask_manual_meeting_place(update: Update, context: CallbackContext) -> int:
    """Log meeting place and ask for priority."""
    current_interaction['meeting_place'] = update.message.text.strip() if update.message.text != 's' else ''
    update.message.reply_text("Please set the priority (i.e. 1,2,3). (Type 's' and then enter to skip)")
    return ASK_MANUAL_PRIORITY

def finalize_manual_interaction(update: Update, context: CallbackContext) -> None:
    """Log priority and finalize interaction."""
    user_id = update.message.from_user.id
    if user_id not in chat_log:
        chat_log[user_id] = []
    current_interaction['priority'] = update.message.text.strip() if update.message.text != 's' else ''
    chat_log[user_id].append(current_interaction.copy())
    update.message.reply_text("Data manually logged successfully!")
    current_interaction.clear()
    send_csv(update, context, user_id)
    return ConversationHandler.END


def finalize_interaction(update: Update, context: CallbackContext) -> None:
    """Log priority and finalize interaction."""
    user_id = update.message.from_user.id
    current_interaction['priority'] = update.message.text.strip() if update.message.text != 's' else ''
    chat_log[user_id].append(current_interaction.copy())
    update.message.reply_text("Logged successfully! Forward another chat or use /generateCSV to get your interactions.")
    current_interaction.clear()
    send_csv(update, context, user_id)
    return ConversationHandler.END

def display_data(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    
    # Check if the user has logged any data
    if user_id not in chat_log or not chat_log[user_id]:
        update.message.reply_text("You don't have any logged data to display.")
        return
    
    # Header for the table
    header = "| {date:^10} | {chat:^10} | {handle:^10} | {company:^10} | {place:^10} | {priority:^2} |".format(
        date="date", chat="chat", handle="handle", company="company", place="place", priority="priority"
    )
    
    # Divider for the table
    divider = "-" * len(header)
    
    # Create table rows for each log entry
    rows = []
    for log in chat_log[user_id]:
        # Rename the keys
        log_renamed = {
            'date': log['date'],
            'chat': log['chat_name'][:10],  # truncate if necessary
            'handle': log['username'][:10],  # truncate if necessary
            'company': log['company'][:10],  # truncate if necessary
            'place': log['meeting_place'][:10],  # truncate if necessary
            'priority': log['priority'][:2]
        }
        row = "| {date:^10} | {chat:^10} | {handle:^10} | {company:^10} | {place:^10} | {priority:^2} |".format(**log_renamed)
        rows.append(row)

    # Combine header, divider, and rows to form the table
    table = "\n".join([divider, header, divider] + rows + [divider])
    
    update.message.reply_text(table, parse_mode='Markdown')


def generate_csv(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    
    # Check if the user_id exists in chat_log
    if user_id not in chat_log:
        update.message.reply_text("You don't have any logged data to generate a CSV for.")
        return

    filename = f"{user_id}_logs.csv"
    
    with open(filename, 'w', newline='') as file:
        # Define the fieldnames (headers)
        fieldnames = ["date", "chat_name", "username", "description", "company", "meeting_place", "priority"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for log in chat_log[user_id]:
            writer.writerow(log)

    with open(filename, 'rb') as file:
        update.message.reply_document(document=file, filename=filename)

def clear_csv(update: Update, context: CallbackContext) -> None:
    """Clear CSV data without confirmation."""
    user_id = update.message.from_user.id
    
    if user_id in chat_log:
        del chat_log[user_id]
        update.message.reply_text("Your CSV data has been cleared.")
    else:
        update.message.reply_text("You don't have any logged data to clear.")


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the current conversation and send a message."""
    update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def error_callback(update: Update, context: CallbackContext) -> None:
    """Log unexpected errors."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with states
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('clearCSV', clear_csv),
                      MessageHandler(Filters.forwarded, forward_handler),
                      CommandHandler('manual', manual_entry)],
        states={
            ASK_COMPANY: [MessageHandler(Filters.text & ~Filters.command, ask_company)],
            ASK_MEETING_PLACE: [MessageHandler(Filters.text & ~Filters.command, ask_meeting_place)],
            ASK_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, ask_description)],
            ASK_PRIORITY: [MessageHandler(Filters.text & ~Filters.command, finalize_interaction)],
            ASK_MANUAL_USERNAME: [MessageHandler(Filters.text & ~Filters.command, ask_manual_username)],
            ASK_MANUAL_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, ask_manual_description)],
            ASK_MANUAL_COMPANY: [MessageHandler(Filters.text & ~Filters.command, ask_manual_company)],
            ASK_MANUAL_MEETING_PLACE: [MessageHandler(Filters.text & ~Filters.command, ask_manual_meeting_place)],
            ASK_MANUAL_PRIORITY: [MessageHandler(Filters.text & ~Filters.command, finalize_manual_interaction)]
        },
            fallbacks=[CommandHandler('cancel', lambda update, context: update.message.reply_text("Action cancelled.")), MessageHandler(Filters.command, stray_command)]
    )

    dp.add_handler(conversation_handler)
    dp.add_handler(CommandHandler('generateCSV', generate_csv))
    dp.add_handler(CommandHandler('clearCSV', clear_csv))
    dp.add_handler(CommandHandler('display', display_data))
    dp.add_error_handler(error_callback)
    dp.add_handler(CommandHandler("howtouse", how_to_use))


    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()