from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsField
from qgis.core import QgsMarkerSymbol, QgsSingleSymbolRenderer, QgsFeature, QgsGeometry, QgsPointXY
from qgis.core import QgsTextAnnotation, edit
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from PyQt5.QtCore import QSizeF, QPoint
from PyQt5.QtGui import QTextDocument


class LayerHandler(object):
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LayerHandler, cls).__new__(cls)
            return cls.instance


    def __init__(self):
        self.is_tool1_initialized = False
        self.is_tool2_initialized = False
        self.is_tool3_initialized = False
        self.is_tool4_initialized = False
        self.is_tool5_initialized = False

        self.layers = []

        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.my_crs = QgsCoordinateReferenceSystem.fromEpsgId(3067)


    def init_tool1(self):
        if self.is_tool1_initialized:
            return

        self.group_1 = self.root.addGroup('1. Tieosoite')

        #annotation layer
        self.tool1_annotation_layer = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet')
        self.project.addMapLayer(self.tool1_annotation_layer, False)
        self.group_1.addLayer(self.tool1_annotation_layer)

        self.rearrange_layers(self.layers)
        self.is_tool1_initialized = True


    def init_tool2(self):
        if self.is_tool2_initialized:
            return

        self.group_2 = self.root.addGroup('2. Hakutyökalu')

        #point layer
        self.tool2_point_layer = self.init_point_layer('255,0,0', 'circle', '2.5', 'Pisteet')
        self.project.addMapLayer(self.tool2_point_layer, False)
        self.group_2.addLayer(self.tool2_point_layer)

        self.rearrange_layers(self.layers)
        self.is_tool2_initialized = True


    def init_tool3(self):
        if self.is_tool3_initialized:
            return

        self.group_3 = self.root.addGroup('3. Tieosa')

        #annotation layer
        self.tool3_annotation_layer = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet')
        self.project.addMapLayer(self.tool3_annotation_layer, False)
        self.group_3.addLayer(self.tool3_annotation_layer)

        #starting point layer
        self.tool3_starting_point_layer = self.init_point_layer('0,255,0', 'square', '3.0', 'Alkupisteet')
        self.project.addMapLayer(self.tool3_starting_point_layer, False)
        self.group_3.addLayer(self.tool3_starting_point_layer)

        #ending point layer
        self.tool3_ending_point_layer = self.init_point_layer('255,0,0', 'square', '3.0', 'Loppupisteet')
        self.project.addMapLayer(self.tool3_ending_point_layer, False)
        self.group_3.addLayer(self.tool3_ending_point_layer)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers()
        #creating variables to reference them when adding features
        self.tool3_roadway0_layer = roadway_layer_list[0]
        self.tool3_roadway1_layer = roadway_layer_list[1]
        self.tool3_roadway2_layer = roadway_layer_list[2]

        for roadway_layer in roadway_layer_list:
            self.project.addMapLayer(roadway_layer, False)
            self.group_3.addLayer(roadway_layer)

        self.rearrange_layers(self.layers)
        self.is_tool3_initialized = True


    def init_tool4(self):
        if self.is_tool4_initialized:
            return

        self.group_4 = self.root.addGroup('4. Tieosoite (Alku- ja loppupiste)')

        #annotation layer
        self.tool4_annotation_layer = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet')
        self.project.addMapLayer(self.tool4_annotation_layer, False)
        self.group_4.addLayer(self.tool4_annotation_layer)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers()
        #creating variables to reference them when adding features
        self.tool4_roadway0_layer = roadway_layer_list[0]
        self.tool4_roadway1_layer = roadway_layer_list[1]
        self.tool4_roadway2_layer = roadway_layer_list[2]

        for roadway_layer in roadway_layer_list:
            self.project.addMapLayer(roadway_layer, False)
            self.group_4.addLayer(roadway_layer)

        self.rearrange_layers(self.layers)
        self.is_tool4_initialized = True


    def init_tool5(self):
        if self.is_tool5_initialized:
            return
        self.group_5 = self.root.addGroup('5. Kohdistustyökalu')

        #point layer
        self.tool5_point_layer = self.init_point_layer('0,255,0', 'triangle', '3.5', 'Pisteet')
        self.project.addMapLayer(self.tool5_point_layer, False)
        self.group_5.addLayer(self.tool5_point_layer)

        #starting point layer
        self.tool5_starting_point_layer = self.init_point_layer('0,255,0', 'square', '3.0', 'Alkupisteet')
        self.project.addMapLayer(self.tool5_starting_point_layer, False)
        self.group_5.addLayer(self.tool5_starting_point_layer)

        #ending point layer
        self.tool5_ending_point_layer = self.init_point_layer('255,0,0', 'square', '3.0', 'Loppupisteet')
        self.project.addMapLayer(self.tool5_ending_point_layer, False)
        self.group_5.addLayer(self.tool5_ending_point_layer)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers()
        #creating variables to reference them when adding features
        self.tool5_roadway0_layer = roadway_layer_list[0]
        self.tool5_roadway1_layer = roadway_layer_list[1]
        self.tool5_roadway2_layer = roadway_layer_list[2]

        for roadway_layer in roadway_layer_list:
            self.project.addMapLayer(roadway_layer, False)
            self.group_5.addLayer(roadway_layer)

        self.rearrange_layers(self.layers)
        self.is_tool5_initialized = True


    def add_annotation(self, tool_id:str, text:str, point_x:float, point_y:float, number_of_rows:int=None, position_x:int=14, position_y:int=11):
        """Adds an annotation to the given coordinates.

        Args:
            tool_id (str): Tool number.
            text (str): Annotation content.
            point_x (float): Annotation X coordinates.
            point_y (float): Annotation Y coordinates.
            number_of_rows (int, optional): Height of the annotation box. Defaults to None.
            position_x (int, optional): X position of the annotation box in reference to the coordinates. Defaults to 14.
            position_y (int, optional): X position of the annotation box in reference to the coordinates. Defaults to 11.
        """
        if tool_id == '1':
            layer = self.tool1_annotation_layer
        if tool_id == '3':
            layer = self.tool3_annotation_layer
        if tool_id == '4':
            layer = self.tool4_annotation_layer

        annot = QgsTextAnnotation()

        if number_of_rows != None:
            annot_length = len(text) // 1.5
            annot_width = number_of_rows * 6
            annot.setFrameSizeMm(QSizeF(annot_length, annot_width))
        else:
            annot_length = len(text) * 3
            annot.setFrameSizeMm(QSizeF(annot_length, 6))
        annot.setMapLayer(layer)
        annot.setFrameOffsetFromReferencePointMm(QPoint(position_x, position_y))
        annot.setDocument(QTextDocument(text))

        # X and Y are defined previously
        annot.setMapPositionCrs(QgsCoordinateReferenceSystem(layer.crs()))
        annot.setMapPosition(QgsPointXY(point_x, point_y))

        self.project.annotationManager().addAnnotation(annot)


    def add_point_feature(self, tool_id:str, feature_name:str, point_x:float, point_y:float, point_type:str=None):
        """Draws a point to given coordinates.

        Args:
            tool_id (str): Tool number.
            feature_name (str): Feature name.
            point_x (float): X coordinate.
            point_y (float): Y coordinate.
            point_type (str, optional): Add feature to the starting or ending point layer. Defaults to None.
        """
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point_x, point_y)))
        feature.setAttributes([tool_id, feature_name])

        if tool_id == '2':
            self.tool2_point_layer.dataProvider().addFeature(feature)
            self.tool2_point_layer.updateExtents()
            self.tool2_point_layer.reload()

        if tool_id == '3':
            if point_type == 'starting':
                self.tool3_starting_point_layer.dataProvider().addFeature(feature)
                self.tool3_starting_point_layer.updateExtents()
                self.tool3_starting_point_layer.reload()
            if point_type == 'ending':
                self.tool3_ending_point_layer.dataProvider().addFeature(feature)
                self.tool3_ending_point_layer.updateExtents()
                self.tool3_ending_point_layer.reload()

        if tool_id == '5':
            if point_type == 'starting':
                self.tool5_starting_point_layer.dataProvider().addFeature(feature)
                self.tool5_starting_point_layer.updateExtents()
                self.tool5_starting_point_layer.reload()
            if point_type == 'ending':
                self.tool5_ending_point_layer.dataProvider().addFeature(feature)
                self.tool5_ending_point_layer.updateExtents()
                self.tool5_ending_point_layer.reload()
            if point_type == None:
                self.tool5_point_layer.dataProvider().addFeature(feature)
                self.tool5_point_layer.updateExtents()
                self.tool5_point_layer.reload()

            
    def add_roadway_feature(self, tool_id:str, feature_name:str, xy_points:list, roadway:str):
        """Draws a line using list of XY coordinates.

        Args:
            tool_id (str): Tool number.
            feature_name (str): Feature name.
            xy_points (list): List of QgsPointXY type XY coordinates of a linestring.
            roadway (str): Roadway number.
        """
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY(xy_points))
        feature.setAttributes([tool_id, feature_name])
