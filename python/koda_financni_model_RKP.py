"""
FINANČNI RKP PROBLEM
"""

##### za pridobitev rešitve finančnega RKP modela potrebujemo dva argumenta:
# - datoteko tipa .txt, v kateri so po vrsti v stolpcih napisani podatki: Simbol 
#podjetja, ime podjetja, nominalna cena delnice, najvišja cena delnice in pričakovani donos
# - znesek denarja, namenjenega investiranju (BUDGET)
#Optimalni portelj dobimo tako, da pokličemo funkcijo resitev_za_delnice(datoteka, budget)


import time
start_time = time.time()

def matrika(m,n):
    return [[0] * (m+1) for _ in range(n+1)] #funkcija, ki naredi ničelno matriko 

def v_seznam(N):
    N0 = []
    for i in N:
        N0 += [i]
    N = N0
    return N

# funkcija, ki podatke razvrsti padajoče po maks_w(j)
def podatki(N, w, p, maks_w = None):
    N = v_seznam(N)
    if maks_w is None:
         vrstni_red = [i[0] for i in sorted(enumerate(w), key=lambda x:x[1])]
         w = [w[i] for i in vrstni_red]
         p = [p[i] for i in vrstni_red]
         N = [N[i] for i in vrstni_red]
         return (N[::-1], w[::-1], p[::-1])
    else:  
        urejen_sez = [0] * len(maks_w)
        for i in range(len(maks_w)):
            urejen_sez[i] = maks_w[i] - w[i]
        vrstni_red = [i[0] for i in sorted(enumerate(urejen_sez), key=lambda x:x[1])]
        maks_w = [maks_w[i] for i in vrstni_red]
        p = [p[i] for i in vrstni_red]
        w = [w[i] for i in vrstni_red]
        N = [N[i] for i in vrstni_red]
        return (N[::-1], w[::-1], p[::-1], maks_w[::-1])

# množico N razdeli na dva enako velika seznama N1 in N2
def particija(N):
    n = len(N)
    N = v_seznam(N)
    N1 = []
    N2 = []
    if n % 2 == 0:
        for el in N:
            if N.index(el) < (n / 2) :
                N1.append(el)
            else:
                N2.append(el)
        return N1, N2
    else:
        for el in N:
            if N.index(el) <= (n / 2):
                N1.append(el)
            else:
                N2.append(el)
        return N1, N2

