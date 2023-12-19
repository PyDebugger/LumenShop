from flask import Flask, render_template


app = Flask(__name__)

@app.route('/') # начальная страница сайта, открывается при запуске локального сервера
def index(): # функция, которая возвращает содержимое файла index.html
    return render_template('index.html', menu_show=False) # весь визуал сайта содержится в файле index.html

@app.route('/image.json') # позволяю получить доступ к папке содержимое картинок, за счёт его статического метода send_static_file
def serve_json_file(): # функция, которая возвращает содержимое папки image
    return app.send_static_file('static/image')


if __name__ == "__main__":
    app.run(debug=True)