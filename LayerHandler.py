from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField
from qgis.core import QgsMarkerSymbol, QgsSingleSymbolRenderer
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor


class LayerHandler(object):
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LayerHandler, cls).__new__(cls)
            return cls.instance


    def __init__(self, iface):
        self.iface = iface

        self.is_tool1_initialized = False
        self.is_tool2_initialized = False
        self.is_tool3_initialized = False
        self.is_tool4_initialized = False
        self.is_tool5_initialized = False

        self.root = QgsProject.instance().layerTreeRoot()
        self.my_crs = QgsCoordinateReferenceSystem.fromEpsgId(3067)


    def init_tool1(self):
        if self.is_tool1_initialized:
            return

        self.group_1 = self.root.addGroup('1. Tieosoite')

        self.tool1_annotation_layer = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet')

        QgsProject.instance().addMapLayer(self.tool1_annotation_layer, False)

        self.group_1.addLayer(self.tool1_annotation_layer)

        self.is_tool1_initialized = True


    def init_tool2(self):
        if self.is_tool2_initialized:
            return
        self.group_2 = self.root.addGroup('2. Hakutyökalu')

        self.tool2_point_layer = QgsVectorLayer('Point', f'Pisteet', 'memory')
        self.tool2_point_pr = self.tool2_point_layer.dataProvider()
        self.tool2_point_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.tool2_point_pr.addAttributes([QgsField("ID", QVariant.String)])
        self.tool2_point_layer.updateFields()

        #style
        symbol = QgsMarkerSymbol.createSimple({
        'color': '255,0,0',
        'name': 'circle',
        'size': '2.5'
        })

        self.tool2_point_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        self.tool2_point_layer.setCrs(self.my_crs)

        QgsProject.instance().addMapLayer(self.tool2_point_layer, False)
        self.group_2.addLayer(self.tool2_point_layer)

        self.is_tool2_initialized = True


    def init_tool3(self):
        if self.is_tool3_initialized:
            return
        self.group_3 = self.root.addGroup('3. Tieosa')

        #annotation layer
        self.tool3_annotation_layer = QgsVectorLayer('Point', f'Karttavihjeet', 'memory')
        self.tool3_annotation_pr = self.tool3_annotation_layer.dataProvider()
        self.tool3_annotation_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.tool3_annotation_pr.addAttributes([QgsField("ID", QVariant.String)])
        self.tool3_annotation_layer.updateFields()

        #style
        symbol = QgsMarkerSymbol.createSimple({
        'color': '0,0,0',
        'name': 'circle',
        'size': '0.0'
        })

        self.tool3_annotation_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        self.tool3_annotation_layer.setCrs(self.my_crs)

        QgsProject.instance().addMapLayer(self.tool3_annotation_layer, False)
        self.group_3.addLayer(self.tool3_annotation_layer)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers()
        self.tool3_roadway0_layer = roadway_layer_list[0]
        self.tool3_roadway1_layer = roadway_layer_list[1]
        self.tool3_roadway2_layer = roadway_layer_list[2]

        QgsProject.instance().addMapLayer(self.tool3_roadway0_layer, False)
        self.group_3.addLayer(self.tool3_roadway0_layer)
        QgsProject.instance().addMapLayer(self.tool3_roadway1_layer, False)
        self.group_3.addLayer(self.tool3_roadway1_layer)
        QgsProject.instance().addMapLayer(self.tool3_roadway2_layer, False)
        self.group_3.addLayer(self.tool3_roadway2_layer)

        self.is_tool3_initialized = True


    def init_roadway_layers(self):
        layer_list = []

        #roadway 0 layer
        self.roadway0_layer = QgsVectorLayer('LineString?crs=3067&field=id:integer&index=yes', 'Ajoradat 0', 'memory')
        self.roadway0_pr = self.roadway0_layer.dataProvider()
        self.roadway0_pr.addAttributes([QgsField("ID", QVariant.String)])
        self.roadway0_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.roadway0_layer.updateFields()

        renderer = self.roadway0_layer.renderer()
        renderer.symbol().setWidth(0.6)
        renderer.symbol().setColor(QColor(0,255,0))
        self.roadway0_layer.triggerRepaint()

        self.roadway0_layer.setCrs(self.my_crs)
        layer_list.append(self.roadway0_layer)

        #roadway 1 layer
        self.roadway1_layer = QgsVectorLayer('LineString?crs=3067&field=id:integer&index=yes', 'Ajoradat 1', 'memory')
        self.roadway1_pr = self.roadway1_layer.dataProvider()
        self.roadway1_pr.addAttributes([QgsField("ID", QVariant.String)])
        self.roadway1_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.roadway1_layer.updateFields()

        renderer = self.roadway1_layer.renderer()
        renderer.symbol().setWidth(0.6)
        renderer.symbol().setColor(QColor(255,127,80))
        self.roadway1_layer.triggerRepaint()

        self.roadway1_layer.setCrs(self.my_crs)
        layer_list.append(self.roadway1_layer)

        #roadway 2 layer
        self.roadway2_layer = QgsVectorLayer('LineString?crs=3067&field=id:integer&index=yes', 'Ajoradat 2', 'memory')
        self.roadway2_pr = self.roadway2_layer.dataProvider()
        self.roadway2_pr.addAttributes([QgsField("ID", QVariant.String)])
        self.roadway2_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.roadway2_layer.updateFields()

        renderer = self.roadway2_layer.renderer()
        renderer.symbol().setWidth(0.6)
        renderer.symbol().setColor(QColor(0,0,255))
        self.roadway2_layer.triggerRepaint()

        self.roadway2_layer.setCrs(self.my_crs)
        layer_list.append(self.roadway2_layer)

        return layer_list


    def init_point_layer(self, color:str, shape:str, size:str, layer_name:str):
        point_layer = QgsVectorLayer('Point', layer_name, 'memory')

        point_pr = point_layer.dataProvider()
        point_pr.addAttributes([QgsField("NAME", QVariant.String)])
        point_pr.addAttributes([QgsField("ID", QVariant.String)])

        point_layer.updateFields()

        #point style
        symbol = QgsMarkerSymbol.createSimple({
        'color': color,
        'name': shape,
        'size': size
        })
        point_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        point_layer.setCrs(self.my_crs)

        return point_layer


