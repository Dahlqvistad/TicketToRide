import heapq
import math
import random
from collections import defaultdict
from typing import List, Tuple

import pygame

from Button import Button

# =================
# Pygame fönsterkonfiguration

WIDTH = 1439
HEIGHT = 849
FPS = 30

I_WIDTH = 1200
I_HEIGHT = 760

# Bakgrunds- och kortbilder
BACKGROUND_IMAGE = pygame.image.load('ttr_map_europe.JPG')
CARD = pygame.image.load('ttr_card_short.jpeg')
CARD_BLUE = pygame.image.load('ttr_card_long.jpeg')

# Skärminställningar
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()
running = True

# Teckensnitt
font = pygame.font.Font(pygame.font.get_default_font(), 12)
myfont = pygame.font.SysFont("Times New Roman", 20)

# =================
# Färger

LIME = (0, 255, 0)
GRAY = "#Bec1c3"
YELLOW = "#Ffff2e"
BLUE = "#226dc1"
GREEN = "#2dad14"
RED = "#F50707"
DARKGRAY = "#202123"


# =================
# Klasser

class Graph:
    def __init__(self):
        """Initialiserar en graf med städer och deras förbindelser."""
        self.connections = defaultdict(list)  # Förbindelser mellan städer
        self.cities = {}  # Städer och deras koordinater

    def add_city(self, name: str, coords: Tuple[int, int], links: List[Tuple[str, int, int]]):
        """Lägger till en stad i grafen med dess namn, koordinater och länkar till andra städer.
        
        Args:
            name (str): Stadens namn.
            coords (Tuple[int, int]): Stadens koordinater.
            links (List[Tuple[str, int, int]]): Lista över länkar till andra städer (stad, avstånd, vikt).
        """
        self.cities[name] = {"coords": coords, "branches": len(links)}
        for city, distance, weight in links:
            self.connections[name].append({"city": city, "distance": distance, "weight": weight})

    def neighbors(self, city_name):
        """Hämtar alla grannstäder till en given stad.
        
        Args:
            city_name (str): Namnet på staden.

        Returns:
            List[str]: Lista över grannstäder.
        """
        list_connections = []
        connections = self.connections[city_name]
        for cities in connections:
            list_connections.append(cities['city'])
        return list_connections

    def cost(self, pointA, pointB):
        """Hämtar kostnaden mellan två städer.
        
        Args:
            pointA (str): Namnet på startstaden.
            pointB (str): Namnet på slutstaden.

        Returns:
            Tuple[int, str]: Avståndet och namnet på slutstaden.
        """
        connections = self.connections[pointA]
        for cities in connections:
            if cities['city'] == pointB:
                return cities['distance'], cities['city']


# =================
# Funktioner

def route_creater(num_trains):
    """Skapar en rutt och beräknar dess information inklusive kortaste vägen och poäng.
    
    Args:
        num_trains (int): Antal tåg att använda i rutten.

    Returns:
        dict: Information om rutten inklusive koordinater och poäng.
    """
    info_route = {}
    route = route_planner(num_trains)
    info_route["route"] = route

    route_coords = travel_coords(route)
    info_route["route_coords"] = route_coords

    shortest_cost, shortest_path = a_star(route[0], route[-1], graph)
    info_route["shortest_cost"] = shortest_cost
    info_route["shortest_path"] = shortest_path

    shortest_route_coords = travel_coords(shortest_path)
    info_route["shortest_route_coords"] = shortest_route_coords

    points, pointsText = calculate_points(route_coords[0], route_coords[-1], shortest_cost)

    info_route["points"] = points
    info_route["pointsText"] = pointsText

    return info_route


def route_planner(num_trains):
    """Planerar en rutt slumpmässigt baserat på antal tåg.
    
    Args:
        num_trains (int): Antal tåg att använda i rutten.

    Returns:
        List[str]: Lista över städer i rutten.
    """
    route_local = []
    counter = 0

    # Väljer en slumpmässig stad som startpunkt
    list_city = list(graph.cities.keys())
    random_city = random.choice(list_city)
    route_local.append(random_city)

    n = 0
    rand_length_route = num_trains + random.randrange(0, 4)  # Slumpmässig längd på rutten
    while counter <= rand_length_route:
        prev_stop = route_local[n]
        prev_stop_connections = graph.connections[prev_stop]

        next_stop = None
        iterations = 0
        # Väljer nästa stad slumpmässigt
        while next_stop is None or next_stop in route_local:
            prev_stop_index = random.randrange(0, len(prev_stop_connections))
            next_stop = prev_stop_connections[prev_stop_index]['city']
            if iterations > 50:
                return route_local
            iterations += 1

        route_local.append(next_stop)
        for connection in prev_stop_connections:
            if connection["city"] == next_stop:
                counter += connection["distance"]

        n += 1
    return route_local


