> Бот создан специально для Codemasters Code Cup 2023

### Установка.

1. Установка репозитория. <br />
<code>git clone https://notabug.org/vovan533/codecup_bot.git & cd codecup_bot</code>
2. Создание виртуального окружения. <br />
<code>python -m venv venv</code>
3. Установка зависимостей. <br />
<code>pip install -r requirements.txt</code>
4. Установка переменных окружения. <br />
необходимо создать файл .env и заполнить его по примеру ниже. <br />
<code>TOKEN=токен телеграм бота <br />
DB_NAME=имя бд <br />
DB_USER=юзер бд <br />
DB_PASSWORD=пароль юзера бд <br />
DB_HOST=хост бд <br />
ADMINS=айди админов в телеграме (через ,)
</code>
5. Создание папки для логов и аватарок. <br />
<code>mkdir logs & mkdir data/img/personal</code>
6. Копирование файла .service. <br />
<code>cp bot.service /etc/systemd/system/bot.service</code>
7. В файле /etc/systemd/system/bot.service отредактируйте пути до бота.
8. Настройка автозапуска. <br />
<code>systemctl enable --now bot.service</code>