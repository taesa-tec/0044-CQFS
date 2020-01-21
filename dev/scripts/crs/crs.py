""""
https://docs.qgis.org/2.18/en/docs/pyqgis_developer_cookbook/crs.html
"""
from qgis.core import QgsCoordinateReferenceSystem
from osgeo import osr


if __name__ == '__console__':
    print("-----------------------------------------------\n\n")
    # PostGIS SRID 4326 is allocated for WGS84
    # If not specified otherwise in second parameter, PostGIS SRID is used by default.
    crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.PostgisCrsId)
    print("Valid: ", crs.isValid())
    print("QGIS CRS ID:", crs.srsid())
    print("EPSG ID:", crs.authid())
    print("Description:", crs.description())
    print("Projection Acronym:", crs.projectionAcronym())
    print("Ellipsoid Acronym:", crs.ellipsoidAcronym())
    print("Proj4 String:", crs.toProj4())
    # check whether it's geographic or projected coordinate system
    print("Is geographic:", crs.geographicFlag())
    # check type of map units in this CRS (values defined in QGis::units enum)
    print("Map units:", crs.mapUnits())
    print("-----------------------------------------------\n\n")

    wkt = '''GEOGCS["WGS84", DATUM["WGS84", SPHEROID["WGS84", 6378137.0, 298.257223563]],
                PRIMEM["Greenwich", 0.0],
                UNIT["degree", 0.017453292519943295],
                AXIS["Longitude", EAST], AXIS["Latitude", NORTH]]'''
    crs = QgsCoordinateReferenceSystem(wkt)
    print("Valid: ", crs.isValid())
    print("QGIS CRS ID:", crs.srsid())
    print("EPSG ID:", crs.authid())
    print("Description:", crs.description())
    print("Projection Acronym:", crs.projectionAcronym())
    print("Ellipsoid Acronym:", crs.ellipsoidAcronym())
    print("Proj4 String:", crs.toProj4())
    # check whether it's geographic or projected coordinate system
    print("Is geographic:", crs.geographicFlag())
    # check type of map units in this CRS (values defined in QGis::units enum)
    print("Map units:", crs.mapUnits())
    print("-----------------------------------------------\n\n")

    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

    print("Valid: ", crs.isValid())
    print("QGIS CRS ID:", crs.srsid())
    print("EPSG ID:", crs.authid())
    print("Description:", crs.description())
    print("Projection Acronym:", crs.projectionAcronym())
    print("Ellipsoid Acronym:", crs.ellipsoidAcronym())
    print("Proj4 String:", crs.toProj4())
    # check whether it's geographic or projected coordinate system
    print("Is geographic:", crs.geographicFlag())
    # check type of map units in this CRS (values defined in QGis::units enum)
    print("Map units:", crs.mapUnits())
    print("-----------------------------------------------\n\n")

    wkt = '''PROJCS["Albers_like_IBGE",GEOGCS["GCS_SIRGAS_2000",DATUM["D_SIRGAS_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-54.0],PARAMETER["Standard_Parallel_1",-2.0],PARAMETER["Standard_Parallel_2",-22.0],PARAMETER["Latitude_Of_Origin",-12.0],UNIT["Meter",1.0]]'''
    crs = QgsCoordinateReferenceSystem(wkt)
    print("Valid: ", crs.isValid())
    print("QGIS CRS ID:", crs.srsid())
    print("EPSG ID:", crs.authid())
    print("Description:", crs.description())
    print("Projection Acronym:", crs.projectionAcronym())
    print("Ellipsoid Acronym:", crs.ellipsoidAcronym())
    print("Proj4 String:", crs.toProj4())
    # check whether it's geographic or projected coordinate system
    print("Is geographic:", crs.geographicFlag())
    # check type of map units in this CRS (values defined in QGis::units enum)
    print("Map units:", crs.mapUnits())

    print('\nSaving..')

    success = crs.saveAsUserCRS('Albers_like_IBGE')
    print(success)
    print(crs.srsid())

    print('done.')

    print("-----------------------------------------------\n\n")

    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    print(srs.ExportToProj4())
