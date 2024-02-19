Pakiet służy do analizy danych związanych z API urzędu miasta Warszawy. 
Jest podzielony na 4 części, pobieranie, wczytywanie, analiza i wizualizacja danych.
Dodatkowo w folderze scripts umieszczono dwa entry points umożliwiające oddzielnie pobieranie danych (main_download.py) oraz analizę i wizualizację (main.py)

Aby pobieranie danych działało należy stworzyć plik .env w którym umieści się stałą API_KEY, którą można otrzymać przez zalogowanie się w serwisie api.um.warszawa.pl

W pakiecie nie są zawarte żadne dane,
do sprawdzenia prędkości autobusów należy podać plik z ich lokalizacjami bądź puścić skrypt pobierający ich pozycję,
do sprawdzenia punktualności autobusów wymagane są dodatkowo pliki pobierane przez opcje (--stoploc --buslines, --schedule) w skrypcie main_download.py (te opcje to odpowiednio lokalizacje przystanków, linie przechodzące przez przystanki i rozkład jazdy autobusów)
