from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio, os, sys, time, re

chatIds = set()

class MyHandler(FileSystemEventHandler):
    bot = None
    
    def __init__(self, bot):
        self.bot = bot 

    def on_created(self, event):
        print("on_created", event.src_path)
        path = event.src_path.strip()
        artist = os.path.dirname(path).split("/")[-1]
        v_title = os.path.split(path)[1].split('.')[0]
        if (path.__contains__(".mp3") and not path.__contains__(".temp.")):
            try:
                files = os.listdir(path)
                regex = re.compile(".*\.mp4")
                while (len(list(filter(regex.match, files))) > 0):
                    print('mp3 file not finished till mp4 exists. Sleeping 10s')
                    time.sleep(10)
                mp3 = open(path, "rb")
                tasks = []
                for id in chatIds:
                    print ("start sending to " + str(id))
                    asyncio.new_event_loop().run_until_complete(send(id, mp3, artist, v_title))
                    print("finished sending to " + str(id))
            except Exception as e:
                print("Exception in preperation\n" + str(e))
        else:
            print("passing")
                
    
async def send(id, mp3, artist, v_title):
    try:
        bot = Bot(os.environ['BOT_TOKEN'])
        await bot.send_audio(id, mp3, performer=artist, title=v_title, caption="#"+str(artist))
    except Exception as e:
        print("Exception occured for " + str(artist) + " " + str(v_title) + "\n" + str(e))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chatId = update.message.chat.id
    chatIds.add(chatId)
    print("adding chat id " + str(chatId))
    await update.message.reply_text(
        rf"This chat will now recive podcasts"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("This bot uploads Podcasts to this channel if started")


def main():
    print("Starting telempup")
    upload_path = "."
    if (len(sys.argv) > 1):
        upload_path = sys.argv[1]
    print("looking in " + str(upload_path))

    bot = Bot(os.environ['BOT_TOKEN'])
    if not bot:
        print("A bot token must be given in the environment as BOT_TOKEN")
        sys.exit()
    application = Application.builder().bot(bot).build()
    
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    event_handler = MyHandler(bot) 
    observer = PollingObserver()
    observer.schedule(event_handler, path=upload_path, recursive=True)
    observer.start()

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()




