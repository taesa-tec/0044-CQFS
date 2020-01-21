:: Substituir pelo path da maquina

:: QGISNAME=qgis
:: C:\Program Files\QGIS 2.18
:: C:\Program Files\QGIS 2.18\apps\qgis
:: C:\Users\heitor.carneiro\.qgis2\python
:: C:\Users\heitor.carneiro\.qgis2\python\plugins

SET OSGEO4W_ROOT="C:\Program Files\QGIS 2.18"
SET QGISNAME=qgis
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
SET QGIS_PREFIX_PATH=%QGIS%

set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%QGIS_PREFIX_PATH%\qtplugins;%OSGEO4W_ROOT%\apps\qt4\plugins

CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

:: Abrir QGIS e executar no console python: import sys; print(sys.path)
SET PYTHONPATH=C:\Program Files\QGIS 2.18\apps\qgis\python\plugins\processing;C:\Program Files\QGIS 2.18\apps\qgis\python;C:\Program Files\QGIS 2.18\apps\qgis\python\plugins;C:\Program Files\QGIS 2.18\bin\python27.zip;C:\Program Files\QGIS 2.18\apps\Python27\DLLs;C:\Program Files\QGIS 2.18\apps\Python27\lib;C:\Program Files\QGIS 2.18\apps\Python27\lib\plat-win;C:\Program Files\QGIS 2.18\apps\Python27\lib\lib-tk;C:\Program Files\QGIS 2.18\bin;C:\Program Files\QGIS 2.18\apps\Python27;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\jinja2-2.7.2-py2.7.egg;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\markupsafe-0.23-py2.7-win-amd64.egg;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\win32;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\win32\lib;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\Pythonwin;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\Shapely-1.2.18-py2.7-win-amd64.egg;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\wx-2.8-msw-unicode;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\xlrd-0.9.2-py2.7.egg;C:\Program Files\QGIS 2.18\apps\Python27\lib\site-packages\xlwt-0.7.5-py2.7.egg;C:\Users\heitor.carneiro\.qgis2\python;C:\Users\heitor.carneiro\.qgis2\python\plugins;%PYTHONPATH%
SET PYTHONHOME=%OSGEO4W_ROOT%\apps\Python27
SET PATH=%QGIS_PREFIX_PATH%\bin;%OSGEO4W_ROOT%\apps\Python27\Scripts;%PATH%

:: C:\Program Files\JetBrains\PyCharm 2018.2.4\helpers\pydev
::SET QGIS_IDE="C:\Program Files\JetBrains\PyCharm 2018.2.4\bin\pycharm64.exe"

:: C:\Program Files\Brainwy\LiClipse 5.0.3\plugins\org.python.pydev.core_6.5.0.201809011413\pysrc
:: C:\Users\heitor.carneiro\.vscode\extensions\fabioz.vscode-pydev-0.1.5\server\plugins\org.python.pydev.core_6.3.3.201805051749\pysrc
SET QGIS_IDE="C:\Program Files\Brainwy\LiClipse 5.0.3\LiClipse.exe"

start "PyCharm aware of QGIS" /B %QGIS_IDE% %*