def travel_coords(travel_route):
    """Hämtar koordinaterna för en given resrutt.
    
    Args:
        travel_route (List[str]): Lista över städer i rutten.

    Returns:
        List[Tuple[int, int]]: Lista över koordinater för rutten.
    """
    route_coords_local = []

    for i in range(len(travel_route)):
        route_coords_local.append(graph.cities[travel_route[i]]['coords'])
    return route_coords_local


def draw_to_screen(route_coordinates, color, size):
    """Ritar en linje på skärmen som representerar en rutt.
    
    Args:
        route_coordinates (List[Tuple[int, int]]): Lista över koordinater för rutten.
        color (Tuple[int, int, int]): Färgen på linjen.
        size (int): Tjockleken på linjen.
    """
    pygame.draw.lines(screen, color, False, route_coordinates, size)


def a_star(start, end, graph_local):
    """A* algoritm för att hitta den kortaste vägen mellan två städer.
    
    Args:
        start (str): Startstadens namn.
        end (str): Slutstadens namn.
        graph_local (Graph): Grafen som representerar städer och deras förbindelser.

    Returns:
        Tuple[int, List[str]]: Kostnaden och vägen mellan start och slut.
    """
    heap = [(0, start, [start])]
    visited = set()
    while heap:
        (cost, node, path) = heapq.heappop(heap)
        if node == end:
            return cost, path
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph_local.neighbors(node):
            if neighbor in visited:
                continue
            new_cost = cost + graph_local.cost(node, neighbor)[0]
            new_path = path + [graph_local.cost(node, neighbor)[1]]
            heapq.heappush(heap, (new_cost, neighbor, new_path))
    return None


def start_game(num_trains, num_routes):
    """Startar spelet och genererar rutter.
    
    Args:
        num_trains (int): Antal tåg att använda i varje rutt.
        num_routes (int): Antal rutter att generera.

    Returns:
        List[dict]: Lista över information om varje rutt.
    """
    global list_routes
    list_routes = []

    for i in range(num_routes):
        list_routes.append(route_creater(num_trains))

    return list_routes


def calculate_points(pointA, pointB, trains_used):
    """Beräknar poängen för en rutt baserat på avstånd och antal använda tåg.
    
    Args:
        pointA (Tuple[int, int]): Startpunktens koordinater.
        pointB (Tuple[int, int]): Slutpunktens koordinater.
        trains_used (int): Antal använda tåg.

    Returns:
        Tuple[int, pygame.Surface]: Poängen och textytan för poängen.
    """
    points = 0
    euclidean_dist = math.dist(pointA, pointB)
    points += math.sqrt(euclidean_dist) / 7
    points += trains_used / 2
    points += random.randrange(0, 3)

    points = points.__floor__()

    pointText = pygame_text(points)

    return points, pointText


def pygame_text(text):
    """Renderar text för att visas i Pygame.
    
    Args:
        text (int): Texten som ska renderas.

    Returns:
        pygame.Surface: Ytan med renderad text.
    """
    text = myfont.render(str(text).upper(), False, (0, 0, 0))
    return text


def lsh():
    """LSH-algoritm för att kategorisera st

äder och välja start- och slutstad för en lång rutt.
    
    Returns:
        Tuple[str, str]: Start- och slutstadens namn.
    """
    list_cities = list(graph.cities.keys())

    categorized_cities = {}

    for city in list_cities:
        coords = graph.cities[city]['coords']

        str_city = point_side_of_line(LSH_BLUE_COORDS[0][0], LSH_BLUE_COORDS[0][1], LSH_BLUE_COORDS[1][0], LSH_BLUE_COORDS[1][1], coords[0], coords[1])
        str_city += point_side_of_line(LSH_GREEN_COORDS[0][0], LSH_GREEN_COORDS[0][1], LSH_GREEN_COORDS[1][0], LSH_GREEN_COORDS[1][1], coords[0], coords[1])
        str_city += point_side_of_line(LSH_YELLOW_COORDS[0][0], LSH_YELLOW_COORDS[0][1], LSH_YELLOW_COORDS[1][0], LSH_YELLOW_COORDS[1][1], coords[0], coords[1])

        if coords[0] < LSH_RED_COORDS[0][0]:
            str_city += "L"
        else:
            str_city += "R"

        if str_city in categorized_cities:
            categorized_cities[str_city].append(city)
        else:
            categorized_cities[str_city] = [city]

    ALL_COMBINATIONS = list(categorized_cities.keys())

    selected_combination = random.choice(ALL_COMBINATIONS)
    opposite_combination = generate_opposite_combination(selected_combination)

    start_city = random.choice(categorized_cities[selected_combination])
    end_city = random.choice(categorized_cities[opposite_combination])
    return start_city, end_city


