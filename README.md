# API-connection-website
# BITO -> POWER BI | SALES TEMPLATE (ENGLISH)

3 STEPS TO GET YOUR DATA:

STEP 1 — ADD YOUR API KEY
Open the .env file
Paste your Bito API key after the = sign
Example: BITO_API_KEY=abc123yourkeyhere
Save the file

STEP 2 — INSTALL REQUIREMENTS
Open terminal in this folder
Run: pip install requests python-dotenv

STEP 3 — RUN THE SCRIPT
Run: python sync_runner.py
A file called sales_data.csv will appear in this folder

CONNECT TO POWER BI:
Open Power BI Desktop
Get Data -> Text/CSV -> select sales_data.csv
Refresh whenever you want updated data

WANT TO REMOVE A COLUMN?
Open sync_runner.py
Find the section marked "EDIT THIS"
Remove the column name from the header row
Remove the matching value from the row below it

QUESTIONS?
Ask your teacher or check the course website

---

# BITO -> POWER BI | SALES TEMPLATE (O'ZBEKCHA)

MA'LUMOTLARNI OLISH UCHUN 3 TA QADAM:

1-QADAM — API KALITINI QO'SHING
.env faylini oching
Bito API kalitingizni = belgisidan keyin joylashtiring
Misol: BITO_API_KEY=abc123yourkeyhere
Faylni saqlang

2-QADAM — TALAB QILINGAN KUTUBXONALARNI O'RNATING
Ushbu papkada terminalni oching
Buyruqni bajaring: pip install requests python-dotenv

3-QADAM — SKRIPTNI ISHGA TUSHIRING
Buyruqni bajaring: python sync_runner.py
Ushbu papkada sales_data.csv nomli fayl paydo bo'ladi

POWER BI GA ULANISH:
Power BI Desktop dasturini oching
Get Data -> Text/CSV -> sales_data.csv faylini tanlang
Ma'lumotlarni yangilamoqchi bo'lsangiz, Refresh tugmasini bosing

USTUNNI O'CHIRISHNI HOXLAYSIZMI?
sync_runner.py faylini oching
"EDIT THIS" deb belgilangan qismni toping
Sarlavha qatoridan ustun nomini olib tashlang
Pastdagi qatordan unga mos keladigan qiymatni olib tashlang

SAVOLLAR BO'LSA?
O'qituvchingizdan so'rang yoki kurs veb-saytini tekshiring

---

# BITO -> POWER BI | SALES TEMPLATE (РУССКИЙ)

3 ШАГА ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ:

ШАГ 1 — ДОБАВЬТЕ ВАШ API КЛЮЧ
Откройте файл .env
Вставьте ваш API ключ Bito после знака =
Пример: BITO_API_KEY=abc123yourkeyhere
Сохраните файл

ШАГ 2 — УСТАНОВИТЕ ЗАВИСИМОСТИ
Откройте терминал в этой папке
Запустите: pip install requests python-dotenv

ШАГ 3 — ЗАПУСТИТЕ СКРИПТ
Запустите: python sync_runner.py
В этой папке появится файл sales_data.csv

ПОДКЛЮЧЕНИЕ К POWER BI:
Откройте Power BI Desktop
Get Data -> Text/CSV -> выберите файл sales_data.csv
Нажимайте Refresh каждый раз, когда нужны обновленные данные

ХОТИТЕ УДАЛИТЬ КОЛОНКУ?
Откройте файл sync_runner.py
Найдите секцию с пометкой "EDIT THIS"
Удалите имя колонки из строки заголовков
Удалите соответствующее значение из строки ниже

ВОПРОСЫ?
Обратитесь к преподавателю или проверьте сайт курса
