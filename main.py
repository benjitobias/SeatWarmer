import re
import requests
from bs4 import BeautifulSoup

THEATRE_ID = 3
GET_REQUEST = 'https://globusmax.co.il/theatre_list.aspx?theatresid=%d&eventdate=%s'
RE_EVENT_TIME_ID = r'data-eventid=\"(\d+)\"'

TEMP_TODAY_DATE = "10/11/2016"


class FilmFinder(object):
    def __init__(self, theatre_id, date):
        self.__theatre_id = theatre_id
        self.__date = date
        self.__films = dict()

    def __populate_list_of_films(self):
        get_request = GET_REQUEST % (self.__theatre_id, self.__date)
        films_in_html = requests.get(get_request).text
        self.__convert_html_to_dict(films_in_html)

    def __convert_html_to_dict(self, films_in_html):
        parser = BeautifulSoup(films_in_html, 'html.parser')
        film_info_list = parser.find_all("tr", {"class": "yeshover"})

        for film_info in film_info_list:
            film_name = self.__extract_film_name(film_info)
            if self.__check_if_3d(film_info):
                film_name += ' 3D'
            film_times = self.__extract_film_times(film_info)
            self.__films[film_name] = film_times

    @staticmethod
    def __extract_film_name(film_info):
        film_name = film_info.find_all("td", {"class": "theatre_name movie_name_list"})[0].text
        return film_name

    @staticmethod
    def __extract_film_times(film_info):
        film_times = dict()
        for hour_tag in film_info.find_all("td", {"class": "hour"}):
            time_text = hour_tag.text
            # check time isn't empty string
            if not not time_text:
                film_time_event_id = re.findall(RE_EVENT_TIME_ID, str(hour_tag))
                film_times[time_text] = film_time_event_id[0]
        return film_times

    @staticmethod
    def __check_if_3d(film_info):
        return '3D' in str(film_info)

    def get_films(self):
        return self.__films

    def find_films(self):
        self.__populate_list_of_films()


def write_films_to_file(films):
    with open("c:\\tmp\\film_list.txt", "wb") as film_file:
        for film in films:
            film_file.write("%s\r\n" % film.encode('utf8'))
            for time in films[film]:
                film_file.write("\t%s  " % time.encode('utf8'))
                film_file.write("\t%s\r\n" % films[film][time].encode('utf8'))
            film_file.write("\r\n--------------\r\n")


def main():
    ff = FilmFinder(THEATRE_ID, TEMP_TODAY_DATE)
    ff.find_films()
    write_films_to_file(ff.get_films())


if '__main__' == __name__:
    main()
