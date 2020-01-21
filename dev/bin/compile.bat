@echo off
call "C:\Program Files\QGIS 2.18\bin\o4w_env.bat"

@echo on
"C:\Program Files\QGIS 2.18\bin\pyrcc4" -o resources.py resources.qrc
