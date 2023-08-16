import logging
import os
from sqlalchemy import update
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from methods.tables import (User,
                            Collocation,
                            connection)
from random import randint


TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

reply_keyboard = [
    ["Add"]
]

help_message = "I support following commands:\n" \
                "/start - start using\n" \
                "/add - add your collocation\n" \
                "/set - for setup reminder\n" \
                "/edit - edit collocation\n" \
                "/list - list all collocations\n" \
                "/schedule_reminder - set schedule of reminds\n" \
                "/stop_reminder - stop reminder\n" \
                "/help - for help"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = connection.query(User.chat_id == update.effective_chat.id).filter_by().all()
    logging.info("users %s", user)
    if user.__len__() == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="So, let's meet! "
                                                                              "What's your name?")
        return 'USER_NAME'
    elif user.__len__() != 0:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=help_message)


async def greeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot for improving "
                                                                          "your english skills! "
                                                                          "If you want to know what I can, "
                                                                          "please type /help")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=help_message)


async def meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('meeting is working now')
    username = update.message.chat.username
    chat_id = update.message.chat.id
    first_name = update.message.text
    user = User()
    user.username = username
    user.chat_id = chat_id
    user.first_name = first_name
    connection.add(user)
    connection.commit()
    connection.close()
    message = f"Hello {first_name}, my name is collocations_bot, " \
              f"nice to meet you! Please input /help for look what can I do."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return 'END'


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Type your phrase")
    return 'PHRASE'

async def add_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    collocation = Collocation()
    collocation.author_id = update.effective_chat.id
    collocation.collocation = update.message.text
    collocation.explanation = 'in progress'
    connection.add(collocation)
    connection.commit()
    connection.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Type translation")
    return 'TRANSLATION'


async def add_transaltion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    collocation = connection.query(Collocation).filter(Collocation.author_id == update.effective_chat.id,
                                   Collocation.explanation == 'in progress')
    collocation[0].explanation = update.message.text
    connection.commit()
    connection.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Got it!")
    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    return ConversationHandler.END


async def phrases_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    collocations = connection.query(Collocation).filter(Collocation.author_id == update.effective_chat.id,
                                                       Collocation.explanation != 'in progress')
    message = ''
    for collocation in collocations:
        message += f"{collocation.collocation} - {collocation.explanation}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def reminder(context: CallbackContext):
    collocations = connection.query(Collocation).filter(Collocation.author_id == context._chat_id,
                                                        Collocation.explanation != 'in progress')
    collocations_list = []
    for collocation in collocations:
        collocations_list.append(f"{collocation.collocation} - {collocation.explanation}")
    await context.bot.send_message(chat_id=context._chat_id,
                                   text=collocations_list[randint(0, len(collocations_list) - 1)])


async def scheduler_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="How do I often remind you collocations?"
                                        " Please type count of reminds, for example 3, "
                                        "It means that I'll "
                                        "remind you 3 times/day.")
    return "REMINDS"



async def remind_sheduler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminds = update.message.text
    chat_id = update.effective_chat.id
    try:
        reminds = int(reminds)
        period = int(144/reminds) * 60
        context._chat_id = chat_id
        context.job_queue.run_repeating(reminder, period, chat_id=chat_id, name=str(chat_id))
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Reminder was set.")
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please type number. Try /shedule_reminder\n"
                                      "another one.")
        return ConversationHandler.END


async def stop_remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        job = context.job_queue.get_jobs_by_name(str(chat_id))
        job[0].schedule_removal()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Reminder stopped")
    except IndexError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Reminder already stopped")


if __name__ == '__main__':
    if TOKEN is None:
        logging.info("TOKEN variable is not specified.")
        exit(1)
    application = Application.builder().token(TOKEN).build()
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_cmd)
    greeting_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), greeting)
    # application.add_handler(greeting_handler)
    application.add_handler(help_handler)

    meeting_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            'USER_NAME': [MessageHandler(filters.TEXT, meeting)]
        },
        fallbacks=[CommandHandler('done', done)]
    )

    collocation_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add)],
        states={
            'PHRASE': [MessageHandler(filters.Regex("^[A-Za-z\-']*$"), add_phrase)],
            'TRANSLATION': [MessageHandler(filters.TEXT, add_transaltion)]
        },
        fallbacks=[CommandHandler('done', done)]
    )
    phrases_list_handler = CommandHandler("list", phrases_list)
    sheduler_handler = ConversationHandler(
        entry_points=[CommandHandler('schedule_reminder', scheduler_cmd)],
        states={
            "REMINDS": [MessageHandler(filters.TEXT, remind_sheduler)]
        },
        fallbacks=[CommandHandler('cancel', done)]
    )

    stop_reminder_handler = CommandHandler('stop_reminder', stop_remind)
    application.add_handler(meeting_handler)
    application.add_handler(collocation_handler)
    application.add_handler(phrases_list_handler)
    application.add_handler(stop_reminder_handler)
    application.add_handler(sheduler_handler)

    application.run_polling()
