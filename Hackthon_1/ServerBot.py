
import logging
from telegram import Update, constants
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
# AI is only in charge of getting output from chatgpt
from AI import parse_user_input
from DateHandling import get_date, get_scheduled_time, daynum_to_string
from Database import insert_data, scan_database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # logging.info(f"message from {update.effective_chat.id}")
    msg_text = "🤖 Welcome to the Reminder Bot\! 📅 \n\nI'm here to help you stay organized and never miss important dates or events\. Whether it's birthdays, anniversaries, or other special occasions, I'll make sure you're well\-prepared\."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg_text,parse_mode=MarkdownV2)


async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, constants.ChatAction.TYPING)

    # This function returns None if it didn't manage to parse the output
    parsed_message = parse_user_input(update.message.text)

    if parsed_message is None:
        output_msg = "I'm sorry, I didn't get that..."
    else:
        parsed_message['date'] = get_date(parsed_message['date'])
        if parsed_message['date'] is None:  # incorrect datetime and "today" is not supported.
            output_msg = "Sorry your date input is incorrect / unsupported. "
        else:
            parsed_message['chat_id'] = update.effective_chat.id
            # store it to database
            insert_data(parsed_message)
            output_msg = "Successfully Saved!"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=output_msg)


async def reminder(context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Calling event...")
    msg_text = "Testing"

    fetched_events: dict = scan_database([1, 2])
    for day in fetched_events.keys():
        for event in fetched_events[day]:
            event_name = event["event"]
            more_info = event["more_info"]
            enumerated = event["enumerated"]
            subject = event["subject"]
            chat_id = event["chat_id"]
            msg_text = f"✨ *Reminder for {daynum_to_string(day).lower()}* ✨\n\n"
            if enumerated == "BIRTHDAY":
                msg_text += f"{subject}'s \*birthday\* is coming\! 🥳🥳🥳\n\n"
                msg_text += f"Don't forget to wish them a _Happy \n\nBirthday_ {daynum_to_string(day).lower()} ❤"
            elif enumerated == "ANNIVERSARY":
                msg_text += f"_{subject}'s \*anniversary\* is coming\! ❤❤❤_\n\n"
                msg_text += f"_💌 Don't forget to prepare something \n\nspecial {daynum_to_string(day).lower()} 💌_\n\n"
                msg_text += f"*Event*: {event}\n\n"
                if (more_info): msg_text += f"*More Info*: {more_info}\n\n"
            elif enumerated == "MONTHLY_REMINDER":
                msg_text += f"_This is your monthly reminder for \.\.\. _\n\n"
                msg_text += f"*Subject*: {subject}\n\n"
                msg_text += f"*Event*: {event}\n\n"
                if (more_info): msg_text += f"*More Info*: {more_info}\n\n"
            else:
                msg_text += f"*Subject*: {subject}\n\n"
                msg_text += f"*Event*: {event}\n\n"
                if (more_info): msg_text += f"*More Info*: {more_info}\n\n"
            await context.bot.send_message(chat_id=chat_id, text=msg_text, parse_mode="MarkdownV2")



if __name__ == '__main__':
    # use fake Telegram bot token for public sharing.
    application = ApplicationBuilder().token('6666666666:AABBCCDDEEFG_ABCD-68687987-11').build()
    # run the callback function daily at 9AM
    application.job_queue.run_daily(reminder, get_scheduled_time())
    start_handler = CommandHandler('start', start)
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chatgpt)
    application.add_handler(start_handler)
    application.add_handler(chat_handler)
    application.run_polling()
