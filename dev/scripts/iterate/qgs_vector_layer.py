from qgis.core import QgsVectorLayer


def test_vector_layer():
    input_layer = QgsVectorLayer(r"C:\Users\diane.soares\Downloads\ne_10m_airports\ne_10m_airports.shp", "ne_10m_airports",
                                 "ogr")

    if not input_layer:
        print("Layer failed to load!")

    print(input_layer.name())
    print(input_layer.crs().isValid())
    print(input_layer.crs().authid())
    print(input_layer.crs().toWkt())

    source = unicode(input_layer.source())
    print(source)

    return input_layer


if __name__ == '__main__':
    test_vector_layer()


