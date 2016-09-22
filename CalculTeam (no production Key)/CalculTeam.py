import urllib.request
from urllib.parse import quote
import json
import sys
import os
import time
from TransformToInput import transformFile, transformFileFestigeek


# Classe------------------------
class Key:
    def __init__(self, value, owner):
        self.value = value
        self.owner = owner
        self.nbRequest = 0


class Roster:
    def __init__(self):
        self.name = ""
        self.team = Team()
        self.players = []
        self.power = 0

    def __repr__(self):
        ret = self.name + " (Power: " + str(self.power) + ")\n"
        for player in self.players:
            ret += "\t\t - " + str(player) + "\n"
        return ret


class Team:
    def __init__(self):
        self.name = ""
        self.rosters = []

    def __repr__(self):
        i = 0
        ret = "----" + self.name + "----\n"
        for roster in self.rosters:
            i += 1
            ret += "\t" + str(i) + ". " + str(roster) + "\n"

        return ret


class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.division = ""
        self.tier = ""
        self.power = 0

    def __repr__(self):
        ret = ""
        if self.id == -1:
            ret += "*"
        ret += self.name + "(" + str(self.id) + "): " \
               + self.tier + " " + self.division + " (Power: " + str(self.power) + ")"
        return ret


# Constante-------------------
# Toute les constante sont initialisé avec des valeurs par défaut
# Caractère de commentaire
COMMENT = '?'

# Set le round robin pour les API keys. 1 = RR, 0 = Erreur
ROUND_ROBIN = 1

# Utilisation d'une seul clé (0) ou plusieurs clé (1)
MULTIPLE_API_KEY = 0

# Ecrire dans un fichier ou dans la console. Console = 0, fichier = 1
PRINTING = 1

# Crée un résumer des équipes. 1 = Summary, 0 = None
SUMMARY = 1

# Rankings par defaut pour les UNRANKED (Set uniquement le nombre de point)
# Si SET_DEFAULT = 1 alors on donne des point par default, sinon ignore les unranked dans le calcul des points
SET_DEFAULT = 0
DEFAULT_DIVISION = "V"
DEFAULT_TIER = "SILVER"
DEFAULT_NAME = "UNRANKED"

# Dictionnaire pour comptage de points
DIVISION_POINT = {"I": 4, "II": 3, "III": 2, "IV": 1, "V": 0}
TIER_POINT = {"BRONZE": 0, "SILVER": 1, "GOLD": 2, "PLATINUM": 3, "DIAMOND": 4, "MASTER": 5, "CHALLENGER": 6}

# Clé dev RIOT
API_KEYS = []

# Fichier d'entree-sortie:
# Format dans le fichier d'entree:
#   Team1: player1 / player2 / player3 / player4 / player5
#   Team2: player1 / player2 / player3 / player4 / player5
#   ...
INPUT_FILENAME = "Input.txt"
INPUTTMP_FILENAME = INPUT_FILENAME + ".tmp"
OUTPUT_FILENAME = "Output.txt"
SUMMARY_FILENAME = "Summary.txt"
CONFIG_FILENAME = "config.txt"
SEEDING_FILENAME = "Seeding.txt"

# Efface les fichiers temporaires. Garder = 0
DELETE_TMP_FILES = 0


# Méthode---------------