#       
        if tool_id == '3':
            if roadway == '0':
                self.tool3_roadway0_layer.dataProvider().addFeature(feature)
                self.tool3_roadway0_layer.updateExtents()
                self.tool3_roadway0_layer.reload()
            if roadway == '1':
                self.tool3_roadway1_layer.dataProvider().addFeature(feature)
                self.tool3_roadway1_layer.updateExtents()
                self.tool3_roadway1_layer.reload()
            if roadway == '2':
                self.tool3_roadway2_layer.dataProvider().addFeature(feature)
                self.tool3_roadway2_layer.updateExtents()
                self.tool3_roadway2_layer.reload()

        if tool_id == '4':
            if roadway == '0':
                self.tool4_roadway0_layer.dataProvider().addFeature(feature)
                self.tool4_roadway0_layer.updateExtents()
                self.tool4_roadway0_layer.reload()
            if roadway == '1':
                self.tool4_roadway1_layer.dataProvider().addFeature(feature)
                self.tool4_roadway1_layer.updateExtents()
                self.tool4_roadway1_layer.reload()
            if roadway == '2':
                self.tool4_roadway2_layer.dataProvider().addFeature(feature)
                self.tool4_roadway2_layer.updateExtents()
                self.tool4_roadway2_layer.reload()

        if tool_id == '5':
            if roadway == '0':
                self.tool5_roadway0_layer.dataProvider().addFeature(feature)
                self.tool5_roadway0_layer.updateExtents()
                self.tool5_roadway0_layer.reload()
            if roadway == '1':
                self.tool5_roadway1_layer.dataProvider().addFeature(feature)
                self.tool5_roadway1_layer.updateExtents()
                self.tool5_roadway1_layer.reload()
            if roadway == '2':
                self.tool5_roadway2_layer.dataProvider().addFeature(feature)
                self.tool5_roadway2_layer.updateExtents()
                self.tool5_roadway2_layer.reload()
        
    
    def remove_feature(self):
        """Removes one random feature that was added using this plugin.
        """
        for layer in self.layers:
            with edit(layer):
                for feature in layer.getFeatures():
                    layer.deleteFeature(feature.id())
                    layer.reload()
                    break

    
    def remove_all_features(self):
        """Removes all features that were added using this plugin.
        """
        for layer in self.layers:
            with edit(layer):
                feature_id_list = [feature.id() for feature in layer.getFeatures()]
                layer.deleteFeatures(feature_id_list)
                layer.reload()


