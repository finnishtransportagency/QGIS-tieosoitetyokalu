"""
/*

* Copyright 2022 Finnish Transport Infrastructure Agency
*

* Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the European Commission - subsequent versions of the EUPL (the "Licence");
* You may not use this work except in compliance with the Licence.
* You may obtain a copy of the Licence at:
*
* https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/2020-03/EUPL-1.2%20EN.txt
*
* Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the Licence for the specific language governing permissions and limitations under the Licence.
*/
"""


from qgis.core import (QgsCoordinateReferenceSystem, QgsFeature, QgsField,
                       QgsGeometry, QgsMarkerSymbol, QgsPointXY, QgsProject,
                       QgsSingleSymbolRenderer, QgsTextAnnotation,
                       QgsVectorLayer, edit)
from qgis.PyQt.QtCore import QCoreApplication, QPoint, QSizeF, QVariant
from qgis.PyQt.QtGui import QColor, QTextDocument


class LayerHandler(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LayerHandler, cls).__new__(cls)
            return cls.instance


    def __init__(self):

        self.tool_layers = {
            "1" : {
                "Karttavihjeet": None
            },

            "2" : {
                "Pisteet" : None
            },

            "3" : {
                "Karttavihjeet": None,
                "Alkupisteet": None,
                "Loppupisteet": None,
                "Ajoradat 0" : None,
                "Ajoradat 1" : None,
                "Ajoradat 2" : None
            },

            "4" : {
                "Karttavihjeet": None,
                "Ajoradat 0" : None,
                "Ajoradat 1" : None,
                "Ajoradat 2" : None
            },

            "5" : {
                "Pisteet" : None,
                "Alkupisteet": None,
                "Loppupisteet": None,
                "Ajoradat 0" : None,
                "Ajoradat 1" : None,
                "Ajoradat 2" : None
            }
        }

        self.layers = []

        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.my_crs = QgsCoordinateReferenceSystem.fromEpsgId(3067)

    @staticmethod
    def tr(message, disambiguation="", n=-1) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LayerHandler', message, disambiguation, n)


    def create_layer_group(self, group_name:str):
        """Creates a layer group.

        Args:
            group_name (str): Name of the group.
        """
        tool_group = self.root.findGroup(self.tr(u'Tieosoitetyökalu'))
        if tool_group is None:
            tool_group = self.root.insertGroup(0, self.tr(u'Tieosoitetyökalu'))
        group = tool_group.findGroup(group_name)

        return tool_group.addGroup(group_name) if group is None else group


    def init_tool1(self):
        self.group_1 = self.create_layer_group(self.tr(u'1. Tieosoite'))

        #annotation layer
        self.tool_layers['1']['Karttavihjeet'] = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet', '1', self.group_1)


    def init_tool2(self):
        self.group_2 = self.create_layer_group(self.tr(u'2. Hakutyökalu'))

        #point layer
        self.tool_layers['2']['Pisteet'] = self.init_point_layer('255,0,0', 'circle', '2.5', 'Pisteet', '2', self.group_2)


    def init_tool3(self):
        self.group_3 = self.create_layer_group(self.tr(u'3. Tieosa'))

        #annotation layer
        self.tool_layers['3']['Karttavihjeet'] = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet', '3', self.group_3)

        #starting point layer
        self.tool_layers['3']['Alkupisteet'] = self.init_point_layer('0,255,0', 'square', '3.0', 'Alkupisteet', '3', self.group_3)

        #ending point layer
        self.tool_layers['3']['Loppupisteet'] = self.init_point_layer('255,0,0', 'square', '3.0', 'Loppupisteet', '3', self.group_3)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers('3', self.group_3)
        #creating variables to reference them when adding features
        self.tool_layers['3']['Ajoradat 0'] = roadway_layer_list[0]
        self.tool_layers['3']['Ajoradat 1'] = roadway_layer_list[1]
        self.tool_layers['3']['Ajoradat 2'] = roadway_layer_list[2]


    def init_tool4(self):
        self.group_4 = self.create_layer_group(self.tr(u'4. Tieosoite (Alku- ja loppupiste)'))

        #annotation layer
        self.tool_layers['4']['Karttavihjeet'] = self.init_point_layer('0,0,0', 'circle', '0.0', 'Karttavihjeet', '4', self.group_4)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers('4', self.group_4)
        #creating variables to reference them when adding features
        self.tool_layers['4']['Ajoradat 0'] = roadway_layer_list[0]
        self.tool_layers['4']['Ajoradat 1'] = roadway_layer_list[1]
        self.tool_layers['4']['Ajoradat 2'] = roadway_layer_list[2]


    def init_tool5(self):
        self.group_5 = self.create_layer_group(self.tr(u'5. Kohdistustyökalu'))

        #point layer
        self.tool_layers['5']['Pisteet'] = self.init_point_layer('0,255,0', 'triangle', '3.5', 'Pisteet', '5', self.group_5)

        #starting point layer
        self.tool_layers['5']['Alkupisteet'] = self.init_point_layer('0,255,0', 'square', '3.0', 'Alkupisteet', '5', self.group_5)

        #ending point layer
        self.tool_layers['5']['Loppupisteet'] = self.init_point_layer('255,0,0', 'square', '3.0', 'Loppupisteet', '5', self.group_5)

        #roadway 0-2 layers
        roadway_layer_list = self.init_roadway_layers('5', self.group_5)
        #creating variables to reference them when adding features
        self.tool_layers['5']['Ajoradat 0'] = roadway_layer_list[0]
        self.tool_layers['5']['Ajoradat 1'] = roadway_layer_list[1]
        self.tool_layers['5']['Ajoradat 2'] = roadway_layer_list[2]


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

        layer = self.tool_layers[tool_id]['Karttavihjeet']

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

        if point_type == 'starting':
            self.add_feature(self.tool_layers[tool_id]['Alkupisteet'], feature)
        elif point_type == 'ending':
            self.add_feature(self.tool_layers[tool_id]['Loppupisteet'], feature)
        elif point_type is None:
            self.add_feature(self.tool_layers[tool_id]['Pisteet'], feature)


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
        self.add_feature(self.tool_layers[tool_id][f'Ajoradat {roadway}'], feature)


    def add_feature(self, layer:QgsVectorLayer, feature:QgsFeature):
        """Adds and reloads a layer after adding a feature.

        Args:
            layer (QgsVectorLayer): Layer to add the feature to.
            feature (QgsFeature): Feature being added.
        """
        layer.dataProvider().addFeature(feature)
        layer.updateExtents()
        layer.reload()


    def remove_feature(self):
        """Removes one random feature that was added using this plugin.
        """
        for layer in self.layers:
            if layer in self.project.mapLayers().values():
                with edit(layer):
                    for feature in layer.getFeatures():
                        layer.deleteFeature(feature.id())
                        layer.reload()
                        break


    def remove_all_features(self):
        """Removes all features that were added using this plugin.
        """
        for layer in self.layers:
            if layer in self.project.mapLayers().values():
                with edit(layer):
                    feature_id_list = [feature.id() for feature in layer.getFeatures()]
                    layer.deleteFeatures(feature_id_list)
                    layer.reload()


