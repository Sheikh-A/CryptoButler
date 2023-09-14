# CryptoButler
Telegram CRM bot

CryptoButler is meant to keep track of people you have met over TG (like at a conference or event). Anytime you meet someone at a conference and create a telegram chat, you can fwd their the message to the bot. The bot will then kick off a series of questions for you to fill out, and after that it generates a CSV. As you meet more and more people the CSV stores that info. Fields: Date, Username, Company, Where you met, Description, Priority. All the fields are optional and you csn skip them if you want.

Its pretty lightwieght and csv refreshes every 24hrs or so, since data is not stored in any database.


CryptoButler
🤖 How to Use This Bot 🤖

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
    - /start: Start the bot instructions.
    - /manual: Manually add an account.
    - /generatecsv: Generate a CSV of your data
    - /clearcsv: Clear data in your CSV, CAUTION: IRREVERSIBLE
    - /display: Display a grid of all your data (truncated)
    - /howtouse: Start the bot instructions.

    🌐 High-Level Explanation: 🌐
    This bot is designed to serve as a quick Telegram CRM for Crypto Conferences, Events, or workflow. It can help you track multiple interactions at events and generates a CSV that you can use.