# funkcija solve_RKP vrne optimalno vrednost, optimalno težo pri tej vrednosti, koliko predmetov uporabimo in koliko predmetov uporabimo iz N1 (prve polovice predmetov)
def solve_RKP(N, c, w, p, gama = None,  maks_w = None):
    # slovar predmetov spremenimo v seznam(resitev) predmetov
    N = v_seznam(N)
    if len(N) == 1:
        if gama != 0:
            if maks_w[0] <= c: #če imamo samo en element, ki spremeni svojo težo na maks_w <= c,
                return [p[0], maks_w[0], 1, 0]  #je to edini element, ki ga damo v nahrbtnik 
            else:
                return [0, 0, 0, 0]  
        else:
            if w[0] <= c:
                return [p[0], w[0], 1, 0] #če predmet ne spremeni svoje teže, ga dodamo v nahrbnik,
            else:                          #če je w <= c
                return [0, 0, 0, 0]
    else:
        if maks_w is not None:
            pravilni_podatki = podatki(N, w, p, maks_w) #uporabiva funkcijo podatki, ki podatke spremeni v pravo obliko
            N, w, p, maks_w = pravilni_podatki[0], pravilni_podatki[1], pravilni_podatki[2], pravilni_podatki[3]
        else: 
            pravilni_podatki = podatki(N, w, p) # uporabiva funkcijo podatki, ki podatke spremeni v pravo obliko
            N, w, p = pravilni_podatki[0], pravilni_podatki[1], pravilni_podatki[2] 
        if gama == None or 0:
            maks_w = [c]* len(w)
            gama = 0 
        if c < min(w):
            return [0, 0, 0, 0]
        if len(N) == len(w) == len(p) == len(maks_w): 
            pass
        else: 
            raise ValueError("Napačno vneseni podatki")
        #naredimo matrike z, k, n in nastavimo začetne pogoje
        z = matrika(gama,c) #element matrike z[d][s] pomeni maksimalno vrednost pri
        for d in range(c + 1): #kapaciteti nahrbtnika d, pri čemer največ s predmetov spremeni
            for s in range(gama + 1): #svojo težo na maks_w
                z[d][s]= float("-inf")
        z[0][0] = 0     
        c_zvezdica = 0

        g = matrika(gama,c) #element matrike g[d][s] pomeni optimalno število predmetov v 
        for d in range(c + 1): #nahrbtniku pri kapaciteti nahrbtnika d, pri čemer največ s 
            for s in range(gama + 1): #predmetov spremeni svojo težo na maks_w
                g[d][s]= 0
        g[0][0] = 0

        k = matrika(gama,c) #element matrike k[d][s] pomeni optimalno število predmetov v 
        for d in range(c + 1): #v nahrbtniku iz množice N2 (druga polovica vseh stvari) pri
            for s in range(gama + 1): #kapaciteti nahbrnika d, pri čemer največ s predmetov
                g[d][s] = 0 #spremeni svojo težo na maks_w
        k[0][0] = 0


        zadnji_elemnt = 0        
        for j in range(len(N)): # izberemo j-ti predmet 
            for d in range(c, w[j]-1, -1):  # in ga poskusimo dodati v svoji nominalni teži 
                if p[j] != p[zadnji_elemnt] and w[j] != w[zadnji_elemnt]: #če smo že vzeli delnico katerega podjetja v robustni teži, nemoremo vzeti še kakšne delnice istega podjetja v njeni nominalni teži
                    if z[d - w[j]][gama] + p[j] > z[d][gama]: #pri pogoju, da smo že vstavili 
                        z[d][gama] = z[d - w[j]][gama] + p[j]  #gama predmetov
                        g[d][gama] = 1 + g[d - w[j]][gama]
                        if j  >= ((len(N) / 2)):
                            k[d][gama] = 1 + k[d - w[j]][gama]
                      
            for s in range(gama, 0, -1): # poskusimo ga dodati v svoji robustni teži
                for d in range(c, maks_w[j] - 1, -1):
                    if z[d - maks_w[j]][s - 1] + p[j] > z[d][s]:
                        z[d][s] = z[d - maks_w[j]][s - 1] + p[j]
                        g[d][s] = 1 + g[d - maks_w[j]][s-1]
                        zadnji_elemnt = j #zapomnemo si zadnji element, ki smo ga dodali v robustni teži
                        if j  >= ((len(N) / 2)):
                            k[d][s] = 1 + k[d - maks_w[j]][s - 1]


        z_zvedica = max([max(l) for l in z]) #tako dobimo max vrednost (največji element matrike z)
        pozicija = [[index, vrstica.index(z_zvedica)] for index, vrstica in enumerate(z) if z_zvedica in vrstica]
        c_zvezdica = pozicija[0][0] #vrstica in stolpec max vrednosti predstavljata skupno težo vstavljenih predmetov
        stevilo_predmetov_s_povecano_tezo = pozicija[0][-1] #in število predmetov, ki se jim spremeni teža
        k1 = k[c_zvezdica][stevilo_predmetov_s_povecano_tezo] #k1 se v k nahaja na istem mestu kot z_zvezdica(pomeni koliko elementov iz N2 je v optimalni rešitvi)
        g_zvezdica = g[c_zvezdica][stevilo_predmetov_s_povecano_tezo] #na istem mestu kot z_zvezdica se nahaja tudi število vseh vstavljenih predmetov v optimalni rešitvi
        k_zvezdica = g_zvezdica - k1 #k_zvezdica = št.elementov v N1, g_zvezdica = št. vseh elementov
        return [z_zvedica, c_zvezdica, g_zvezdica, k_zvezdica]

