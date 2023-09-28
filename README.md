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
<code>TOKEN=токен телеграм бота</code> <br />
<code>DB_NAME=имя бд</code> <br />
<code>DB_USER=юзер бд</code> <br />
<code>DB_PASSWORD=пароль юзера бд</code> <br />
<code>DB_HOST=хост бд</code> <br />
<code>ADMINS=айди админов в телеграме (через ,)
</code>
5. Создание папки для логов и аватарок. <br />
<code>mkdir logs & mkdir data/img/personal</code>
6. Копирование файла .service. <br />
<code>cp bot.service /etc/systemd/system/bot.service</code>
7. В файле /etc/systemd/system/bot.service отредактируйте пути до бота.
8. Настройка автозапуска. <br />
<code>systemctl enable --now bot.service</code>


### Архитектура проекта.
<code><br />
| codecup_bot <br />
|-- data </code> <i>директория файлов</i><code><br />
|   |-- img <br />
|   |--   -- personal <br />
|   |-- other <br />
|-- handlers </code> <i>директория хендлеров бота</i><code><br />
|   |-- keyboards.py </code> <i>клавиатуры пользователей</i><code><br />
|   |-- users.py </code> <i>хендлер ответственный за взаимодействие с пользователями</i><code><br />
|-- logs </code> <i>директория логов</i><code><br />
|-- app.py </code> <i>исполняемый файл</i><code><br />
|-- config.py </code> <i>конфиг файл</i><code><br />
|-- pdb.py </code> <i>файл с методами работы с базой данных</i><code><br />
|-- app.py </code> <i>исполняемый файл</i><code><br />
|-- bot.service </code> <i>systemd сервис</i><code><br />
</code>
