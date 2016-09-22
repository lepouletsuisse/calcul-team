import codecs
import sys

#Classe--------------
class Player:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

    def __repr__(self):
        result = ""
        playerStr = "".join([str(player) + "/" for player in self.players])
        #playerStr += "/"
        playerStr = playerStr[:len(playerStr) - 1]
        result += self.name + ":" + playerStr

        return result

#Constante----------
INPUT_FILENAME = "Input.txt"
OUTPUT_FILNAME = INPUT_FILENAME + ".tmp"

INDIVIDUEL_TEAM_NAME = "///Joueurs individuel\\\\\\"
INDIVIDUEL_ROSTER_NAME = "///Joueurs individuel\\\\\\"

#Méthodes--------------
def setConfig(input_filename, output_filename):
    global INPUT_FILENAME, OUTPUT_FILNAME
    INPUT_FILENAME = input_filename
    OUTPUT_FILNAME = output_filename

def printing(teams):
    tmp_stdout = sys.stdout
    sys.stdout = open(OUTPUT_FILNAME, "w")
    for name, team in teams.items():
        print(team)
    sys.stdout = tmp_stdout

def transformFile(input_filename, output_filename):
    print("Transforming the input file...")
    setConfig(input_filename, output_filename)
    teams = {}
    firstLine = 0
    with codecs.open(INPUT_FILENAME, encoding='utf8') as fp:
        for line in fp:
            if firstLine == 0:
                firstLine = 1
                continue
            teamIndice = line.find(';')
            teamName = line[:teamIndice].strip()
            if teamName == "":
                teamName = INDIVIDUEL_TEAM_NAME

            memberIndice = line.find(';', teamIndice + 1)
            memberName = line[teamIndice + 1: memberIndice].strip()
            statutIndice = line.find(';', memberIndice + 1)
            if line[memberIndice + 1:statutIndice].strip() == "preins":
                continue
            playerIndice = line.find(';', statutIndice + 1)
            playerName = line[statutIndice + 1: playerIndice].strip(" ,\r\n")
            if playerName == "":
                playerName = memberName

            rosterName = line[playerIndice + 1:len(line) - 1].strip()
            if teamName == INDIVIDUEL_TEAM_NAME:
                rosterName = INDIVIDUEL_ROSTER_NAME

            teamRosterName = teamName + " (" + rosterName + ")"

            if teamRosterName not in teams:
                team = Team(teamRosterName)
                teams[team.name] = team
            else:
                team = teams[teamRosterName]


            team.players.append(Player(playerName))
    print("Input file transformed!")
    printing(teams)