def setConfig():
    print("Setting the config...")
    APIKEY = 0
    global COMMENT, \
        ROUND_ROBIN, \
        PRINTING, \
        SET_DEFAULT, \
        DEFAULT_DIVISION, \
        DEFAULT_TIER, \
        DEFAULT_NAME, \
        INPUT_FILENAME, \
        INPUTTMP_FILENAME, \
        INPUTTMPFG_FILENAME, \
        OUTPUT_FILENAME, \
        SUMMARY_FILENAME, \
        SEEDING_FILENAME, \
        SUMMARY, \
        MULTIPLE_API_KEY, \
        DELETE_TMP_FILES

    # Ouverture du fichier d'entree
    try:
        with open(CONFIG_FILENAME) as fp:
            for line in fp:
                if line[0] == '#' or line[0] == '\n':
                    continue
                param = line[:line.find('=')].strip(' ')
                value = line[line.find('=') + 1:].strip(' \n')
                print(param + " = " + value)
                if param == "COMMENT":
                    COMMENT = value
                elif param == "ROUND_ROBIN":
                    ROUND_ROBIN = int(value)
                elif param == "MULTIPLE_API_KEY":
                    MULTIPLE_API_KEY = int(value)
                elif param == "PRINTING":
                    PRINTING = int(value)
                elif param == "SET_DEFAULT":
                    SET_DEFAULT = int(value)
                elif param == "DEFAULT_DIVISION":
                    DEFAULT_DIVISION = value
                elif param == "DEFAULT_TIER":
                    DEFAULT_TIER = value
                elif param == "DEFAULT_NAME":
                    DEFAULT_NAME = value
                elif param == "APIKeys":
                    APIKEY = 1
                elif param == "ENDAPIKeys":
                    APIKEY = 0
                elif param == "INPUT_FILENAME":
                    INPUT_FILENAME = value
                    INPUTTMP_FILENAME = INPUT_FILENAME + ".tmp"
                elif param == "OUTPUT_FILENAME":
                    OUTPUT_FILENAME = value
                elif param == "SUMMARY_FILENAME":
                    SUMMARY_FILENAME = value
                elif param == "SEEDING_FILENAME":
                    SEEDING_FILENAME = value
                elif param == "SUMMARY":
                    SUMMARY = int(value)
                elif param == "DELETE_TMP_FILES":
                    DELETE_TMP_FILES = int(value)
                elif APIKEY == 1:
                    API_KEYS.append(Key(value, param))
                else:
                    raise NameError("Bad param in " + CONFIG_FILENAME + "! param = " + param)
        print("Config set!")
    except FileNotFoundError as e:
        print("No " + CONFIG_FILENAME + " file found! Abort")
        exit(1)


# Trouve un joueur dans le dic a partir de son id
def findPlayerInList(id, playerList):
    for player in playerList:
        if player.id == id:
            return player
    raise NameError('PlayerNotInDic: The id ' + str(id) + " is not in the list!")


# Retourne un dictionnaire
def sendRequest(url):
    # Verifie que la variable existe
    if not hasattr(sendRequest, "counter"):
        sendRequest.counter = 0
    # Switch de clé si on atteint le nombre de requete max
    if API_KEYS[sendRequest.counter].nbRequest == 10:
        if MULTIPLE_API_KEY == 0:
            print("Waiting 10 seconds...")
            time.sleep(10)
            API_KEYS[sendRequest.counter].nbRequest = 0
        else:
            sendRequest.counter += 1
            if sendRequest.counter >= len(API_KEYS):
                if ROUND_ROBIN == 0:
                    raise NameError("sendRequestException: Not enough API KEY")
                print("Round Robin!")
                sendRequest.counter = 0
                for key in API_KEYS:
                    key.nbRequest = 0
            print("API KEY switched to " + API_KEYS[sendRequest.counter].owner)
    print(url + '?api_key=' + API_KEYS[sendRequest.counter].value)
    response = {}
    try:
        response = urllib.request.urlopen(url + '?api_key=' + API_KEYS[sendRequest.counter].value)
    except urllib.error.HTTPError as e:
        print("Error! " + str(e))
        return "404"
    except urllib.error.URLError:
        print("-----TIMEOUT-----")
        return "404"
    finally:
        API_KEYS[sendRequest.counter].nbRequest += 1
    return json.loads(response.read().decode("UTF-8"))


