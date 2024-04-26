import random

class LFSR:

    """
    Classe représentant les LFSR 
        Attributs:
        length : La taille du LFSR
        state : l'état actuel du LFSR
        coeff : le coefficient de retroaction du LFSR
    """

    def __init__(self, seed: int, coeffs: list) -> None:

        assert seed <= 2 ** len(coeffs), "La seed doit être plus petite ou égale à 2^" + str(len(coeffs))
        assert seed != 0, "La seed ne peut pas être nulle"

        self.length = len(coeffs)
        self.state = seed
        self.coeffs = coeffs

    
    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state
    
        

    def generate_bit(self):
        """Fonction qui simule un coup d'horloge du LFSR en retournant le bit sorti et mettant à jour l'état en fonction des coefficients de rétroaction"""

        output_bit = self.state & 1
        retroaction_bit = 0
        for i in range(self.length):
            if self.coeffs[i] == 1:
                retroaction_bit ^= (self.state >> i) & 1
        self.state = (retroaction_bit << (self.length - 1)) | (self.state >> 1)

        return output_bit
    

    

def test_lfsr(seed, coeffs):

    """
    Fonction qui test si un LFSR passe par tous les états possibles.
    """

    lfsr = LFSR(seed, coeffs)
    seen_states = set()

    while True:
        lfsr.generate_bit()
        # On arrete si on revient à un état déjà vu.
        if lfsr.state in seen_states:
            break
        seen_states.add(lfsr.state)

    return len(seen_states) == (1 << lfsr.length) - 1


class CSS():
    """
    Classe simulant le fonctionnement d'un CSS
    """
    def __init__(self) -> None:
        #initialisation des LFSR et de leurs coefficients de rétroaction

        coeffs_LFSR_17 = [0] * 17

        coeffs_LFSR_17[0] = 1 
        coeffs_LFSR_17[14] = 1

        coeffs_LFSR_25 = [0] * 25

        coeffs_LFSR_25[0]  = 1
        coeffs_LFSR_25[3] = 1
        coeffs_LFSR_25[4] = 1
        coeffs_LFSR_25[12] = 1

        self.lfsr17 = LFSR(1, coeffs_LFSR_17)
        self.lfsr25 = LFSR(1, coeffs_LFSR_25)

        self.z = None #initialisationd de la cle de chiffrement/dechiffrement

    def generate_key(self, s, n_bytes):
        """Fonction qui génère une clé de chiffrement/dechiffrement z de longueur n_bytes à partir de la clé secrete s"""
        
        seed_lfsr_17 = (s >> 24) & 0xFFFF | 1 << 16
        seed_lfsr_25 =  s & 0xFFFFFF | 1 << 24

        

        self.lfsr17.setState(seed_lfsr_17)
        self.lfsr25.setState(seed_lfsr_25)

        x = 0 #les octets qui sortent du LFSR de longueur 17
        y = 0 #les octets qui sortent du LFSR de longueur 25
        c = 0 #le bit de carry
        k = 0 #la cle de chiffrement/dechiffrement

        #on récupère les n_bytes premiers octets produits par chaque LFSR
        for i in range(n_bytes):
            x = 0
            y = 0
            for j in range(8):
                x = x | (self.lfsr17.generate_bit() << j) 
                y = y | (self.lfsr25.generate_bit() << j) 


            #on ajoute chaque octet au à la cle de chiffrement/dechiffrement selon la formule z = x + y + c % 256
            k = k | ((x + y + c) % 256 << (n_bytes-1-i)*8)

            if (x+y) > 255:
                c = 1
            else:
                c = 0

        self.z = k
        return k
    
    def encrypt_message(self, s, message):
        """Fonction qui permet de chiffrer un message avec un cle secrete"""

        #ici on récupere la longueur l en octet du message pour créer une clé créée à partir des l premiers octets du CSS
        length = 0
        val = message
        if(val == 0):
            length = 1
        else:
            while val > 0:
                length += 1
                val = val >> 8

        self.generate_key(s, length)

        #puis on retourne la clé XOR message
        return self.z ^ message

    def decrypt_message(self, message):
        """Fonction qui décrypte un message précedemment encrypté par le css"""

        return self.z ^ message