def point_side_of_line(x1, y1, x2, y2, a, b):
    """Avgör vilken sida av en linje en punkt ligger på.
    
    Args:
        x1, y1, x2, y2 (int): Koordinater för linjens ändpunkter.
        a, b (int): Koordinater för punkten.

    Returns:
        str: "L" om punkten ligger till vänster, annars "R".
    """
    cross_product = (x2 - x1) * (b - y1) - (y2 - y1) * (a - x1)
    if cross_product < 0:
        return "L"
    else:
        return "R"


def generate_opposite_combination(combinations):
    """Genererar den motsatta kombinationen av en given kombination av "L" och "R".
    
    Args:
        combinations (str): Den ursprungliga kombinationen.

    Returns:
        str: Den motsatta kombinationen.
    """
    opposite_combination = ""
    for char in combinations:
        if char == "L":
            opposite_combination += "R"
        else:
            opposite_combination += "L"
    return opposite_combination


def long_route():
    """Skapar en lång rutt mellan två städer som valts med LSH-algoritmen."""
    global list_routes
    list_routes = []
    list_routes_dict = {}

    start_city, end_city = lsh()
    shortest_cost, shortest_path = a_star(start_city, end_city, graph)

    list_routes_dict['route'] = shortest_path
    list_routes_dict['shortest_route_coords'] = travel_coords(shortest_path)
    list_routes_dict['route_coords'] = travel_coords(shortest_path)

    list_routes.append(list_routes_dict)

    return


# =================
# Definiera alla städer
# Lägg till alla noder (städer) samt kanter (räls) mellan dem tillsammans med koordinaterna för städerna på bilden

graph = Graph()

