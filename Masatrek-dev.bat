@echo off
set /P ip="ENTER SERVER IP ADDRESS : "
cd FaceRecTA
python manage.py runserver --insecure %ip%:80
pause