def solve_KP(N, c, w, p):  
    n = len(N)
    if n == 1:
        if w[0] <= c:
            return [N[0], p[0]]
        else:
            return [0, 0]
    
    else:
        z = matrika(c, n)
        for j in range(n + 1): 
            for d in range(c + 1): 
                if j == 0 or d == 0: 
                    z[j][d] = 0
                elif w[j-1] <= d: 
                    z[j][d] = max(p[j-1] + z[j-1][d-w[j-1]], z[j-1][d]) 
                    z[j][d] == p[j-1] + z[j-1][d-w[j-1]]
                else: 
                    z[j][d] = z[j-1][d] 
        z_zvezdica = z[n][c]
        z_zvezdica1 = z[n][c] 
        c_zvezdica = 0
        seznam_stvari = [] #seznam_stvari predstavlja seznam stvari, ki smo jih dali v nahrbtnik
        #set_stvari = []
        for i in range(n, 0, -1):  
            if z_zvezdica1 <= 0 or c <= 0: #seznam stvari dobimo tako, da za vsak element i v obratnem vrstnem
                break            #redu pogledamo kakšna je optimalna vrednost, če v nahrbtnik lahko
            if z_zvezdica1 == z[i - 1][c]: #vstavimo samo elemente iz množice {0, 1, ..., i}
                continue                   #če je ta vrednost enaka optimalni vrednosti, potem nadaljujemo
            else:                           #če pa se ta vrednost razlikuje od optimalne vrednosti, potem element i
                N = v_seznam(N)            #dodamo v seznam stvari, zmanjšamo optimalno vrednost za vrednost 
                element = N[i - 1]         #tega elementa in nadaljujemo dokler optimalna vrednost ne pride do 0
                #set_stvari.append([element, w[i - 1], p[i - 1]])
                seznam_stvari.append(element)
                c_zvezdica += w[i - 1]
                z_zvezdica1 -= p[i - 1]
                c -= w[i - 1]
        return [seznam_stvari, z_zvezdica, c_zvezdica]

# solve_eKkP vrne seznam vseh predmetov in optimalno vrednost, če dodatno omejimo maksimalno števio uporabljenih predmetov 
def solve_eKkP(N, c, w, p, k):   #algoritem je tu podoben kot pri Solve_KP, le da je matrika k tridimenzionalna, saj zraven
    n = len(N)                 #beleži še kakšna je optimalna vrednost, če omejimo maksimalno število predmetov
    if n == 1:                  #na m = 1, ..., k
        if k == 0:
            return [0, 0]
        else: 
            if w[0] <= c:
                return [N[0], p[0]]
            else:
                return [0, 0]
    else:
        z = [[[0 for col in range(k + 1)] for col in range(c + 1)] for row in range(n + 1)]
        for j in range(n + 1): 
            for d in range(c + 1):
                for m in range(k + 1): 
                    if j == 0 or d == 0 or m == 0: 
                        z[j][d][m] = 0
                    elif w[j-1] <= d: 
                        z[j][d][m] = max(p[j-1] + z[j-1][d-w[j-1]][m - 1], z[j-1][d][m])         
                    else: 
                        z[j][d][m]= z[j-1][d][m]
        z_zvezdica = z[n][c][k]
        z_zvezdica1 = z[n][c][k]
        c_zvezdica = 0
        seznam_stvari = []
        for i in range(n, 0, -1):
            if z_zvezdica1 <= 0 or c <= 0:
                break
            elif z_zvezdica1 == z[i - 1][c][k]:
                continue
            else:
                element = N[i - 1]
                seznam_stvari.append(element)
                c_zvezdica += w[i - 1]
                z_zvezdica1 -= p[i - 1]
                c -= w[i - 1]
        return(seznam_stvari, z_zvezdica)

