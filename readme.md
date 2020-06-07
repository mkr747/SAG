User Agent:
- user może wgrywac dane testowe
 
Data Agent:
- dzieli dane na podobne zbiory pomiędzy węzłami KNN
- jego zadaniem jest ustalenie optymalnej liczby agentów KNN
- rozdystrybuowanie pomiędzy węzłami KNN

KNN Agent:
- bierze dane, robi KNN i przekazuje wynikową klasę (z wagą) do Validation agenta
- narazie nic się nie wywala, obsługa błędów w późniejszym etapie

Validation Agent:
- Na podstawie wyników z KNN z wagami dochodzi do licytacji, czyli zlicza te same klasy
- przekazuje wynik do User Agenta

Basic wersja: Dane trenujące, z pliku. Ewentualnie, może, jak będzie się nam nudziło to baze sie zrobi