#coding=utf-8
import os
import signal
import sys


#def signal_handler(signal, frame):
#        print("You pressed Ctrl+C!")
#        sys.exit(0)
#signal.signal(signal.SIGINT, signal_handler)



class Action:
    UPLOAD = "UPLOAD"    
    DOWNLOAD = "DOWNLOAD"
    QUITTER = "QUIT"
    
    SAISIR = "INPUT"
    INTERACTIF = "INTER"

class ElementDeSynchronisation:
    def __init__(self, eltLocal, eltDistant, sync):
        self.eltLocal = eltLocal
        self.eltDistant = eltDistant
        self.synchronise = sync;
    def __str__(self):
        s = " Local\t\t: " + self.eltLocal
        s += "\n Distant\t: " + self.eltDistant
        s += "\n À synchroniser\t: " + str(self.synchronise)
        return s
    def toggle(self):
        """ Permutte la valeur de synchronisation de l'élément"""
        self.synchronise = not self.synchronise




class Synchronisation:
    def __init__(self):
        self.serveur = "jerep6@cloud"
        self.optgenerales = "-av --delete --exclude-from " + sys.path[0] + "/exclude.rsync"
        self.optssh = "ssh -p 22 -i /home/jerep6/.ssh/id_dsa"
        self.elements = list()
        self.prompt = True #Indique s'il faut demander à l'utilisateur de confirmer la synchro



    def ajouterElement(self, elt):
        self.elements.append(elt)
        
    def changerValeurElements(self, elementsAChanger):
        """ Change la propriété synchonise des éléments """
        try:
            for unNumero in elementsAChanger:
                self.elements[int(unNumero)].toggle()
        except ValueError as e:
            print(e)
            
    def setValeurElements(self, elementsAChanger, valeur):
        """ Postionne la valeur de synchosnisation des éléments """
        for unNumero in elementsAChanger:
            self.elements[int(unNumero)].synchronise = valeur

    def afficherElements(self):
        """ Affiche tous les éléments à syncroniser """
        
        print("-----------------------------------------------")
        for i, unElement in enumerate(self.elements):
            print("## " + str(i) + " ##")
            print(unElement)
            print("")
        print("----------------------------------------------\n")
    
    def synchronisationInteractive(self):
        """Lance la syncronisation des éléments en demandant à l'utilisateur lesquels il souhaite synchroniser"""
        
        action = Action.SAISIR
        while action == Action.SAISIR:
            #Affichage des elts
            self.afficherElements()
            # Demande à l'utilisateur de modifier la valeur de synchronisation des éléments
            saisie = input("Saisie (h pour l'aide) : ")
            action = self.gererSaisieInteractive(saisie)
        
        self.gererAction(action)


    def gererSaisieInteractive(self, saisie):
        """ En fonction de la saisie du l'utilisateur, effectue les opérations nécessaires. N'effectue pas de traitement
        métier tel que la synchronisation. Prépare uniquement les données """
        
        # Action à réaliser après la saisie de l'utilisateur
        action = Action.QUITTER
        # liste des éléments dont on veut changer la valeur de synchronisation
        elementsAChanger = list()
        
        if saisie == "a": # tous les éléments sont à sélectionner
            action = Action.SAISIR
            elementsAChanger = range(len(self.elements))
        elif saisie == "u": # synchronisation montante
            action = Action.UPLOAD
        elif saisie == "d": # synchronisation descendante
            action = Action.DOWNLOAD
        elif saisie == "h": # aide
            action = Action.SAISIR
            self.aideSaisieInteractive()
        elif saisie == "q": # quitter
            action = Action.QUITTER
        else :
            action = Action.SAISIR
            elementsAChanger = saisie.split(" ")
        
        # S'il y a des éléments à changer => changement de la valeur de synchronisation
        if elementsAChanger:
            self.changerValeurElements(elementsAChanger)
            
        return action
    
    def aideSaisieInteractive(self):
        """ Affiche les opérations possibles lors d'une synchronisation interactive"""
        print("Actions possibles : ")
        print("num1 num2,...\t:    pour changer la valeur de synchonisation des éléments")            
        print("a\t\t:    pour changer la valeur de tous des éléments")
        print("h\t\t:    affiche ce message")
        print("u\t\t:    upload les fichiers locaux sur le serveur distant")
        print("d\t\t:    télécharge les fichiers distants dans les dossiers locaux")
        print("q\t\t:    quitter")

    def gererArguments(self, arguments):
        action = Action.QUITTER
        # mode interactif implicite (pas d'argument)
        if len(arguments) <= 1:
            action = Action.INTERACTIF
        else:
            # mode interactif explicite
            if arguments[1] == "--interactif":
                action = Action.INTERACTIF
            else:
                #Action principale (upload/download)
                if arguments[1] == "--push":
                    action = Action.UPLOAD
                elif arguments[1] == "--pull":
                    action = Action.DOWNLOAD

                try:
                    if arguments[2] == "-f": #force : ne pas demander de confirmation
                        self.prompt = False;
                except:
                    pass
                
        # Traitement particulier pour le mode interactif
        if action == Action.INTERACTIF:
            self.synchronisationInteractive()
        else: # sinon gestion de l'action
            self.gererAction(action);
        
    def gererAction(self, action):        
        # SI uploa ou download demande à l'utilisateur de confirmer
        if action == Action.DOWNLOAD or action == Action.UPLOAD:
            if self.prompt:
                reponse = input(action+" : vous allez écraser les données. Continuer [o/n] ? ")
                if reponse != "o":
                    sys.exit()
            
            if action == Action.DOWNLOAD:
                for unElement in self.elements:
                    if unElement.synchronise:
                        print(unElement)
                        os.system("rsync " + self.optgenerales + " -e \"" + self.optssh + "\" " + self.serveur + ":" + unElement.eltDistant + " " + unElement.eltLocal)
    
            elif action == Action.UPLOAD:
                for unElement in self.elements:
                    if unElement.synchronise:
                        print(unElement)
                        os.system("rsync " + self.optgenerales + " -e \"" + self.optssh + "\" " + unElement.eltLocal + " " + self.serveur + ":" + unElement.eltDistant)
        else:
            sys.exit()


sync = Synchronisation()
sync.ajouterElement(ElementDeSynchronisation("/mnt/donnees/Perso/", "/mnt/Jeremy/Perso/", True))
sync.ajouterElement(ElementDeSynchronisation("/mnt/donnees/Code/", "/mnt/Jeremy/Code/", False))
sync.gererArguments(sys.argv)

#print(sys.path[0])
#print(os.path.dirname(__file__))
#print(os.path.dirname(os.path.realpath(__file__)))