def Question1():
    print("--------------------------------------------------------------------------------------")
    print("QUESTION 1")


    coeffs_LFSR_17 = [0] * 17

    coeffs_LFSR_17[0] = 1 
    coeffs_LFSR_17[14] = 1

    seed_17 = random.getrandbits(16) | 1 << 16 #génération d'un état initial valide aléatoire

    is_full_cycle = test_lfsr(seed_17, coeffs_LFSR_17)

    print(f"Etat initial: {hex(seed_17)}")
    print("Le LSFR passe par toutes les valeurs non-nulles: ", is_full_cycle)
    print('---------------------------------------------------------------------------------------')

def Question4():
    print("--------------------------------------------------------------------------------------")
    print("QUESTION 4")
    message = 0xffffffffff

    css = CSS()
    s = 0

    message_chiffre = css.encrypt_message(s, message)
    message_dechiffre = css.decrypt_message(message_chiffre)

    print(f"Le message de base est: {hex(message)}")
    print(f"Une fois chiffré le message est: {hex(message_chiffre)}")
    print(f"Et une fois déchifré le message est {hex(message_dechiffre)}")

    print("--------------------------------------------------------------------------------------")


def Question6():

    print("--------------------------------------------------------------------------------------")
    print("QUESTION 6")

    #initilaisation des coefficients de rétroaction pour les LFSR

    coeffs_LFSR_17 = [0] * 17

    coeffs_LFSR_17[0] = 1 
    coeffs_LFSR_17[14] = 1

    coeffs_LFSR_25 = [0] * 25

    coeffs_LFSR_25[0]  = 1
    coeffs_LFSR_25[3] = 1
    coeffs_LFSR_25[4] = 1
    coeffs_LFSR_25[12] = 1

    secret_key = random.getrandbits(40) #génere un nombre aléatoire de 40 bits qui va nous servie de clé secrete
    seed17 = 1 << 16 | (secret_key >> 24) & 0xFFFF
    seed25 = 1 << 24 | (secret_key) & 0xFFFFFFFF

    css = CSS()
    _z = css.generate_key(secret_key, 6)# génère les 6 premiers octets de z
    z = [_z >>(8*i) & 0xFF for i in range (6)][::-1] #liste qui divise z en 6
    

    for _etat in range(0, 2**16): #on boucle sur tous les états possibles du LFSR de longueur 17
   
        c = 0
        etat_init = 1 << 16 | _etat
        lfsr17 = LFSR(etat_init, coeffs_LFSR_17)

        #on récupère x1 et x2 qui sont les deux derniers octets de l'etat initial
        x1 = lfsr17.getState() % 256
        x2 = (lfsr17.getState() >> 8) % 256 
        
        #on génère x3
        for _ in range(16):
            lfsr17.generate_bit()
        
        x3 = lfsr17.getState() % 256

        
        #à partir de là on peut calculer y1, y2 et y3
        y1 = (z[0] - x1 - c)%256
        c = 1 if (x1 + y1 > 255) else 0

        y2 = (z[1] - x2 - c)%256
        c = 1 if (x2 + y2 > 255) else 0

        y3 = (z[2] - x3 - c)%256
        c = 1 if (x3 + y3 > 255) else 0

        #on peut alors calculer z3, z5, et z6 et les comparer avec les z originaux pour vérifier la cohérence des résultats
        etat_initial_25 = 1 << 24 | y3 << 16 | y2 << 8 | y1   
        lfsr25 = LFSR(etat_initial_25, coeffs_LFSR_25)

        for _ in range(24):
            lfsr25.generate_bit()
        for _ in range(8):
            lfsr17.generate_bit()
        
        correspondance = True
        for i in range(3, 6):
            x = lfsr17.getState() % 256
            y = lfsr25.getState() % 256

            if z[i] != (x + y + c) % 256:
                correspondance = False
                break
            else:
                for _ in range(8):
                    lfsr17.generate_bit()
                    lfsr25.generate_bit()
                c = 1 if x + y > 255 else 0
                continue
        if not correspondance:
            continue


        print("Etat initial du LFSR17 calculé: " + hex((1 << 16) + (x2 << 8) + x1))
        print("Etat initial du LFSR25 correspondant: " + hex((1 << 24) + (y3 << 16) + (y2 << 8) + y1))
        print("Etat initial du LFSR17 original: " + hex(seed17))
        print("Etat initial du LFSR25 original:" + hex(seed25))
        break
    
    print("--------------------------------------------------------------------------------------")
    
    return

Question1()
Question4()
Question6()