# ------------------------------------------------------#


    def init_roadway_layers(self):
        """Create a different layer for each roadway number for roadway features.

        Returns:
            layer_list (list): List of roadway layers.
        """
        layer_list = []

        #roadway 0 layer
        self.roadway0_layer = QgsVectorLayer('LineString?crs=3067&field=id:integer&index=yes', 'Ajoradat 0', 'memory')
        self.roadway0_pr = self.roadway0_layer.dataProvider()
        self.roadway0_pr.addAttributes([QgsField("TOOL_ID", QVariant.String)])
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
        self.roadway1_pr.addAttributes([QgsField("TOOL_ID", QVariant.String)])
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
        self.roadway2_pr.addAttributes([QgsField("TOOL_ID", QVariant.String)])
        self.roadway2_pr.addAttributes([QgsField("NAME", QVariant.String)])
        self.roadway2_layer.updateFields()

        renderer = self.roadway2_layer.renderer()
        renderer.symbol().setWidth(0.6)
        renderer.symbol().setColor(QColor(0,0,255))
        self.roadway2_layer.triggerRepaint()

        self.roadway2_layer.setCrs(self.my_crs)
        layer_list.append(self.roadway2_layer)

        self.layers.extend(layer_list)
        return layer_list


    def init_point_layer(self, color:str, shape:str, size:str, layer_name:str):
        """Creates a point layer with given style variables.

        Args:
            color (str): _description_
            shape (str): _description_
            size (str): _description_
            layer_name (str): Name of the layer.

        Returns:
            _type_: _description_
        """
        point_layer = QgsVectorLayer('Point?crs=epsg:3067', layer_name, 'memory')

        point_pr = point_layer.dataProvider()
        point_pr.addAttributes([QgsField("TOOL_ID", QVariant.String)])
        point_pr.addAttributes([QgsField("NAME", QVariant.String)])

        point_layer.updateFields()

        #point style
        symbol = QgsMarkerSymbol.createSimple({
        'color': color,
        'name': shape,
        'size': size
        })
        point_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        
        point_layer.setCrs(self.my_crs)

        self.layers.append(point_layer)
        return point_layer


    def rearrange_layers(self, layer_list):
        """Moves every new layer created by this plugin on top.

        Args:
            layer_list (list): List of existing layers.
        """
        self.root.setHasCustomLayerOrder(True)
        order = self.root.customLayerOrder()

        for layer in layer_list: # How many layers we need to move
            order.insert(0, order.pop(order.index(layer))) # Last layer to first position
    
        self.root.setCustomLayerOrder(order)


