# Reminder Bot

The Reminder Bot is a Telegram bot that helps users stay organized by allowing them to send natural language messages and reminders. The bot parses user messages to extract important information such as event dates and names, stores them in a database, and sends reminders to users at scheduled times.

## Features

- **Natural Language Parsing:** The bot uses ChatGPT to parse user messages and extract relevant information about events, such as subject, dates, types and etc.

- **Database Storage:** The extracted event information is stored in a SQLite database, allowing for efficient retrieval and management of reminders.

- **Scheduled Scans:** The bot automatically scans the database at a scheduled time, typically 9 AM IL time ( can be adjust for local use) , to identify upcoming events. It sends reminders to users three days in advance as well as on the event day.

