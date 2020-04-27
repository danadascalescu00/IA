"""
    Copii sunt asezati pe randuri, in banci de cate doua persoane. Bancile sunt dispuse in 3 coloane.
    Un copil poate transmite mesajul(biletul) catre colegul de banca sau catre colegul din spatele sau sau din fata sa, 
    insa nu si pe diagonala. De asemenea, trecerea biletelului de pe un rand pe altul este mai anevoioasa, deoarece poate fi vazut foarte usor 
    de catre profesor, de aceea singurele banci intre care se poate face transferul sunt penultimele si ultimele de pe fiecare rand.
    Copilul vrea sa scrie pe bilet drumul pe care trebuie sa-l parcurga, de la un coleg la altul, pentru a fi sigur ca nu se 
    rataceste prin clasa si nu mai ajunge la prietenul sau pana la inceputul pauzei.
"""

import re
import sys
import copy
import timeit

input_file_prefix, file_format = '231_Dăscălescu_Dana_Lab6_Pb4_input_', '.txt'
output_file_prefix = '231_Dăscălescu_Dana_Lab6_Pb4_output_'
index_files = [1, 2, 3, 4]

"""
    Admisibilitatea algoritmului
    Conditii:
    - Orice nod al grafului, daca admite succesori, are un numar finit de succesori
    - Toate arcele din graf au coturi mai mari decat o cantitate pozitiva µ
    - Pentru toate nodurile n din graful de cautare, h^(n) <= h(n), aidcă h^ niciodata nu supraestimeaza valoarea efectiva a lui h
        Atunci cand sunt indeplinite conditiile asupra grafurilor si asupra lui h^ enuntate anterior si cu
    conditia sa existe un drum de cost finit de la nodul initial, n0, la un nod scop, algoritmul A* garanteaza
    gasirea unui drum de cost minim la un nod scop.

    Functia euristica trebuie sa fie admisibila, ceea ce inseamna ca nu poate sa supraestimeze niciodata costul pentru atingerea obiectivului.
    Utilizarea unei euristici bune este importanta in determinarea perfomantei algoritmului A*
    Ideal valoarea lui h^(n) ar fi fost egala cu costul exact al atingerii distantei. Totusi, in realitate, acest lucru nu este posibil,
    deoarece nu stim peste ce obstacole putem da. Totusi, putem sa alegem o metoda care sa nu ofere valoare exacta in cateva dati, 
    un astfel de exemplu ar fi deplasarea in linia dreapta, fara obstacolem caz in care am avea o performanta perfecta.
"""


""" Definire problema """