def naredi_pravi_seznam(resitev): #funkcija vgnezden seznam spremeni v navaden seznam
    nov_sez = []
    for el in resitev:
        if isinstance(el, list):
            for i in el:
                nov_sez.append(i)
        else:
            nov_sez.append(el)
    return(nov_sez)
#funkcija, ki deluje na principu rekurzije in nam vrne seznam stvari, ki jih vstavimo v nahrbtnik
def rekurzija(N, z_zvezdica, k_zvezdica, c_zvezdica, gama, w, maks_w, p, resitev=None):
    if resitev is None:
        resitev = []
    if len(N) == 1 and resitev == []:
        if gama != 0:
            if maks_w[0] <= c_zvezdica:
                print(N)
                return N
            else:
                print("V nahrbtnik ne moremo dati nobene stvari.")
        else:
            if w[0] <= c_zvezdica:
                return N
            else:
                print("V nahrbtnik ne moremo dati nobene stvari.")
    elif len(N) == 1 and resitev != []:
        if gama != 0:
            if maks_w[0] <= c_zvezdica:
                resitev.append(N[0])
                resitev = naredi_pravi_seznam(resitev)
                return(resitev)
            else: 
                resitev = naredi_pravi_seznam(resitev)
                return(resitev)
        else:
            if w[0] <= c_zvezdica:
                resitev.append(N[0])
                resitev = naredi_pravi_seznam(resitev)
                return(resitev)
    else:
        N = v_seznam(N)
        N, w, p, maks_w = podatki(N, w, p, maks_w)
        N1, N2 = particija(N) #N razdelimo na N1 in N2
        n = len(N)  
        polovica = int((n / 2 ))
        if n % 2 == 0:     #tudi seznam, ki predstavlja vrednosti, teže in maks teže
           w1 = w[:polovica] #razdelimo na dva dela
           w2 = w[polovica:] 
           maks_w1 = maks_w[:polovica]
           maks_w2 = maks_w[polovica:]
           p1 = p[:polovica]
           p2 = p[polovica:]
        else:
           w1 = w[:polovica + 1]
           w2 = w[polovica + 1:] 
           maks_w1 = maks_w[:polovica + 1]
           maks_w2 = maks_w[polovica + 1:]
           p1 = p[:polovica + 1]
           p2 = p[1+ polovica:]
    
        if k_zvezdica >= gama: #če je število vstavljenih predmetov iz prve polovice stvari večje
                                #od lamde (največ toliko predmetov lahko spremeni svojo težo iz w na maks w),
            for c_1 in range(c_zvezdica + 1): #potem seznam vstavljenih predmetov iz N2 dobimo s pomočjo
                c1 = c_1                      #funkcije Solve_KP, problem za predmete iz N1, kjer največ
                c2 = c1 - c_zvezdica          #gama predmetov spremeni svojo težo, pa spet predstavlja 
                z1_c_1 = solve_RKP(N1, c_1, w1, p1, gama, maks_w1)[0] #robustni problem nahrbtnika, zato spet pokličemo
                z2_c_2 = solve_KP(N2, c_zvezdica - c_1, w2, p2)[1] #funkcijo rekurzija
                z1_c1 = z1_c_1
                z2_c2 = z2_c_2
                if z1_c_1 + z2_c_2 == z_zvezdica:
                    z2_c2 = z2_c_2
                    z1_c1 = z1_c_1
                    c1 = c_1
                    c2 = c_zvezdica - c1
                    break
            solution_set_kp = solve_KP(N2, c2, w2, p2)[0]
            resitev.append(solution_set_kp)
            k1_zvezdica = solve_RKP(N1, c1, w1, p1, gama, maks_w1)[3]
            return rekurzija(N1, z1_c1 , k1_zvezdica, c1, gama, w1, maks_w1, p1, resitev)        
        else: 
            for c_2 in range(c_zvezdica + 1):    #če je gama večji od k, dobimo seznam predmetov iz množice
                c2 = c_2                      #N1 s pomočjo funkcije solve_ekkp, za N2 pa spet pokličemo funkcijo rekurzija
                c1 = c_zvezdica - c2
                z2_c_2 = solve_RKP(N2, c_zvezdica - c1, w2, p2, gama - k_zvezdica, maks_w2)[0]
                z1_c_1 = solve_eKkP(N1, c1, maks_w1, p1, k_zvezdica)[1]
                z1_c1 = z1_c_1
                z2_c2 = z2_c_2

                if z1_c_1 + z2_c_2 == z_zvezdica:
                    z2_c2 = z2_c_2
                    z1_c1 = z1_c_1
                    c2 = c_2
                    c1 = c_zvezdica - c2
                    break
            solution_set_eKkP = solve_eKkP(N1, c1, maks_w1, p1, k_zvezdica)[0]
            resitev.append(solution_set_eKkP)
            k2_zvezdica = solve_RKP(N2, c2, w2, p2, gama - k_zvezdica, maks_w2)[3]
            c2 = c_zvezdica - c1
            return rekurzija(N2, z2_c2, k2_zvezdica, c2,gama - k_zvezdica, w2, maks_w2, p2, resitev)
 
