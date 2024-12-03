import json
import networkx as nx


def _get_reachable_locations(graph, start_id, max_distance):
    paths = nx.single_source_shortest_path_length(graph, int(start_id), cutoff=max_distance)
    return [node for node in paths.keys() if node != int(start_id)]


class GameMap:
    def __init__(self, json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            self.locations = json.load(file)

        self.graph_walk = nx.Graph()
        self.graph_sea = nx.Graph()
        self.graph_railway_white = nx.Graph()
        self.graph_railway_yellow = nx.Graph()

        self._build_graphs()

    def _build_graphs(self):
        for location in self.locations:
            loc_id = location["id"]

            self.graph_walk.add_node(loc_id)
            self.graph_sea.add_node(loc_id)
            self.graph_railway_white.add_node(loc_id)
            self.graph_railway_yellow.add_node(loc_id)

            for nearby_id in location.get("cities_nearby", []):
                self.graph_walk.add_edge(loc_id, nearby_id)

            for sea_id in location.get("seas_ports_nearby", []):
                self.graph_sea.add_edge(loc_id, sea_id)

            for railway_id in location.get("cities_railway_white", []):
                self.graph_railway_white.add_edge(loc_id, railway_id)

            for railway_id in location.get("cities_railway_yellow", []):
                self.graph_railway_yellow.add_edge(loc_id, railway_id)

    def get_locations_walk(self, start_id, distance):
        return _get_reachable_locations(self.graph_walk, start_id, distance)

    def get_locations_sea(self, start_id, distance):
        return _get_reachable_locations(self.graph_sea, start_id, distance)

    def get_locations_railway(self, start_id, white_steps, yellow_steps):

        reachable_by_white = set()
        to_visit_white = {start_id}

        for _ in range(white_steps):
            next_visit_white = set()
            for loc in to_visit_white:
                neighbors = set(self.graph_railway_white.neighbors(loc))
                next_visit_white.update(neighbors)

            reachable_by_white.update(next_visit_white)
            to_visit_white = next_visit_white

        reachable_by_yellow = {start_id}

        for _ in range(yellow_steps):
            next_visit_yellow = set()

            for loc in reachable_by_yellow:
                neighbors_yellow = set(self.graph_railway_yellow.neighbors(loc))
                next_visit_yellow.update(neighbors_yellow)

                neighbors_white = set(self.graph_railway_white.neighbors(loc))
                next_visit_yellow.update(neighbors_white)

            reachable_by_yellow.update(next_visit_yellow)

        return reachable_by_white | reachable_by_yellow

    def find_by_id(self, id):
        for location in self.locations:
            if location["id"] == int(id):
                return location
