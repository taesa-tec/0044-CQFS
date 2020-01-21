@echo off
SET OSGEO4W_ROOT=C:\Program Files\QGIS 2.18
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
@echo off
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin

set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python;
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;C:\Program Files\JetBrains\PyCharm 2018.2.4\debug-eggs\pycharm-debug.egg
SET PYTHONPATH=C:\PROGRA~1\QGIS2~1.18\apps\qgis\python\plugins\processing;C:\PROGRA~1\QGIS2~1.18\apps\qgis\python;C:\PROGRA~1\QGIS2~1.18\apps\qgis\python\plugins;C:\PROGRA~1\QGIS2~1.18\bin\python27.zip;C:\PROGRA~1\QGIS2~1.18\apps\Python27\DLLs;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\plat-win;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\lib-tk;C:\PROGRA~1\QGIS2~1.18\bin;C:\PROGRA~1\QGIS2~1.18\apps\Python27;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\jinja2-2.7.2-py2.7.egg;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\markupsafe-0.23-py2.7-win-amd64.egg;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\win32;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\win32\lib;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\Pythonwin;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\Shapely-1.2.18-py2.7-win-amd64.egg;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\wx-2.8-msw-unicode;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\xlrd-0.9.2-py2.7.egg;C:\PROGRA~1\QGIS2~1.18\apps\Python27\lib\site-packages\xlwt-0.7.5-py2.7.egg;C:\Users\heitor.carneiro\.qgis2\python;C:\Users\heitor.carneiro\.qgis2\python\plugins;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis

rem EVERYTHING FROM HERE DOWN IS TAKEN FROM THE `qgis.bat` file

set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt4\plugins
start "QGIS" /B "%OSGEO4W_ROOT%"\bin\qgis-bin.exe %*