# rekurzija({1,2,3,4,5,6,7,8,9,10},66,3,20,4,[4,2,6,5,2,1,7,3,5,2],[5,4,6,7,4,4,7,4,5,3], [8,5,17,10,14,4,6,8,9,25])

def resitev(N, c, w, p, imena_delnic, gama = None, maks_w = None): #funkcija nam vrne končno rešitev: 
    n = len(N)
    if gama is None or gama == 0:
        resitev = solve_KP(N, c, w, p)[0]
        z_zvedica = solve_KP(N, c, w, p)[1]
        c_zvezdica = solve_KP(N, c, w, p)[2]
        return resitev, z_zvedica, c_zvezdica
    else:
        k_zvezdica = solve_RKP(N, c, w, p, gama, maks_w)[3]     #seznam vstavljenih predmetov in vrednost
        z_zvezdica = solve_RKP(N, c, w, p, gama, maks_w)[0]
        c_zvezdica = solve_RKP(N, c, w, p, gama, maks_w)[1]
        resitev = rekurzija(N, z_zvezdica, k_zvezdica, c_zvezdica, gama, w, maks_w, p)
        nova_resitev = []
        resitev = naredi_pravi_seznam(resitev)
        for el in resitev:
            if el != 0:
                nova_resitev.append(el)
        
    #če je slučajno v seznamu predmetov tudi element 0,
    #ga odstranimo, saj se v funkciji rekurzija zaradi lažjega
    #poteka v primeru, da ne vstavimo nobenega elementa v seznam
    #vstavi 0 
    delnice = []  
    with open('resitev' "%s" % n +'-' "%s" % c + '-' "%s.txt" % gama, 'w', encoding='utf-8') as izhodna:
        for el in nova_resitev:
            izhodna.write("{} {} {} {}\n".format(N[el - 1], p[el - 1], w[el - 1], maks_w[el - 1]))
            delnice.append(imena_delnic[el - 1])
    return(nova_resitev, z_zvezdica, c_zvezdica, delnice)

# ta funkcija prebere podatke iz S&P 500.txt in jih prilagodi, tako da potem dela program preberi_podatke_za_delnice() 
def popravi_podatke(dat, kodna_tabela="utf-8"):
    with open(dat, encoding=kodna_tabela) as datoteka:
        N = []
        w = []
        r = []
        ime_podjetja = []
        kratica_podjetja = []
        maks_w = []
        števec = 0
        for vrstica in datoteka:
            vrstica = vrstica.rstrip()
            števec += 1
            if števec > 1:
                x = []
                x = vrstica.split(",")
                if len(x) == 7:
                    N.append(x[0])
                    kratica_podjetja.append(x[1])
                    ime_podjetja.append(x[2])
                    w.append(float(x[4]))
                    maks_w.append(float(x[5]))
                    r.append(x[6])
                else:                  
                    N.append((x[0]))
                    kratica_podjetja.append(x[1])
                    ime_podjetja.append(x[2])
                    w.append(float(x[3]))
                    maks_w.append(float((x[4])))
                    r.append((x[5]))
    with open("Robust-knapsack-problem/podatki/podatki za delnice/popravljeni_podatki.txt","w") as nova_datoteka:
        for i in range(len(N)):
            nova_datoteka.write("{} {} {} {} {} {}\n".format(int(N[i].strip('""')), kratica_podjetja[i], ime_podjetja[i], w[i], maks_w[i], float(r[i].strip('""'))))
    

