Подключитесь к серверу  
Создайте SuperUser  
Обновите пакет репозиториев (команда терминала: sudo apt update)  
Обновите пакетный менеджер  (команда терминала: sudo apt upgrade)  
Установите виртуально окружение (команда терминала: sudo apt install python3-venv)  
Установите Python3-pip (команда терминала: sudo apt install python3-pip)  
Установите postgresql (команда терминала: sudo apt install postgresql)  
Проверте статус postgresql (команда терминала: systemctl status postgresql) при           необходимости запустите командой: sudo systemctl postgresql  
Копируйте HTTPS ссылку репозитория git и клонируйте репозиторий (git clone //ссылка//)  
Войдите в папку проекта и перейдите в ветку проекта (cd //папка//, git checkout main)  
Cоздайте виртуальное окружение в папке проекта (python3 -m venv env)  
Активируйте виртуальное окружение (source env/bin/activate)  
Установите зависимости (pip install -r requirements.txt) проверка зависимостей          (pip freeze)  
Перейдите к пользователю postgres (sudo su postrges)  
Перейдите к psql  
Создайте пользователя базы данных ( CREATE USER //имя пользователя// WITH SUPERUSER;)  
Установите пароль пользователя базы данных ( ALTER USER //имя пользователя// WITH PASSWORD 'пароль';)  
Создайте базу данных для нового пользователя( CREATE DATABASE //название базы данных//;)
Выйдете из psql (/q)  и пользователя postrges(exit)  
Перейдите к psql   
Создайте базу данных для проекта( CREATE DATABASE //название базы данных//)  
Выйдете из psql (/q)  
Настройте переменные окружения в файле .env  
Выполните миграции (python manage.py migrate)  
Активируйте WSGI сервер(GUNICORN) (gunicorn <пакет с файлом wsgi>.wsgi -b 0.0.0.0:8000)  
Создайте сервисный файл GUNICORN (sudo nano /etc/systemd/system/gunicorn.service)  

Заполните сервисный файл:  
[Unit]  
Description=gunicorn service  
After=network.target  
[Service]  
User=root  
Group=www-data   
workingDirectory=/home/<имя пользовотеля>/<папка с проектом>   
ExecStart=/home/<имя пользовотеля>/<папка с проектом>/env/bin/gunicorn \  
 --access-logfile - \  
 --worker=1 \
 -bind unix:/home/<имя пользовотеля>/<папка с проектом>/mfc/project.sock \  
 mfc.wsgi:application  
[Install]  
wantedBy=multi-user.target  

Создайте файл настроек nginx: sudo nano /<папка с проектом>/etc/nginx/sites-avilable/mfc  
Зaполните файл настроек nginx:  

server {  
    listen 80;  
    server_name your_domain.com www.your_domain.com;  
        
    
    # Обработка медиа файлов Django  
    location /media/ {  
        alias /home/backend/media/;    
    }
    # Обработка Root URL для React  
    location / {  
        root /home/frontend/build;    
        try_files $uri $uri/ /index.html;  
    }
    # Проксирование API запросов
    location /api/ {   
        proxy_pass http://unix:/home/backend/myproject.sock;    
        proxy_set_header Host $host;  
        proxy_set_header X-Real-IP $remote_addr;  
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  
    }  
}  

Создаем символическую ссылку:  
sudo ln -s /etc/nginx/sites-available/mfc /etc/mginx/sites-enabled  

Перезапускаем nginx:    
sudo service nginx restart    
