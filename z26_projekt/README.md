# Struktury globalne: (koniecznie mutexowane)

## globals.py

-   stan wszystkich plików w naszym folderze
    -   nazwa
    -   data modyfikacji
    -   status
        -   aktualny
        -   do pobrania (zamówienie w kolejce)
        -   pobierany
        -   usunięty
-   aktualne połączenia
    -   adres IP
    -   port
    -   socket?
    -   kolejka wiadomości do wysłania

# Wątki:

## udp_server.py

wątek do wysyłania UDP + potencjalnie odbierania

-   inicjalizuje połączenia TCP i uruchamia dla nich wątki
-   uruchomiony na starcie

## tcp_server.py

wątek serwera TCP

-   przyjmuje połączenia TCP i uruchamia dla nich wątki
-   uruchomiony na starcie

## folder_scanner.py

wątek do skanowania naszego folderu co 30s

-   dodaje wiadomość file_list do kolejki każdego połączenia
-   uruchomiony na starcie

## tcp_handler.py

wątki dla każdego połączenia TCP

-   każdy ma swoją kolejkę wiadomości do wysłania
-   na podstawie informacji o długości wiadomości pobiera całą do bufora, a następnie parsuje przy pomocy `data_parser.py`
-   przetwarza odebrane wiadomości
    -   dodaje wiadomości file_request do kolejki, jak wyjdą jakieś aktualizacje na podstawie file_list
        -   jeżeli ta aktualizacja jest najnowsza, to anuluje wszystkie inne file_request z kolejek
    -   dodaje wiadomości file_transmission do kolejki, jak ktoś zamówi
    -   zapisuje i deszyfruje na dysk zawartość z file_transmission

## gui.py

wątek do wyświetlania logów i statusu

-   kolejka wiadomości do wyświetlenia w logu
-   co jakiś czas wyświetla wartości zmiennych globalnych
