import telebot
import json
from random import randint
import os
image_url = ""
text_image = ""
status = False
# Запускаю бота в телеграме
bot = telebot.TeleBot('6673545734:AAFdjeDQzWq9jVcrMLZWAvSLLLCQ1HOusCY')
# боту нужно скинуть картинку, которую он сохранит в папку image и отправит в ответ пользователю
# что картинка сохранена и попросит написать содержимое текста
@bot.message_handler(content_types=['photo']) # обрабатываю сообщение с типом фото
def handle_docs_photo(message):
    global image_url, text_image # глобальные переменные, которые будут использоваться внутри функции
    image_url,text_image = "", "" # обнуляю переменные

    try: # пытаюсь выполнить код внутри try
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id) # получаю информацию о файле
        downloaded_file = bot.download_file(file_info.file_path) # скачиваю файл

        # получить текущий путь директории
        file_image = f'{os.getcwd()}\static\image' # указываю путь куда сохранять файл
        rand_numbers = str(randint(1,2**8)) # генерирую случайное число
        src = file_image + "\img_"+rand_numbers+".jpg"; # указываю путь куда сохранять файл
        with open(src, 'wb') as new_file: # открываю файл на запись
            new_file.write(downloaded_file) # записываю в него скачанный файл

        bot.reply_to(message, "Файл сохранён, теперь введите текст") # отправляю сообщение пользователю
        image_url = "\static\image\img_"+rand_numbers+".jpg" # сохраняю путь к картинке
        global status # глобальная переменная, которая будет использоваться внутри функции
        status = True # меняю статус на True

    except Exception as error: # если внутри try возникла ошибка, то выполняется код внутри except
        bot.reply_to(message, error) # отправляю сообщение пользователю с ошибкой

@bot.message_handler(func=lambda message: status == True, content_types=['text']) # обрабатываю сообщение с типом текст
# получаю текст пользователя и сравниваю не больше ли там 40 символов и не пустой ли он
def put_text(message):
    global image_url, text_image # глобальные переменные, которые будут использоваться внутри функции
    if len(message.text) <= 40 and len(message.text) > 0: # если длина текста не больше 40 символов и не пустой
        text_image = message.text # сохраняю текст
        bot.reply_to(message, "Текст сохранён") # отправляю сообщение пользователю

        # открываю json файл на чтение image.json который находится в папке static и считываю его содержимое
        with open('static/images.json', 'r') as file:
            data_img = json.loads(file.read())

        # добавляю в json файл новую картинку и текст
        data_img.append(
            { "src":image_url,
              "alt": f"Description of the image {image_url[18:-4]}",
              "description": text_image})

        # открываю json файл на запись image.json который находится в папке static и записываю в него новое содержимое
        with open('static/images.json', 'w',encoding="utf-8") as file:
            file.write(json.dumps(data_img, indent=4, ensure_ascii=True))

    else: # если длина текста больше 40 символов или пустой
        bot.reply_to(message, "Текст больше 40 символов или пустой") # отправляю сообщение пользователю
    global status  # глобальная переменная, которая будет использоваться внутри функции
    status = False

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)