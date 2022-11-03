from pathlib import Path


class RoadName:
    

    def __init__(self) -> None:
        working_dir = str(Path.cwd())
        self.file_path = f'{working_dir}/data/tienimi.json'


    def get_road_name(self, road_number:int):
        with open(self.file_path, 'r') as file:
            for row in file:
                if row['tie'] == road_number:
                    return row['tienimi']