# ------------------------------------------------------#


    def init_roadway_layers(self, tool:str, group=None):
        """Create a different layer for each roadway number for roadway features.

        Args:
            tool (str): Tool number.
            group (): A group to add the layer to.

        Returns:
            layer_list (list): List of roadway layers.
        """
        layer_list = []

        #roadway 0 layer
        if self.tool_layers[tool]['Ajoradat 0'] != None and self.tool_layers[tool]['Ajoradat 0'] in self.project.mapLayers().values():
            layer = self.tool_layers[tool]['Ajoradat 0']
            layer_list.append(layer)

            if layer not in self.layers:
                self.layers.append(layer)

        else:
            roadway0_layer = self.create_roadway_layer(self.tr(u'Ajoradat 0'), QColor(0,255,0))

            self.project.addMapLayer(roadway0_layer, False)
            group.addLayer(roadway0_layer)

            layer_list.append(roadway0_layer)

            if roadway0_layer not in self.layers:
                self.layers.append(roadway0_layer)

        #roadway 1 layer
        if self.tool_layers[tool]['Ajoradat 1'] != None and self.tool_layers[tool]['Ajoradat 1'] in self.project.mapLayers().values():
            layer = self.tool_layers[tool]['Ajoradat 1']
            layer_list.append(layer)

            if layer not in self.layers:
                self.layers.append(layer)

        else:
            roadway1_layer = self.create_roadway_layer(self.tr(u'Ajoradat 1'), QColor(255,127,80))

            self.project.addMapLayer(roadway1_layer, False)
            group.addLayer(roadway1_layer)

            layer_list.append(roadway1_layer)

            if roadway1_layer not in self.layers:
                self.layers.append(roadway1_layer)

        #roadway 2 layer
        if self.tool_layers[tool]['Ajoradat 2'] != None and self.tool_layers[tool]['Ajoradat 2'] in self.project.mapLayers().values():
            layer = self.tool_layers[tool]['Ajoradat 2']
            layer_list.append(layer)

            if layer not in self.layers:
                self.layers.append(layer)

        else:
            roadway2_layer = self.create_roadway_layer(self.tr(u'Ajoradat 2'), QColor(0,0,255))

            self.project.addMapLayer(roadway2_layer, False)
            group.addLayer(roadway2_layer)

            layer_list.append(roadway2_layer)

            if roadway2_layer not in self.layers:
                    self.layers.append(roadway2_layer)

        return layer_list


    def create_roadway_layer(self, name, color):
        layer = QgsVectorLayer('LineString?crs=epsg:3067&field=id:integer&index=yes', name, 'memory')
        pr = layer.dataProvider()
        pr.addAttributes([QgsField("TOOL_ID", QVariant.String), QgsField("NAME", QVariant.String)])
        layer.updateFields()

        renderer = layer.renderer()
        renderer.symbol().setWidth(0.6)
        renderer.symbol().setColor(color)
        layer.triggerRepaint()

        layer.setCrs(self.my_crs)

        return layer


    def init_point_layer(self, color:str, shape:str, size:str, layer_name:str, tool:str, group=None):
        """Creates a point layer with given style variables.

        Args:
            color (str): _description_
            shape (str): _description_
            size (str): _description_
            layer_name (str): Name of the layer.
            tool (str): Tool number.
            group (): A group to add the layer to.

        Returns:
            point_layer (QgsVectorLayer): _description_
        """
        if self.tool_layers[tool][layer_name] != None and self.tool_layers[tool][layer_name] in self.project.mapLayers().values():
            layer = self.tool_layers[tool][layer_name]
            if layer not in self.layers:
                self.layers.append(layer)
            return layer

        if layer_name == 'Karttavihjeet':
            name = self.tr(u'Karttavihjeet')
        elif layer_name == 'Pisteet':
            name = self.tr(u'Pisteet')
        elif layer_name == 'Alkupisteet':
            name = self.tr(u'Alkupisteet')
        elif layer_name == 'Loppupisteet':
            name = self.tr(u'Loppupisteet')
        

        point_layer = QgsVectorLayer('Point?crs=epsg:3067', name, 'memory')

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

        self.project.addMapLayer(point_layer, False)
        if group:
            group.addLayer(point_layer)

        if point_layer not in self.layers:
                self.layers.append(point_layer)

        return point_layer


    def delete_all_annotations(self):
        """Deletes all annotations."""
        manager = self.project.annotationManager()
        current_layers = self.project.mapLayers().values()
        for annotation in manager.annotations():
            annotation_layer = annotation.mapLayer()
            if annotation_layer is not None and len(current_layers) > 0:
                for layer in current_layers:
                    if layer.id() == annotation_layer.id():
                        manager.removeAnnotation(annotation)
                        break


    def delete_annotation(self):
        """Deletes one random annotation."""
        manager = self.project.annotationManager()
        current_layers = self.project.mapLayers().values()
        for annotation in manager.annotations():
            annotation_layer = annotation.mapLayer()
            if annotation_layer is not None and len(current_layers) > 0:
                for layer in current_layers:
                    if layer.id() == annotation_layer.id():
                        manager.removeAnnotation(annotation)
                        return

