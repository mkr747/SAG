## Opis agentów
####User Agent:
- user może wgrywac dane testowe
 
#### Data Agent:
- dzieli dane na podobne zbiory pomiędzy węzłami KNN
- jego zadaniem jest ustalenie optymalnej liczby agentów KNN
- rozdystrybuowanie pomiędzy węzłami KNN

#### KNN Agent:
- bierze dane, robi KNN i przekazuje wynikową klasę (z wagą) do Validation agenta
- narazie nic się nie wywala, obsługa błędów w późniejszym etapie

#### Validation Agent:
- Na podstawie wyników z KNN z wagami dochodzi do licytacji, czyli zlicza te same klasy
- przekazuje wynik do User Agenta

Basic wersja: Dane trenujące, z pliku. Ewentualnie, może, jak będzie się nam nudziło to baze sie zrobi

### Serwer xmpp - Prosody

#### Konfiguracja
- conf - katalog zawiera certyfikaty ssl oraz konfugurację serwera 
- prosody_modules - katalog z dodatkowymi modułami (admin, listusers)

#### Uruchamianie

Serwer Prosody XMPP uruchamiamy za pomocą komendy `docker-compose up -d`

Aby Program.py działał trzeba wejść do kontenera 
`docker exec -it <container_name> /bin/bash` i stworzyć użytkowników za pomocą 
komend zawartych w pliku `conf/init_users.sh`

Konsola administratora jest dostępna pod `localhost:5280/admin`