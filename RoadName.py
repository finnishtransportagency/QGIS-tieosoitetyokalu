from pathlib import Path


class RoadName:
    

    def __init__(self) -> None:
        path = Path('data/tienimi.json')
        self.file_path = path.resolve()


    def get_road_name(self, road_number:int):
        with open(self.file_path, 'r') as file:
            for row in file:
                if row['tie'] == road_number:
                    return row['tienimi']