class Configuratie:
    def __init__(self, matrice, mesaj):
        self.matrice = matrice
        self.asezare_in_banci = self.asezare()
        self.poz_mesaj = self.get_pozitie(mesaj)    # pozitia copilului la care se afla biletelul in clasa 

    """
        Complexitatea timpului (amortizat) este constantă (O(1)) în mărimea dicționarului, atat pentru inserare, cautare, cat si stergere, 
        deoarece in Python dictionarele sunt implementate ca hash tables.
    """
    def asezare(self):
        """
            Vom salva intr-un dictionar pozitiile copiilor in banci: cheia este reprezentata de numele copilului, iar valoarea de
            un tuplu (i,j) ce reprezinta pozitia sa in clasa, i este randul pe care sta copilul si j coloana
        """
        asezare = {}
        for i, rand in enumerate(self.matrice):
            for j, copil in enumerate(rand):
                asezare[copil] = (i, j)
        return asezare


    def get_pozitie(self, nume_copil):
        return self.asezare_in_banci.get(nume_copil)
    

    """
        Euristici admisibila:
        I) Manhattan Distance - Distanta dintre doua puncte masurate de-a lungul axelor in unghi drept.
            Intr-un plan cu punctele P1(x1, y1) si P2(x2, y2) este egala cu |x1 - x2| + |y1 - y2|.
            Distanta Manhattan este adesea utilizata atunci cand putem sa ne deplasam doar in patru directii(Nord, Vest, Sud , Est).
            Intrucat, un copil poate transmite mesajul(biletul) catre colegul de banca sau catre colegul din spatele sau sau din fata, 
            insa nu si pe diagonala, am ales distanta Manhatan pentru evaloare euristica a unui nod.

        II) Diagonal distance - este adesea folosita cand ne putem deplasa in opt directii, asemanator regelui pe tabla de sah:
                        NV           N              NE
                            \        |          /
                        V  --   current_cell    --   E
                            /        |          \
                        SV           S              SE

        III) Distanta Euclidiana- este adesea fiolosita cand ne putem deplasa pe orice directie.
            Chiar daca distanta Euclidiana este mai mica decat distanta Manhattan sau distanta diagonala, si, in continuare vom avea
            drumul de cost minim de la un nod start la un nod scop, algoritmull A*, cu aceasta euristica va dura mai mult pentru a rula.

        Un caz particular al lui A* este algoritmul breadth-first. In acest caz avem f^(n) = g^(n) = adancime(n) pentru orice nod din graful 
        de cautare n, deci h = 0, prin urmare aceasta este o euristica admisibila, dar nu ofera performanta cautarii(este o cautare neinformata).
    """
    def distanta_manhattan(self):
        global configuratie_finala
        return abs(self.poz_mesaj[0] - configuratie_finala.poz_mesaj[0]) + abs(self.poz_mesaj[1] - configuratie_finala.poz_mesaj[1])

    def distanta_diagonala(self):
        global configuratie_finala
        return max(abs(self.poz_mesaj[0] - configuratie_finala.poz_mesaj[0]), abs(self.poz_mesaj[1] - configuratie_finala.poz_mesaj[1]))

    def __eq__(self, other):
        return self.poz_mesaj == other.poz_mesaj

    def __repr__(self):
        return f"{self.matrice[self.poz_mesaj[0]][self.poz_mesaj[1]]}"


class Nod:
    def __init__(self, configuratie):
        self.info = configuratie
        self.h = configuratie.distanta_manhattan()

    def __str__(self):
        return "{}".format(self.info)
    
    def __repr__(self):
        return f"{self.info}"


class Arc:
    def __init__(self, capat, varf):
        self.capat = capat
        self.varf = varf
        self.cost = 1 # Transmiterea unui mesaj de la un copil la altul are costul 1
    

class Problema:
    def __init__(self, configuratie_initiala, configuratie_finala):
        self.noduri = [
            Nod(configuratie_initiala)
        ]
        self.arce = []
        self.nod_start = self.noduri[0]
        self.nod_scop = configuratie_finala

    def cauta_nod_nume(self, info):
        # Stiind doar informatia "info" a unui nod, trebuie returnata fie obiectul de tip Nod care are acea informatie ori None
        for nod in noduri:
            if nod.info == info:
                return nod

""" Sfarsit definire problema """

