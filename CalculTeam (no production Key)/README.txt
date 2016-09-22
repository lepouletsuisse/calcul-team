////README\\\\

This application will take a .csv file in entry with the following syntaxe:
team;membre;statut;pseudoIG;Roster

It will parse it and output the folloing files (Can be modified in the config.txt file):
Output.txt:
	This file contains all the teams with all the rosters and all the players with the power of each one
Summary.txt:
	This file contains all the teams with all the rosters only
Seedings.txt:
	This file contains the automatically seedings done by the script arranged with their power

You can't use this script like this, you'll need do the following steps:

1. Take the config_exemple.txt file, rename it to config.txt
2. Set inside your official API dev Key from RIOT in the section APIKeys -> ENDAPIKeys (You can set multiple key. If you do like this, you also have to set the correct settings)
3. When this is done, you can modify the settings but globaly, i advise you to not touch it. If you want more explanation about how the config.txt file works, you can ask me :)
4. Put your proper formed .csv file in the folder with the name specified in the config.txt file under "INPUT_FILENAME"
5. Be sure Python 3 is installed on your machine (c.f: https://www.python.org/download/releases/3.0/)
6. Be sure you have internet
7. Execute the CalculTeam.py script either with a editor or in command line.

If everything work well, you'll see the request and after something 2 minutes, you'll get all your output files

Tips: If you see there is some error line in the console, don'w worry, this only mean that the specified summoner name either has not be found or is unranked

Contact me if you have any questions! ;)

Enjoy :)

Le Poulet Suisse
https://github.com/lepouletsuisse