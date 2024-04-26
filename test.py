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
    
        

    def generate_bit(self):
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
    def __init__(self) -> None:
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

        self.k = 1

    def generate_key(self, s, n_bytes):
        
        seed_lfsr_17 = (s >> 24) & 0xFFFF | 1 << 16
        seed_lfsr_25 =  s & 0xFFFFFF | 1 << 24

        

        self.lfsr17.setState(seed_lfsr_17)
        self.lfsr25.setState(seed_lfsr_25)

        x = 0
        y = 0
        c = 0
        k = 0


        for i in range(n_bytes):
            x = 0
            y = 0
            for j in range(8):
                x = x | (self.lfsr17.generate_bit() << j) 
                y = y | (self.lfsr25.generate_bit() << j) 


            
            k = k | ((x + y + c) % 256 << (n_bytes-1-i)*8)

            if (x+y) > 255:
                c = 1
            else:
                c = 0

        self.k = k
        return k
    
    def encrypt_message(self, s, message):
        length = 0
        val = message
        if(val == 0):
            length = 1
        else:
            while val > 0:
                length += 1
                val = val >> 8

        self.generate_key(s, length)
        return self.k ^ message



def Question4():
    message = 0xffffffffff

    css = CSS()
    s = 0

    message_chiffre = css.encrypt_message(s, message)


    print(hex(message_chiffre))

#Question4()


def Question5():

    coeffs_LFSR_17 = [0] * 17

    coeffs_LFSR_17[0] = 1 
    coeffs_LFSR_17[14] = 1

    coeffs_LFSR_25 = [0] * 25

    coeffs_LFSR_25[0]  = 1
    coeffs_LFSR_25[3] = 1
    coeffs_LFSR_25[4] = 1
    coeffs_LFSR_25[12] = 1



    premier_etat = 2 ** 16
    dernier_etat = 2 ** 17

    secret_key = random.getrandbits(40) #génere un nombre aléatoire de 40 bits
    css = CSS()
    z = [css.generate_key(secret_key, 6) >>(8*i) & 0xFF for i in range (6)] #générer z1 à z6

    found_s = -1


    for initial_state_17 in range(premier_etat, dernier_etat): #on teste tous les états possibles du premier LFSR

        lfsr17 = LFSR(initial_state_17, coeffs_LFSR_17)
        x = [] #liste de x1 à x6

        for i in range(6):
            o = 0
            for j in range(8):
                o = o | lfsr17.generate_bit() << j  #on génère x1 à x6
            x.append(o)
        
        y = [] # on va calculer y1 à y6 à partir de x et z
        c = 0
        for i in range(6):
            # Calcul de y en tenant compte du carry
            temp_sum = z[i] - x[i] - c
            if temp_sum < 0:
                y.append(256 + temp_sum)  # Ajouter 256 pour gérer le carry négatif
                c = 1  # Mise à jour du carry pour le prochain calcul
            else:
                y.append(temp_sum)
                c = 0  # Reset carry si aucun dépassement
                
        
        test_seed = 1 << 24 | y[2] << 16 | y[1] << 8 | y[0] #l'état initial du LFSR25 correspond aux trois premiers octets calculés

        test_bytes = []

        test_lfsr25 = LFSR(test_seed, coeffs_LFSR_25) #on crée un LFSR avec l'etat initial calculé pour vérifier si les y calculés correspondent à un état possible du LFSR25
                                                    # et ainsi vérifier si l'état initial du LFSR17 actuel est le bon

        for i in range(6):
            g= 0
            for j in range(8):
                g = g | test_lfsr25.generate_bit() << j
            test_bytes.append(g)
        
        correspondance = (test_bytes == y)
        

        if correspondance:
            print('ok')
            found_s = x[0] << 32 | x[1] << 24 | y[0] << 16 | y[1] << 8 | y[0]
            break
            

    print(found_s)
    print(secret_key)
    print(found_s == secret_key)
    return found_s == secret_key

Question5()

"""

#Partie de test à décommenter pour executer la fonction de test sur un LFSR de taille 17
# Executer la fonction de test

is_full_cycle = test_lfsr(seed_17, coeffs_LFSR_17)
print("Le LSFR pass par toutes les valeurs non-nulles: ", is_full_cycle)


"""