# Exempel på att lägga till städer och deras förbindelser
graph.add_city("edinburgh", (173, 34), [("london", 4, 0)])
graph.add_city("london", (254, 213), [("amsterdam", 2, 0), ("dieppe", 2, 0), ("edinburgh", 4, 0)])
graph.add_city("amsterdam", (371, 224), [("london", 2, 0), ("essen", 3, 0), ("bruxelles", 1, 0), ("frankfurt", 2, 0)])
graph.add_city("dieppe", (239, 327), [("london", 2, 0), ("paris", 1, 0), ("brest", 2, 0), ("bruxelles", 2, 0)])
graph.add_city("essen", (472, 232), [("amsterdam", 3, 0), ("frankfurt", 2, 0), ("berlin", 2, 0), ("kobenhavn", 3, 0)])
graph.add_city("bruxelles", (345, 282), [("frankfurt", 2, 0), ("paris", 2, 0), ("dieppe", 2, 0), ("amsterdam", 1, 0)])
graph.add_city("frankfurt", (457, 318), [("munchen", 2, 0), ("paris", 3, 0), ("bruxelles", 2, 0), ("amsterdam", 2, 0), ("essen", 2, 0), ("berlin", 3, 0)])
graph.add_city("paris", (302, 382), [("bruxelles", 2, 0), ("dieppe", 1, 0), ("brest", 3, 0), ("pamplona", 4, 0), ("marseille", 4, 0), ("zurich", 3, 0), ("frankfurt", 3, 0)])
graph.add_city("brest", (135, 362), [("dieppe", 2, 0), ("paris", 3, 0), ("pamplona", 4, 0)])
graph.add_city("munchen", (520, 374), [("frankfurt", 2, 0), ("zurich", 2, 0), ("venezia", 2, 0), ("wien", 3, 0)])
graph.add_city("kobenhavn", (553, 104), [("essen", 3, 0), ("stockholm", 3, 0)])
graph.add_city("stockholm", (681, 14), [("kobenhavn", 3, 0), ("petrograd", 8, 0)])
graph.add_city("berlin", (593, 250), [("danzig", 4, 0), ("essen", 2, 0), ("frankfurt", 3, 0), ("wien", 3, 0), ("warszawa", 4, 0)])
graph.add_city("wien", (660, 393), [("berlin", 3, 0), ("munchen", 3, 0), ("zagrab", 2, 0), ("warszawa", 4, 0), ("budapest", 1, 0)])
graph.add_city("zurich", (441, 448), [("paris", 3, 0), ("marseille", 2, 0), ("venezia", 2, 0), ("munchen", 2, 0)])
graph.add_city("marseille", (409, 566), [("barcelona", 4, 0), ("pamplona", 4, 0), ("paris", 4, 0), ("zurich", 2, 0), ('roma', 4, 0)])
graph.add_city("pamplona", (224, 565), [("madrid", 3, 0), ("barcelona", 2, 0), ("marseille", 4, 0), ("brest", 4, 0), ('paris', 4, 0)])
graph.add_city("madrid", (102, 666), [("lisboa", 3, 0), ("cadiz", 3, 0), ("pamplona", 3, 0), ("barcelona", 2, 0)])
graph.add_city("lisboa", (23, 696), [("madrid", 3, 0), ("cadiz", 2, 0)])
graph.add_city("cadiz", (105, 754), [("lisboa", 2, 0), ("madrid", 3, 0)])
graph.add_city("barcelona", (241, 675), [("madrid", 2, 0), ("pamplona", 2, 0), ("marseille", 4, 0)])
graph.add_city("roma", (550, 600), [("marseille", 4, 0), ("venezia", 2, 0), ("brindisi", 2, 0), ("palermo", 4, 0)])
graph.add_city("venezia", (543, 487), [("roma", 2, 0), ("zurich", 2, 0), ("munchen", 2, 0), ("zagrab", 2, 0)])
graph.add_city("danzig", (728, 158), [("berlin", 4, 0), ("warszawa", 2, 0), ("riga", 3, 0)])
graph.add_city("riga", (829, 47), [("danzig", 3, 0), ("wilno", 4, 0), ("petrograd", 4, 0)])
graph.add_city("petrograd", (1033, 42), [("stockholm", 8, 0), ("wilno", 4, 0), ("moskva", 4, 0), ("riga", 4, 0)])
graph.add_city("warszawa", (789, 236), [("danzig", 2, 0), ("berlin", 4, 0), ("wien", 4, 0), ("wilno", 3, 0), ("kyiv", 4, 0)])
graph.add_city("wilno", (926, 205), [("warszawa", 4, 0), ("riga", 4, 0), ("petrograd", 4, 0), ("smolensk", 3, 0), ("kyiv", 2, 0)])
graph.add_city("smolensk", (1051, 215), [("wilno", 3, 0), ("moskva", 2, 0), ("kyiv", 3, 0)])
graph.add_city("moskva", (1145, 184), [("petrograd", 4, 0), ("smolensk", 2, 0), ("kharkov", 4, 0)])
graph.add_city("kyiv", (977, 301), [("wilno", 2, 0), ("smolensk", 3, 0), ("warszawa", 4, 0), ("budapest", 6, 0), ("bucuresti", 4, 0), ("kharkov", 4, 0)])
graph.add_city("kharkov", (1131, 368), [("kyiv", 4, 0), ("moskva", 4, 0), ("rostov", 2, 0)])
graph.add_city("rostov", (1186, 430), [("kharkov", 2, 0), ("sevastopol", 4, 0), ("sochi", 2, 0)])
graph.add_city("budapest", (717, 420), [("wien", 1, 0), ("zagrab", 2, 0), ("sarajevo", 3, 0), ("bucuresti", 4, 0), ("kyiv", 6, 0)])
graph.add_city("bucuresti", (897, 502), [("kyiv", 4, 0), ("budapest", 4, 0), ("sofia", 2, 0), ("constantinopel", 3, 0), ("sevastopol", 4, 0)])
graph.add_city("sevastopol", (1072, 523), [("bucuresti", 4, 0), ("rostov", 4, 0), ("sochi", 2, 0), ("erzurum", 1, 0), ("constantinopel", 4, 0)])
graph.add_city("sochi", (1173, 539), [("rostov", 2, 0), ("sevastopol", 2, 0), ("erzurum", 3, 0)])
graph.add_city("erzurum", (1153, 690), [("sevastopol", 4, 0), ("sochi", 3, 0), ("angora", 3, 0)])
graph.add_city("constantinopel", (962, 654), [("sevastopol", 4, 0), ("angora", 2, 0), ("smyrna", 2, 0), ("sofia", 3, 0), ("bucuresti", 3, 0)])
graph.add_city("angora", (1057, 718), [("smyrna", 3, 0), ("erzurum", 3, 0), ("angora", 2, 0)])
graph.add_city("smyrna", (911, 750), [("constantinopel", 2, 0), ("angora", 2, 0), ("athina", 2, 0), ("palermo", 6, 0)])
graph.add_city("sofia", (827, 579), [("athina", 3, 0), ("sarajevo", 2, 0), ("bucuresti", 2, 0), ("constantinopel", 3, 0)])
graph.add_city("sarajevo", (750, 572), [("zagrab", 3, 0), ("budapest", 3, 0), ("sofia", 2, 0), ("athina", 4, 0)])
graph.add_city("zagrab", (650, 500), [("sarajevo", 3, 0), ("venezia", 2, 0), ("wien", 2, 0), ("budapest", 2, 0)])
graph.add_city("brindisi", (650, 625), [("venezia", 4, 0), ("palermo", 3, 0), ("athina", 4, 0)])
graph.add_city("athina", (804, 720), [("sarajevo", 4, 0), ("sofia", 3, 0), ("smyrna", 2, 0), ("brindisi", 5, 0)])
graph.add_city("palermo", (593, 750), [("roma", 4, 0), ("brindisi", 3, 0), ("smyrna", 6, 0)])