class NodParcurgere:
    """
        O clasa care cuprinde informatiile asociate unui nod din listele open/closed.
        Cuprinde o referinta catre nodul in sine(din graf), dar are ca proprietati si valorile specifice algoritmului A*(functia
        euristica de evaluare f, si g, o estimatie a adancimii unui nod n in graf, adica lungimea celui mai scurt drum de la nodul de start la n)
        Se presupune ca h(evaluarea euristica a unui nod) este o proprietate a nodului din graf.
    """
    problema = None

    def __init__(self, nod_graf, nod_parinte = None, g = 0, f = None):
        self.nod_graf = nod_graf            # obiect de tip nod
        self.nod_parinte = nod_parinte      # obiect de tip nod
        self.g = g  # costul drumului de la radacina pana la nodul curent
        if f is None:
            self.f = self.g + self.nod_graf.h
        else:
            self.f = f

    def drum_arbore(self):
        # Functia "construieste" drumul asociat unui nod din arborele de cautare. Aceasta merge din parinte in parinte pana ajunge la radacina.
        nod_curent = self
        drum = [nod_curent.nod_graf]
        while nod_curent.nod_parinte is not None:
            drum = [nod_curent.nod_parinte] + drum
            nod_curent = nod_curent.nod_parinte
        return drum
    
    def contine_in_drum(self, nod):
        nod_curent = self
        while nod_curent.nod_parinte is not None:
            if nod_curent.nod_graf.info == nod.info:
                return True
            nod_curent = nod_curent.nod_parinte
        return False

    def expandeaza(self):
        # metoda returneaza o lista cu toti succesorii posibili ai nodului current
        global numar_randuri, numar_coloane, clasa

        pozitie_actuala_mesaj = self.nod_graf.info.poz_mesaj
        miscari_valide = [[1,0], [0,1], [0,-1], [-1,0]]

        succesori = []
        for mutare in miscari_valide:
            pozitie_noua = [pozitie_actuala_mesaj[0] + mutare[0], pozitie_actuala_mesaj[1] + mutare[1]]
            # Verificam daca noua pozitie este una valida
            if pozitie_noua[0] >= 0 and pozitie_noua[0] < numar_randuri and pozitie_noua[1] >= 0 and pozitie_noua[1] < numar_coloane:
                nume1 = clasa[pozitie_actuala_mesaj[0]][pozitie_actuala_mesaj[1]]
                nume2 = clasa[pozitie_noua[0]][pozitie_noua[1]]
                if poate_da_mai_departe_mesajul(nume1, nume2):
                    clasa_noua = copy.deepcopy(clasa)
                    configuratie_noua_clasa = Configuratie(clasa_noua, nume2)
                    succesor = Nod(configuratie_noua_clasa)
                    succesori.append((succesor, 1))
        return succesori
        

    def test_scop(self):
        return self.nod_graf.info == self.problema.nod_scop

    def __str__ (self):
        parinte = self.nod_parinte if self.nod_parinte is None else self.nod_parinte.nod_graf.info
        if parinte is None:
            return f"{self.nod_graf}"
        else:
            poz1, poz2 = self.nod_parinte.nod_graf.info.poz_mesaj, self.nod_graf.info.poz_mesaj
            if poz1[0] > poz2[0]:
                return f" ^  {self.nod_graf}"
            elif poz1[0] < poz2[0]:
                return f" v  {self.nod_graf}"
            elif poz1[1] < poz2[1]:
                if poz1[1] % 2 == 1:
                    return f" >> {self.nod_graf}"
                return f" > {self.nod_graf}"
            elif poz1[1] > poz2[1]:
                if poz1[1] % 2 == 1:
                    return f" << {self.nod_graf}"
                return f" < {self.nod_graf}"
            return f"{self.nod_graf}"


def sunt_suparati(copil1, copil2):
    global sunt_suparati

    for pereche in copii_suparati:
        if (copil1 == pereche[0] and copil2 == pereche[1]) or (copil2 == pereche[0] and copil1 == pereche[1]):
            return True
    return False

# Verifica daca mesajul(biletelul) poate fi dat transmis mai departe de la banca1 la banca2
def poate_da_mai_departe_mesajul(banca1, banca2):
    # Copii nu isi modifica pozitiile in banci pe parcursul orei si din acest motiv pozitiile lor vor fi aceleasi indiferent de configuratie,
    # ceea ce se modifica in schimb este pozitia mesajului
    global configuratie_initiala
    global numar_randuri

    if "liber" in banca1 or "liber" in banca2:
        return False
    elif sunt_suparati(banca1, banca2):
        return False
    else:
        poz1, poz2 = configuratie_initiala.get_pozitie(banca1), configuratie_initiala.get_pozitie(banca2)
        if poz1[1] > poz2[1]:
            poz1, poz2 = poz2, poz1
        
        # Verificam daca copii se afla pe coloane diferite
        if (poz1[1] % 2 == 1 and poz2[1] % 2 == 0):
            #Copii pot trimite un biletel de pe o colona pe alta doar daca se afla in ultimele doua randuri(obligatoriu pe acelasi rand)
            if poz1[0] != poz2[0]:
                return False
            if poz1[0] < numar_randuri - 2:
                return False
        # In cazul in care se afla pe aceeasi coloana, verificam daca copii sunt colegi de banca sau daca sunt pe randuri diferite acestia 
        # trebuie sa se afle unul in spatelui celuilalt(nu pot transmite mesajul pe diagonala)
        elif poz1[0] != poz2[0] and poz1[1] != poz2[1]:
            return False 
    
    return True


