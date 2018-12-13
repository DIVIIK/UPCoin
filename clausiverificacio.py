import random

class Punt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# y^2 = x^3 + A_VAR*x + B_VAR
A_VAR = 0
B_VAR = 7

# Punt generatriu (G)
G = Punt(
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424
)

# p -> modul
# modul = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC2F
modul = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 -1

# n -> maxim valor que pot ser convertit en clau privada
#      qualsevol número entre [1, n-1]. Gx^n (mod p) = 1
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Valor privat
clauPrivada = 1

# Valors unics a compartir
#numeroRandom = 2869561854380584433211382972037328521042073943857088320383969651817641479123428695618543805844332113829720373285210420739438570883203839696518176414791234
numeroRandom = random.randint(0, 9999999999999999999999999999999999999999999999999999)
missatge = 86032112319101611046176971828093669637772856272773459297323797145286374828050 # Hash del missatge


def InversModular(a,n):
    lm, hm = 1,0
    low, high = a%n,n
    while low > 1:
        ratio = high//low
        nm, new = hm-lm*ratio, high-low*ratio
        lm, low, hm, high = nm, new, lm, low
    return lm % n

def SumaEliptica(punt_origen, punt_final): # ECAdd
    pendent = ((punt_final.y-punt_origen.y)*InversModular(punt_final.x-punt_origen.x, modul)) % modul
    x = (pow(pendent, 2) - punt_origen.x - punt_final.x) % modul
    y = (pendent*(punt_origen.x-x) - punt_origen.y) % modul
    return Punt(x, y)

def DobleEliptic(punt):
     pendent = ((3*pow(punt.x, 2)+A_VAR) * InversModular(2*punt.y, modul)) % modul
     x = (pendent*pendent-2*punt.x) % modul
     y = (pendent*(punt.x - x)-punt.y) % modul
     return Punt(x, y)

def MultiplicacioEliptica(base, clauPrivada):
    binariClauPrivada = str(bin(clauPrivada))[2:]
    q = base
    for i in range(1, len(binariClauPrivada)):
        q = DobleEliptic(q)
        if binariClauPrivada[i] == "1":
            q = SumaEliptica(q, base)
    return q

def GeneraClauPublica(privateKey):
    return MultiplicacioEliptica(G, privateKey)


print(" - Clau privada -")
print(hex(clauPrivada))
print()

print(" - Clau publica -")
clauPublica = MultiplicacioEliptica(G, clauPrivada)
print(clauPublica.x)
print("04" + str(hex(clauPublica.x)[2:]).zfill(64) + str(hex(clauPublica.y)[2:]).zfill(64))
print()

print(" - Signatura -")
puntRandom = MultiplicacioEliptica(G, numeroRandom)
random_x = puntRandom.x % n
signatura = ((missatge + random_x * clauPrivada)*InversModular(numeroRandom, n)) % n
print("s:", signatura)
print()

print(" - Verificacio -")
a = MultiplicacioEliptica(G, (missatge*InversModular(signatura, n))%n)
b = MultiplicacioEliptica(clauPublica, (random_x*InversModular(signatura, n))%n)
res = SumaEliptica(a, b)
print("Intent amb clau pública correcte:",res.x == random_x)

a = MultiplicacioEliptica(G, (missatge*InversModular(signatura, n))%n)
clauPublica.x += 1; # Afegim un 1 a la clau pública per modificar-la
b = MultiplicacioEliptica(clauPublica, (random_x*InversModular(signatura, n))%n)
res = SumaEliptica(a, b)
print("Intent amb clau pública falsa:",res.x == random_x)