# =================

# (x1, x2), (y1, y2)
# LSH-koordinater för att kategorisera städer
LSH_BLUE_COORDS = ((0, 0), (I_WIDTH, I_HEIGHT))
LSH_GREEN_COORDS = ((0, I_HEIGHT/2), (I_WIDTH, I_HEIGHT/2))
LSH_YELLOW_COORDS = ((0, I_HEIGHT), (I_WIDTH, 0))
LSH_RED_COORDS = ((I_WIDTH/2, 0), (I_WIDTH/2, 760))


# =================

start_game(9, 3) # Startar spelet och genererar rutter med 9 tåg och 3 rutter
# Skapar två knappar som kommer att användas för att starta nya rutter, blir placerade bakom bilderna
rectangle = Button(BLUE, 260, 710, 250, 142)
rectangle_blue = Button(BLUE, 1200, 710, 250, 142)

lsh()

# =================
# Pygame spel-loop

# Initierar klockan för att kontrollera spelets FPS
clock = pygame.time.Clock()
while running:
    # Sätter spelets FPS
    clock.tick(FPS)
    
    # Hanterar händelser (events) som användarinteraktioner
    for event in pygame.event.get():
        # Om användaren klickar på stängningsknappen
        if event.type == pygame.QUIT:
            running = False
        
        # Om användaren klickar med musen
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Om användaren klickar på rektangeln (startar nya rutter)
            if rectangle.isOver(pos):
                start_game(9, 3)
            # Om användaren klickar på blåa rektangeln (genererar en lång rutt)
            if rectangle_blue.isOver(pos):
                long_route()
    
    # Hämtar musens position
    pos = pygame.mouse.get_pos()

    # Fyller skärmen med grå bakgrundsfärg
    screen.fill(GRAY)
    # Visar bakgrundsbilden på skärmen
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    # Visar kortbilden på skärmen
    screen.blit(CARD, (260, 710))
    # Visar blå kortbilden på skärmen
    screen.blit(CARD_BLUE, (1200, 710))

    # Lista över färger för rutterna
    colors = [BLUE, GREEN, YELLOW, RED, DARKGRAY]
    counter_loop = 0

    # Loopar genom varje rutt i list_routes
    for j in list_routes:
        try:
            # Sätter färgen för den nuvarande rutten
            COLOR = colors[counter_loop]
            # Ritar den kortaste rutten på skärmen
            draw_to_screen(j['shortest_route_coords'], COLOR, 8)
            # Ritar cirklar vid start- och slutpunkten för rutten
            pygame.draw.circle(screen, COLOR, j['route_coords'][0], 10)
            pygame.draw.circle(screen, COLOR, j['route_coords'][-1], 10)
            
            # Visar start- och slutstaden för rutten på skärmen
            screen.blit(pygame_text(j['route'][0]), (1270, 155*counter_loop+75))
            screen.blit(pygame_text(j['route'][-1]), (1270, 155 * counter_loop + 130))
            
            # Ritar hela rutten på skärmen
            draw_to_screen(j['route_coords'], COLOR, 2)
            
            # Ritar en cirkel vid ruttnumrets position
            pygame.draw.circle(screen, COLOR, (1220, 150*counter_loop+100), 10)
            
            # Visar poängen för rutten på skärmen
            screen.blit(j['pointsText'], (1237, (150*counter_loop + 80)))
            
            # Ökar räknaren för att byta färg för nästa rutt
            counter_loop += 1
        except:
            continue

    # Uppdaterar displayen för att visa alla ändringar
    pygame.display.update()