""" Algoritmul A* """

def str_info_noduri(l):
    global clasa
    numar_randuri = len(clasa)

    sir = "["
    poz_trecut  = [-1,-1]
    for x in l:
        sir += str(x) + "  "
    sir += "]"
    return sir


def afis_succesori_cost(l):
	sir = ""
	for (x, cost) in l:
		sir += "\nnod: "+ str(x)+", cost arc:"+ str(cost)
	return sir


def in_lista(l, nod):
    for i in range(len(l)):
        if l[i].nod_graf.info == nod.info:
            return l[i]
    return None


def a_star(nume_fisier_scriere):
    """
		Functia care implementeaza algoritmul A-star
	"""
    start_time = timeit.default_timer()

    # Se creeaza un graf de cautare G, constand din nodul initial n0. Se creeaza listele vide OPEN si CLOSED. 
    # In lista OPEN se adauga nodul-start, n0.
    radacina_arbore = NodParcurgere(NodParcurgere.problema.nod_start)
    OPEN = [radacina_arbore]  # OPEN va contine elemente de tip NodParcurgere
    closed = []  # closed va contine elemente de tip NodParcurgere
    nod_scop_gasit = False

    # Daca lista OPEN este vida, EXIT=>esec. Alfel urmatorii pasi se executa cat timp lista OPEN mai contine elemente de tip NodParcurgere
    while len(OPEN) > 0:
        nod_curent = OPEN.pop(0)	# scoatem primul element din lista OPEN
        closed.append(nod_curent)	# si il adaugam la finalul listei closed

        # Testez daca nodul extras din lista OPEN este nod scop. Daca n este nod scop, atunci opresc executia cu succes
        if nod_curent.test_scop():
            nod_scop_gasit = True
            break

        l_succesori = nod_curent.expandeaza()	# contine tupluri de tip (Nod, numar)
        for (nod_succesor, cost_succesor) in l_succesori:
            # "nod_curent" este tatal, "nod_succesor" este fiul curent

            # daca fiul nu este stramos al nodului nod_current(tatal) in graful G (adica nu se creeaza un circuit)
            if (not nod_curent.contine_in_drum(nod_succesor)):

                # calculez valorile g si f pentru "nod_succesor" (fiul)
                g_succesor = nod_curent.g + cost_succesor # g-ul tatalui + cost muchie(tata, fiu)
                f_succesor = g_succesor + nod_succesor.h # g-ul fiului + h-ul fiului

                #verific daca "nod_succesor" se afla in closed
                # (si il si sterg, returnand nodul sters in nod_parcg_vechi
                nod_parcg_vechi = in_lista(closed, nod_succesor)

                if nod_parcg_vechi is not None:	# "nod_succesor" e in closed
                    # daca f-ul calculat pentru drumul actual este mai bun (mai mic) decat
                    # 	   f-ul pentru drumul gasit anterior (f-ul nodului aflat in lista closed)
                    # atunci actualizez parintele, g si f
                    # si apoi voi adauga "nod_nou" in lista OPEN
                    if (f_succesor < nod_parcg_vechi.f):
                        closed.remove(nod_parcg_vechi)	# scot nodul din lista closed
                        nod_parcg_vechi.nod_parinte = nod_curent # actualizez parintele
                        nod_parcg_vechi.g = g_succesor	# actualizez g
                        nod_parcg_vechi.f = f_succesor	# actualizez f
                        nod_nou = nod_parcg_vechi	# setez "nod_nou", care va fi adaugat apoi in OPEN

                else :
                    # daca nu e in closed, verific daca "nod_succesor" se afla in OPEN
                    nod_parcg_vechi = in_lista(OPEN, nod_succesor)

                    if nod_parcg_vechi is not None:	# "nod_succesor" e in OPEN
                        # daca f-ul calculat pentru drumul actual este mai bun (mai mic) decat
                        # 	   f-ul pentru drumul gasit anterior (f-ul nodului aflat in lista OPEN)
                        # atunci scot nodul din lista OPEN
                        # 		(pentru ca modificarea valorilor f si g imi va strica sortarea listei OPEN)
                        # actualizez parintele, g si f
                        # si apoi voi adauga "nod_nou" in lista OPEN (la noua pozitie corecta in sortare)
                        if (f_succesor < nod_parcg_vechi.f):
                            OPEN.remove(nod_parcg_vechi)
                            nod_parcg_vechi.nod_parinte = nod_curent
                            nod_parcg_vechi.g = g_succesor
                            nod_parcg_vechi.f = f_succesor
                            nod_nou = nod_parcg_vechi

                    else: # cand "nod_succesor" nu e nici in closed, nici in OPEN
                        nod_nou = NodParcurgere(nod_graf=nod_succesor, nod_parinte=nod_curent, g=g_succesor)
                        # se calculeaza f automat in constructor

                if nod_nou:
                    # inserare in lista sortata crescator dupa f
                    # (si pentru f-uri egale descrescator dupa g)
                    i=0
                    while i < len(OPEN):
                        if OPEN[i].f < nod_nou.f:
                            i += 1
                        else:
                            while i < len(OPEN) and OPEN[i].f == nod_nou.f and OPEN[i].g > nod_nou.g:
                                i += 1
                            break

                    OPEN.insert(i, nod_nou)

    try:
        fout = open(nume_fisier_scriere, "w+")
        
        fout.write("\n------------------ Concluzie -----------------------\n")
        if len(OPEN) == 0:
            if nod_scop_gasit:
                fout.write("Nod start este si nod radacina")
            else:
                fout.write("Lista OPEN e vida, nu avem drum de la nodul start la nodul scop")
        else:
            fout.write("Drum de cost minim:\n" + str_info_noduri(nod_curent.drum_arbore()))
        
        fout.write("\nExecution time: ")
        fout.write(str(timeit.default_timer() - start_time))
    except:
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))


    fout.close()

