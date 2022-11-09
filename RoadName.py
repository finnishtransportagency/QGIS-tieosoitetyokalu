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


import contextlib
import json
from pathlib import Path


class RoadName:


    def __init__(self) -> None:
        path = Path(__file__).parent / "data/tienimi.json"
        self.file_path = path.resolve()


    def get_road_name(self, road_number:int):
        """Retrieves a road name based on the given road number.

        Args:
            road_number (int): Road number.

        Returns:
            (str): Road name.
        """
        with open(self.file_path, 'rb') as file:
            data = json.load(file)
        for road in data:
            with contextlib.suppress(KeyError):
                if road['tie'] == road_number:
                    return road['tienimi']