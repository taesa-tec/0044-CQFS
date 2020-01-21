:: CUSTOM
@echo off
SET OSGEO4W_ROOT=C:\Program Files\QGIS 2.18

call "%OSGEO4W_ROOT%\bin\o4w_env.bat"

path %OSGEO4W_ROOT%\bin;%OSGEO4W_ROOT%\apps\qgis\bin;%PATH%

:: DEFAULT: C:\Program Files\QGIS 2.18\bin\python-qgis.bat
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt4\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%
"%OSGEO4W_ROOT%"\bin\python.exe %*
