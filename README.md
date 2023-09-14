> Бот создан специально для Codemasters Code Cup 2023

### Установка.

1. Установка репозитория.\
<code>git clone https://notabug.org/vovan533/codecup_bot.git & cd codecup_bot</code>
2. Создание виртуального окружения.\
<code>python -m venv venv</code>
3. Установка зависимостей.\
<code>pip install -r requirements.txt</code>
4. Установка переменных окружения.\
необходимо создать файл .env и заполнить его по примеру ниже.\
<code>TOKEN=токен телеграм бота\
DB_NAME=имя бд\
DB_USER=юзер бд\
DB_PASSWORD=пароль юзера бд\
DB_HOST=хост бд\
ADMINS=айди админов в телеграме (через ,)
</code>
5. Создание папки для логов и аватарок.\
<code>mkdir logs & mkdir data/img/personal</code>
6. Копирование файла .service.\
<code>cp bot.service /etc/systemd/system/bot.service</code>
7. В файле /etc/systemd/system/bot.service отредактируйте пути до бота.
8. Настройка автозапуска.\
<code>systemctl enable --now bot.service</code>