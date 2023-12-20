import telebot
import json
from random import randint
import os
image_url = ""
text_image = ""
status = False
status_delete = False
# Запускаю бота в телеграме
bot = telebot.TeleBot('6673545734:AAFdjeDQzWq9jVcrMLZWAvSLLLCQ1HOusCY')
# боту нужно скинуть картинку, которую он сохранит в папку image и отправит в ответ пользователю

# при запуске бота, отобразить инлайн кнопки, удалить изображение или загрузить новое
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Удалить изображение', callback_data='delete'),
        telebot.types.InlineKeyboardButton('Загрузить новое', callback_data='upload')
    )
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=keyboard)


# создать call back кнопки, удалить изображение или загрузить новое
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global status_delete  # глобальная переменная, которая будет использоваться внутри функции

    with open('images.json', 'r') as file:
        data_img = json.loads(file.read())

    if call.data == 'delete':
        global status_delete # глобальная переменная, которая будет использоваться внутри функции
        status_delete = True # меняю статус на True
        # показать все изображения и тексты функцией show и спросить какой номер удалить
        show(call.message)

    if call.data in [str(i+1) for i in range(len(data_img))]: # если пользователь выбрал номер изображения
        # удалить изображение и текст из json файла
        del data_img[int(call.data)-1]
        # открываю json файл на запись image.json который находится в папке static и записываю в него новое содержимое
        with open('images.json', 'w',encoding="utf-8") as file:
            file.write(json.dumps(data_img, indent=4, ensure_ascii=True))

        bot.send_message(call.message.chat.id, 'Изображение удалено')
        print("Удалено изображение")
        status_delete = False # меняю статус на False




    if call.data == 'upload':
        bot.send_message(call.message.chat.id, 'Загрузите новое изображение')
        bot.register_next_step_handler(call.message, handle_docs_photo)

# что картинка сохранена и попросит написать содержимое текста
@bot.message_handler(content_types=['photo']) # обрабатываю сообщение с типом фото
def handle_docs_photo(message):
    global image_url, text_image # глобальные переменные, которые будут использоваться внутри функции
    image_url,text_image = "", "" # обнуляю переменные

    try: # пытаюсь выполнить код внутри try
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id) # получаю информацию о файле
        downloaded_file = bot.download_file(file_info.file_path) # скачиваю файл

        # получить текущий путь директории
        file_image = f'{os.getcwd()}\image' # указываю путь куда сохранять файл
        rand_numbers = str(randint(1,2**8)) # генерирую случайное число
        src = file_image + "/img_"+rand_numbers+".jpg"; # указываю путь куда сохранять файл
        with open(src, 'wb') as new_file: # открываю файл на запись
            new_file.write(downloaded_file) # записываю в него скачанный файл

        bot.reply_to(message, "Файл сохранён, теперь введите текст") # отправляю сообщение пользователю
        image_url = "image/img_"+rand_numbers+".jpg" # сохраняю путь к картинке
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
        with open('images.json', 'r') as file:
            data_img = json.loads(file.read())

        # добавляю в json файл новую картинку и текст
        data_img.append(
            { "src":image_url,
              "alt": f"Description of the image {image_url[18:-4]}",
              "description": text_image})

        # открываю json файл на запись image.json который находится в папке static и записываю в него новое содержимое
        with open('images.json', 'w',encoding="utf-8") as file:
            file.write(json.dumps(data_img, indent=4, ensure_ascii=True))
            print("загрузить новое изображение")



    else: # если длина текста больше 40 символов или пустой
        bot.reply_to(message, "Текст больше 40 символов или пустой") # отправляю сообщение пользователю
    global status  # глобальная переменная, которая будет использоваться внутри функции
    status = False

# Вывести все изображения и тексты из json файла и пронумеровать их
@bot.message_handler(commands=['show'])
def show(message):
    if status_delete == True: # если пользователь хочет удалить изображение
        with open('images.json', 'r') as file:
            data_img = json.loads(file.read())
        for i in range(len(data_img)):
            bot.send_message(message.chat.id, f"{i+1}. {data_img[i]['description']}")
            bot.send_photo(message.chat.id, photo=open(data_img[i]['src'], 'rb'))
        # создать инлайн кнопки ровно столько сколько изображений в json файле
        keyboard = telebot.types.InlineKeyboardMarkup()
        # генератором создаю кнопки
        keyboard.add(*[telebot.types.InlineKeyboardButton(text=f"{i+1}", callback_data=f"{i+1}") for i in range(len(data_img))])
        bot.send_message(message.chat.id, 'Выберите номер изображения:', reply_markup=keyboard)




if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)