def commonPrint(teams):
    nbPlayer = 0
    nbRoster = 0
    for team in teams:
        for roster in team.rosters:
            nbRoster += 1
            nbPlayer += len(roster.players)
    print("* = not found player (Member name display)")
    print("This tournament got " + str(nbPlayer) + " players and " + str(nbRoster) + " rosters for " + str(
        len(teams)) + " teams!\n\n")


def printing(teams, filename):
    if PRINTING == 1:
        tmp_stdout = sys.stdout
        try:
            sys.stdout = open(filename, "w")
        except FileNotFoundError:
            print("No " + filename + " file found! Abort")
            exit(1)

    commonPrint(teams)

    for team in teams:
        print(str(team) + "\n")
    if PRINTING == 1:
        sys.stdout = tmp_stdout


def printingSummary(teams, filename):
    if PRINTING == 1:
        tmp_stdout = sys.stdout
        try:
            sys.stdout = open(filename, "w")
        except FileNotFoundError:
            print("No " + filename + " file found! Abort")
            exit(1)

    commonPrint(teams)

    for team in teams:
        print("----" + team.name + "----\n")
        for roster in team.rosters:
            print("\t- " + roster.name + " (Power: " + str(roster.power) + ")")
    if PRINTING == 1:
        sys.stdout = tmp_stdout


