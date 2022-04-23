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
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def null_command(update: Update, context: CallbackContext) -> None:
     update.message.reply_text('Команда не найдена')

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

def link(update: Update, context: CallbackContext) -> None:
     lnk = update.message.text.split(' ')
     if len(lnk) == 1:
          update.message.reply_text('Ссылки нет')
     else:
          update.message.reply_photo(photo = lnk[1]);

          frame = io.imread(lnk[1])
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          
          frame = process_frame(frame)

          cv2.imwrite('out.jpg', frame)
          update.message.reply_photo(photo = open('out.jpg', 'rb'))

def photo_processor(update: Update, context: CallbackContext) -> None:
     file_id = update.message.photo[-1]
     file = context.bot.getFile(file_id)
     file.download('in.jpg')

     frame = cv2.imread('in.jpg')

     frame = process_frame(frame)
     cv2.imwrite('out.jpg', frame)
     update.message.reply_photo(photo = open('out.jpg', 'rb'));


ft = open(".env", "r")
token = ft.readline()
ft.close()

updater = Updater(token)

dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("link", link))
dispatcher.add_handler(CommandHandler("echo", echo))

dispatcher.add_handler(MessageHandler(~Filters.command, photo_processor))

updater.start_polling()
updater.idle()
