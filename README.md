Привет!
Парсер вакансий hh.ru
Расскажу вкратце как это работает
Для запуска необходима tkinter, если вы на Windows скорее она уже есть в python, на Linux можно
установить: sudo apt install python3-tk
При запуске программа проверяет имеются ли сохраненные данные подключения к базе данных postgres,
при первом запуске их нет поэтому программа предлагает их ввести (в программе не продусмотрено 
подключение без пароля), после заполнения полей программа попросит ввести ключ - его нужно запомнить.
Полученные данные шифруются по протоколу aes (взял здесь https://github.com/Skycker/AES) с использованием
128-битного ключа и храняться в файле в бинарном виде. Ключ введенный на этапе создания этого файла 
необходим при его расшифровке. При последующем подключении программа обнаружит созданный раенее файл 
с данными подключения к базе данных и запросит ключ для его расшифровки.
При первом запуске необходимо наполнить таблицы данными нажав самую левую кнопку. Парсинг hh.ru занимает 
некоторое время. После этого можно нажимать остальные кнопки формируя запросы к базе данных.
