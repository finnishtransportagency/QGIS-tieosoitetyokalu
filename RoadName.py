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
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        for road in data:
            with contextlib.suppress(KeyError):
                if road['tie'] == road_number:
                    return road['tienimi']