#popravi_podatke("Robust-knapsack-problem/podatki/podatki za delnice/S&P 500.txt")


def preberi_podatke_za_delnice(dat, budget, kodna_tabela='utf-8'): #funkcija prebere podatke o delnicah
    with open(dat, encoding=kodna_tabela) as datoteka:
        N = []
        maks_p = []
        p = []
        r = []
        imena_delnic = []
        vse_delnice = 0
        seznam_kolicine_delnic = []
        R = []
        for vrstica in datoteka:
            x = []
            x = vrstica.split() #najprej vsako vrstico razdelimo na seznam            
            st = int(budget / float(x[-2]))
            R.append(float(x[-1]) * st )
            if float(x[-1]) > 0: #če je donos delnice negativen, teh delnic sploh ne upoštevamo, saj nima smisla
                                          #prvi element vsake vrstice predstavlja ime delnice
                stevilo_delnic = int(budget / float(x[-2])) #maksimalno število delnic posameznega podjetja, ki jih lahko kupimo (budget / maks cena delnice)
                seznam_kolicine_delnic.append(stevilo_delnic) #seznam, ki predstavlja največ koliko delnic posameznega podjetja lahko kupimo
                for delnica in range(vse_delnice + 1, vse_delnice + stevilo_delnic + 1): #naredimo nov seznam delnic, cen, maks cen in donosov
                    N.append(delnica)                                                   #tu se vsaka posamezna delnica vsakega podjetja steje kot en element
                    imena_delnic.append(x[1])
                    p.append(int(float(x[-3])))
                    maks_p.append(int(float(x[-2])))
                    r.append(int(float(x[-3]) * (1 + 0.01 * (float(x[-1])))))
                    vse_delnice += 1
    return(N, p, maks_p, r, imena_delnic, R)

from numpy import random
def doloci_gamo(R_popravljen): #iz podatkov določimo gamo (podroben opis v poročilu)
    stevilo_delnic = len(R_popravljen) 
    R_skupen = sum(R_popravljen)/100 
    R_povprecen = (R_skupen / stevilo_delnic)   
    if R_povprecen < 0:
        R_povprecen = 0
    if R_povprecen > 1:
        R_povprecen = 1
    seznam_lambd = random.binomial(n=stevilo_delnic, p = R_povprecen, size=300)
    gama = sum(seznam_lambd)//300 + 1
    return gama

from collections import Counter

def resitev_za_delnice(datoteka, budget):
    N, p, maks_p, r, delnice, R = preberi_podatke_za_delnice(datoteka, budget)
    gama = doloci_gamo(R)
    z_zvezdica = resitev(N,budget, p, r, delnice, gama, maks_p)[1]
    c_zvezdica = resitev(N,budget, p, r,delnice, gama, maks_p)[2]
    seznam_delnic = resitev(N,budget, p, r,delnice, gama, maks_p)[-1]
    stevec = Counter()
    for el in seznam_delnic: #pogledamo kolikokrat se v rešitvi pojavi posamezna delnica
        stevec[el] += 1 

    return(stevec, z_zvezdica - c_zvezdica) #v rezultatu dobimo optimalno sestavo portfelja in dobiček

#print(resitev_za_delnice('Robust-knapsack-problem/podatki/podatki_za_delnice/popravljeni_podatki.txt', 500))