def citire(nume_fisier_citire):
    try:
        fin = open(nume_fisier_citire, "r")
    except:
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

    clasa, copii_suparati, mesaj = [], [], []
    
    for line in fin:
        if 'suparati' in line:
            break

        try:
            nume = line.split()
        except ValueError:
            print("Something went wrong! Invalid input!")
            fin.close()

        clasa.append(nume)

    for line in fin:
        if 'mesaj' in line:
            mesaj = re.split('[:>,-]', line)
            del mesaj[0], mesaj[1]
            mesaj[0] = mesaj[0].strip()
            mesaj[1] = mesaj[1].strip()
            break

        copii_suparati.append((line.split()))

    fin.close()
    return clasa, copii_suparati, mesaj

def afisare_clasa(clasa):
    for rand in clasa:
        print(rand)


if __name__ == "__main__":
    clasa, copii_suparati, mesaj = citire(input_file_prefix + str("1") + file_format)
    afisare_clasa(clasa)
    numar_randuri, numar_coloane = len(clasa), len(clasa[0])

    configuratie_initiala = Configuratie(clasa, mesaj[0])
    configuratie_finala = Configuratie(clasa, mesaj[1])

    problema = Problema(configuratie_initiala, configuratie_finala)
    NodParcurgere.problema = problema

    a_star(output_file_prefix + str("1") + file_format)