def seeding(teams, filename):
    rosterWithoutUnranked = []
    for team in teams:
        for roster in team.rosters:
            if len(roster.players) > 1:
                rosterWithoutUnranked.append(roster)
    sortedRosters = sorted(rosterWithoutUnranked, key=lambda x: x.power, reverse=True)
    median = len(sortedRosters) // 2
    low = median // 2
    high = int(median * 1.5)
    seedings = []

    for i in range(0, len(sortedRosters) // 4):
        tmpTuple = (sortedRosters[i], sortedRosters[i + low])
        seedings.append(tmpTuple)
        tmpTuple = (sortedRosters[i + median], sortedRosters[i + high])
        seedings.append(tmpTuple)

    if len(sortedRosters) != len(seedings) * 2:
        print("Pas le bon nombre de roster!! sortedRoster: " + str(len(sortedRosters)) + " // seedings: " + str(
            len(seedings) * 2))
    else:
        print("Ok pour le nombre")

    if PRINTING == 1:
        tmp_stdout = sys.stdout
        try:
            sys.stdout = open(filename, "w")
        except FileNotFoundError:
            print("No " + filename + " file found! Abort")
            exit(1)

    commonPrint(teams)

    for tupleRoster in seedings:
        print("\"" + tupleRoster[0].team.name + "\" " + tupleRoster[0].name + "(Power: " + str(
            tupleRoster[0].power) + ") VS " + "\"" + tupleRoster[1].team.name + "\" " + tupleRoster[
                  1].name + "(Power: " + str(tupleRoster[1].power) + ")\n")
    if PRINTING == 1:
        sys.stdout = tmp_stdout


def deleteTmpFiles(*files):
    if DELETE_TMP_FILES == 0:
        return
    for file in files:
        os.remove(file)


# Main---------------

# Fonction principal
def main():
    setConfig()
    if SET_DEFAULT == 0:
        print("Ignoring UNRANKED people!")
    else:
        print("Setting power of UNRANKED as " + DEFAULT_TIER + " " + DEFAULT_DIVISION + "!")

    # Ligne pour FestiGeek
    # Beaucoup de bordel dans excel!
    # Numéro de commande	Nom	Prénom	Nom d'utilisateur	Pseudo Steam	Pseudo Riot	Battle TAG	Nom de Team	Participation tournoi principal	Mineur	Repas vendredi soir	Petit déj samedi matin	Repas samedi midi	Repas samedi soir	Petit déj dimanche matin	Repas dimanche midi	Montant total	Moyen de paiement	Statut paiement	Etudiants	Présent

    transformFileFestigeek(INPUT_FILENAME, INPUTTMP_FILENAME)

    # Ligne pour PolyLan
    # team;membre;statut;pseudoIG;Roster
    #transformFile(INPUTTMPFG_FILENAME, INPUTTMP_FILENAME)

    # Ouverture du fichier d'entree
    try:
        with open(INPUTTMP_FILENAME) as fp:
            teams = []
            for line in fp:
                # Charactère de commentaire dans le fichier : ?
                if line[0] == COMMENT:
                    continue
                # Initialisation d'une team + roster
                actualTeam = Team()
                actualRoster = Roster()
                players = []
                indiceTeam = oldplayer = line.find('(')
                rosterIndice = line.find(')')

                # Nom de la team + roster
                actualTeam.name = line[:indiceTeam].strip()
                actualRoster.name = line[indiceTeam + 1:rosterIndice]
                exist = 0
                ind = 0
                for index, team in enumerate(teams):
                    if team.name == actualTeam.name:
                        exist = 1
                        ind = index
                if exist == 1:
                    actualTeam = teams[ind]

                else:
                    teams.append(actualTeam)
                actualTeam.rosters.append(actualRoster)
                actualRoster.team = actualTeam

                # Remplie le roster de players
                oldplayer = line.find(':', 0)
                while line.find(':', oldplayer + 1) != -1:
                    oldplayer = line.find(':', oldplayer + 1)

                while oldplayer != -1:
                    oldplayer += 1
                    players.append(line[oldplayer:line.find('/', oldplayer)].strip(' '))
                    oldplayer = line.find('/', oldplayer)

                # Get le tableau d'ids des players
                allPlayersEncode = ''.join([quote(player) + "," for player in players])
                allPlayersEncode = allPlayersEncode[:len(allPlayersEncode) - 1]

                response = sendRequest('https://euw.api.pvp.net/api/lol/euw/v1.4/summoner/by-name/' + allPlayersEncode)
                if response != "404":
                    for name, data in response.items():
                        actualRoster.players.append(Player(name, data["id"]))
                for player1 in players:
                    exist = 0
                    player1 = player1.strip().lower().replace(' ', '')
                    for player2 in actualRoster.players:
                        if player2.name == player1:
                            exist = 1
                    if exist == 0:
                        actualRoster.players.append(Player(player1, -1))

                # Trouve la force de chaqun et lui attribut des points
                allIdEncode = "".join(
                    [(str(player.id) + "," if player.id != -1 else '') for player in actualRoster.players])
                response = sendRequest(
                    "https://euw.api.pvp.net/api/lol/euw/v2.5/league/by-summoner/" + allIdEncode + "/entry")
                if str(response) != "404":
                    for id, data in response.items():
                        for tmpData in data:
                            actualPlayer = findPlayerInList(int(id), actualRoster.players)
                            actualPlayer.tier = tmpData["tier"]
                            actualPlayer.division = tmpData["entries"][0]["division"]
                            actualPlayer.power = DIVISION_POINT[actualPlayer.division] + TIER_POINT[
                                                                                             actualPlayer.tier] * 5

                # Set le power des unranked aux valeurs par défaut et calcul le power de la team
                countPlayer = 0
                for player in actualRoster.players:
                    if player.tier == "" or player.division == "":
                        player.tier = DEFAULT_NAME
                        if SET_DEFAULT == 1:
                            player.power = DIVISION_POINT[DEFAULT_DIVISION] + TIER_POINT[DEFAULT_TIER] * 5
                        else:
                            player.power = -1
                    if player.power != -1:
                        actualRoster.power += player.power
                        countPlayer += 1

                if countPlayer != 0:
                    actualRoster.power /= countPlayer

            printing(teams, OUTPUT_FILENAME)
            if SUMMARY == 1:
                printingSummary(teams, SUMMARY_FILENAME)
            seeding(teams, SEEDING_FILENAME)
            fp.close()
        deleteTmpFiles(INPUTTMP_FILENAME,)
    except FileNotFoundError:
        print("No " + INPUTTMP_FILENAME + " file found! Abort")
        exit(1)


main()
