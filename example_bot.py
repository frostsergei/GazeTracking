"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""

import cv2
import numpy as np
from skimage import io
from gaze_tracking import GazeTracking

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

gaze = GazeTracking()

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text('Привет, ' + user.username + '!')
    help_command(update, context)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Я отслеживаю зрачки на фотографиях и определяю направления взгляда. Протестируйте меня :)\n\n/help - вывод справки\n/echo - пинг\n\nОтправьте мне ссылки на картинки, которые хотите обработать, или просто отправьте изображения.')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def process_frame(frame):
     gaze.refresh(frame)

     frame = gaze.annotated_frame()
     text = ""

     if gaze.is_blinking():
          text = "Blinking"
     elif gaze.is_right():
          text = "Looking right"
     elif gaze.is_left():
          text = "Looking left"
     elif gaze.is_up():
          text = "Looking up"
     elif gaze.is_up():
          text = "Looking down"
     elif gaze.is_up_right():
          text = "Looking up and right"
     elif gaze.is_up_left():
          text = "Looking up and left"
     elif gaze.is_down_right():
          text = "Looking down and right"
     elif gaze.is_down_left():
          text = "Looking down and left"
     elif gaze.is_center():
          text = "Looking center"

     cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

     left_pupil = gaze.pupil_left_coords()
     right_pupil = gaze.pupil_right_coords()
     cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
     cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

     return frame

def photo_processor(update: Update, context: CallbackContext) -> None:
     if len(update.message.photo) > 0:
          file_id = update.message.photo[-1]
          file = context.bot.getFile(file_id)
          file.download('in.jpg')

          frame = cv2.imread('in.jpg')

          frame = process_frame(frame)
          cv2.imwrite('out.jpg', frame)
          update.message.reply_photo(photo = open('out.jpg', 'rb'));
     else:
          lnk = update.message.text.replace('\n','').split(' ')
          lnk[:] = [x for x in lnk if x]
          if len(lnk) == 0:
               update.message.reply_text('Ничего не подано для обработки')
          else:
               for link in lnk:
                    update.message.reply_photo(photo = link);

                    frame = io.imread(link)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    frame = process_frame(frame)

                    cv2.imwrite('out.jpg', frame)
                    update.message.reply_photo(photo = open('out.jpg', 'rb'))

ft = open(".env", "r")
token = ft.readline()
ft.close()

updater = Updater(token)

dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("echo", echo))

dispatcher.add_handler(MessageHandler(~Filters.command, photo_processor))

updater.start_polling()
updater.idle()
