from bs4 import BeautifulSoup
import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError
import re


class Ship:
    def __init__(self):
        self.name = 'NOME NAVE'
        self.imo = 'IMO NAVE'
        self.mmsi = 'MMSI NAVE'
        self.position = {
            'lat': 'LATITUDINE NAVE',
            'long': 'LONGITUDINE NAVE'
        }
        self.course: 'ROTTA NAVE'
        self.speed: 'VELA NAVE'
        self.delay: 'RITARDO'
        self.destination: 'NPOC'

    def __repr__(self):
        return self.name


def format_ship_name(name):
    return name.replace(' ', '-')


def add_ship(ship_string):
    ship = Ship()
    data = ship_string.strip().split(',')
    ship.name = format_ship_name(data[0])
    ship.imo = data[1]
    ship.mmsi = data[2]
    print("Ho trovato...", ship.name, ship.imo, ship.mmsi)
    return ship


def read_ships():
    ship_list = []
    with open('navi-da-cercare.txt') as file:
        for line in file:
            ship_list.append(add_ship(line))
    return ship_list


def print_ship_data(ship_data, output):
    print("="*45, ship_data.name, sep="\n", file=output)
    print(
        f"Posizione: {ship_data.position['lat']} - {ship_data.position['long']}\n", file=output)
    print(
        f"Elementi del moto: Rotta {ship_data.course} - Vela {ship_data.speed} \n", file=output)
    print(f"Porto di destinazione: {ship_data.destination}\n", file=output)
    print(f"Posizione aggiornata a: {ship_data.delay}\n", file=output)
    print("=" * 45 + "\n\n", file=output)


def write_ships(ships):
    print("Sto scrivendo i risultati della ricerca....")
    with open('risultato-ricerca.txt', 'wt', encoding="utf-8") as file:
        file.write(
            f'Ultima ricerca effettuata alle: {datetime.datetime.now()}\n')
        for ship in ships:
            print_ship_data(ship, file)
    print("Scrittura effettuata con successo! Enjoy!")


def extract_destination(soup_element):
    div = soup_element.find("div", class_="ship-section")
    return div.find_all("strong")[1].get_text().strip()


def compile_ship_data(ship, lat, long, course, speed, delay, destination):
    ship.position['lat'] = lat
    ship.position['long'] = long
    ship.course = course
    ship.speed = speed
    ship.delay = delay.split("ago", 1)[0].strip() + ' ago'
    ship.destination = destination
    print(f"Dati di {ship.name} aggiornati con successo...")
    return ship


def extract_ships_data(webpage, ship):
    soup = BeautifulSoup(webpage, 'html.parser')
    lat = soup.find_all("div", class_="coordinate lat")[1].get_text()
    long = soup.find_all("div", class_="coordinate lon")[1].get_text()
    course = soup.find("td", class_="v3").get_text().split('/')[0].strip()
    speed = soup.find("td", class_="v3").get_text().split(
        '/')[1].strip()
    delay = soup.find_all("td", class_="v3")[3].get_text().strip()
    destination = extract_destination(soup)
    compile_ship_data(ship, lat, long, course, speed, delay, destination)


def search_ships(ships):
    for ship in ships:
        ship_page = make_ship_request(ship)
        ship = extract_ships_data(ship_page, ship)
    return ships


def make_ship_request(ship):
    url = f"https://www.vesselfinder.com/vessels/{ship.name}-IMO-{ship.imo}-MMSI-{ship.mmsi}"
    print('Sto scaricando la pagina...', url)
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        print("Pagina scaricata...Sto aggiornando i dati...")
        return webpage
    except URLError as e:
        print(e.reason)
        print("Connection error, closing program")
        quit()


def main():
    print("="*36, "AUTOMATIC SHIPS FINDER BY DIMOLF345",
          "=".lstrip() * 36, sep="\n")
    ship_list = read_ships()
    results = search_ships(ship_list)
    write_ships(results)


if __name__ == '__main__':
    main()
