from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_admin import Admin
from flask_admin import BaseView, expose
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView

from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
import json
from time import sleep
from datetime import datetime
from threading import Thread

API_KEY = 'e39dc48c64b81913c0ac7024471de184'
FILTER_ID = 309269

MAX_PROFIT = 100.0
MIN_PROFIT = 1.0

TIME_LIMIT = 1

clientIdList = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pwd1234!@#$'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)


BOOKMAKERS = {
    "1" : "Pinnacle",
    "19": "Unibet"
    }

SPORTS = {
    "8" : {"name" : "Tennis"      , "icon" : "🎾"},
    "2" : {"name" : "Basketball"  , "icon" : "🏀"},
    "7" : {"name" : "Soccer"      , "icon" : "⚽"},
    "10": {"name" : "Am. Football", "icon" : "🏈"},
    "9" : {"name" : "Volleyball"  , "icon" : "🏐"},
    "1" : {"name" : "Baseball"    , "icon" : "⚾"},
    "6" : {"name" : "Hockey"      , "icon" : "🏒"},
    "13": {"name" : "Table Tennis", "icon" : "🏓"}
    }

PERIODS = {
    "Tennis" : {
        "3"   : {"Pinnacle": "period:0" , "Unibet": "Partido", "default": "Match"        },
        "5"   : {"Pinnacle": "period:1" , "Unibet": "Set"    , "default": "1st Set"      },
        "6"   : {"Pinnacle": "period:2" , "Unibet": "Set"    , "default": "2nd Set"      },
        "7"   : {"Pinnacle": "period:3" , "Unibet": "Set"    , "default": "3rd Set"      },
        "8"   : {"Pinnacle": "period:4" , "Unibet": "Set"    , "default": "4th Set"      },
        "14"  : {"Pinnacle": "period:6" , "Unibet": "Juego"  , "default": "Set 1 Game 1" },
        "15"  : {"Pinnacle": "period:7" , "Unibet": "Juego"  , "default": "Set 1 Game 2" },
        "16"  : {"Pinnacle": "period:8" , "Unibet": "Juego"  , "default": "Set 1 Game 3" },
        "17"  : {"Pinnacle": "period:9" , "Unibet": "Juego"  , "default": "Set 1 Game 4" },
        "18"  : {"Pinnacle": "period:10", "Unibet": "Juego"  , "default": "Set 1 Game 5" },
        "19"  : {"Pinnacle": "period:11", "Unibet": "Juego"  , "default": "Set 1 Game 6" },
        "20"  : {"Pinnacle": "period:12", "Unibet": "Juego"  , "default": "Set 1 Game 7" },
        "21"  : {"Pinnacle": "period:13", "Unibet": "Juego"  , "default": "Set 1 Game 8" },
        "22"  : {"Pinnacle": "period:14", "Unibet": "Juego"  , "default": "Set 1 Game 9" },
        "23"  : {"Pinnacle": "period:15", "Unibet": "Juego"  , "default": "Set 1 Game 10"},
        "24"  : {"Pinnacle": "period:16", "Unibet": "Juego"  , "default": "Set 1 Game 11"},
        "25"  : {"Pinnacle": "period:17", "Unibet": "Juego"  , "default": "Set 1 Game 12"},
        "26"  : {"Pinnacle": "period:18", "Unibet": "Juego"  , "default": "Set 1 Game 13"},
        "44"  : {"Pinnacle": "period:19", "Unibet": "Juego"  , "default": "Set 2 Game 1" },
        "45"  : {"Pinnacle": "period:20", "Unibet": "Juego"  , "default": "Set 2 Game 2" },
        "46"  : {"Pinnacle": "period:21", "Unibet": "Juego"  , "default": "Set 2 Game 3" },
        "47"  : {"Pinnacle": "period:22", "Unibet": "Juego"  , "default": "Set 2 Game 4" },
        "48"  : {"Pinnacle": "period:23", "Unibet": "Juego"  , "default": "Set 2 Game 5" },
        "49"  : {"Pinnacle": "period:24", "Unibet": "Juego"  , "default": "Set 2 Game 6" },
        "50"  : {"Pinnacle": "period:25", "Unibet": "Juego"  , "default": "Set 2 Game 7" },
        "51"  : {"Pinnacle": "period:26", "Unibet": "Juego"  , "default": "Set 2 Game 8" },
        "52"  : {"Pinnacle": "period:27", "Unibet": "Juego"  , "default": "Set 2 Game 9" },
        "53"  : {"Pinnacle": "period:28", "Unibet": "Juego"  , "default": "Set 2 Game 10"},
        "54"  : {"Pinnacle": "period:29", "Unibet": "Juego"  , "default": "Set 2 Game 11"},
        "55"  : {"Pinnacle": "period:30", "Unibet": "Juego"  , "default": "Set 2 Game 12"},
        "56"  : {"Pinnacle": "period:31", "Unibet": "Juego"  , "default": "Set 2 Game 13"},
        "57"  : {"Pinnacle": "period:32", "Unibet": "Juego"  , "default": "Set 3 Game 1" },
        "58"  : {"Pinnacle": "period:33", "Unibet": "Juego"  , "default": "Set 3 Game 2" },
        "59"  : {"Pinnacle": "period:34", "Unibet": "Juego"  , "default": "Set 3 Game 3" },
        "60"  : {"Pinnacle": "period:35", "Unibet": "Juego"  , "default": "Set 3 Game 4" },
        "61"  : {"Pinnacle": "period:36", "Unibet": "Juego"  , "default": "Set 3 Game 5" },
        "62"  : {"Pinnacle": "period:37", "Unibet": "Juego"  , "default": "Set 3 Game 6" },
        "63"  : {"Pinnacle": "period:38", "Unibet": "Juego"  , "default": "Set 3 Game 7" },
        "64"  : {"Pinnacle": "period:39", "Unibet": "Juego"  , "default": "Set 3 Game 8" },
        "65"  : {"Pinnacle": "period:40", "Unibet": "Juego"  , "default": "Set 3 Game 9" },
        "66"  : {"Pinnacle": "period:41", "Unibet": "Juego"  , "default": "Set 3 Game 10"},
        "67"  : {"Pinnacle": "period:42", "Unibet": "Juego"  , "default": "Set 3 Game 11"},
        "68"  : {"Pinnacle": "period:43", "Unibet": "Juego"  , "default": "Set 3 Game 12"},
        "71"  : {"Pinnacle": "period:44", "Unibet": "Juego"  , "default": "Set 3 Game 13"},
        "113" : {"Pinnacle": "period:45", "Unibet": "Juego"  , "default": "Set 4 Game 1" },
        "114" : {"Pinnacle": "period:46", "Unibet": "Juego"  , "default": "Set 4 Game 2" },
        "115" : {"Pinnacle": "period:47", "Unibet": "Juego"  , "default": "Set 4 Game 3" },
        "116" : {"Pinnacle": "period:48", "Unibet": "Juego"  , "default": "Set 4 Game 4" },
        "117" : {"Pinnacle": "period:49", "Unibet": "Juego"  , "default": "Set 4 Game 5" },
        "118" : {"Pinnacle": "period:50", "Unibet": "Juego"  , "default": "Set 4 Game 6" },
        "119" : {"Pinnacle": "period:51", "Unibet": "Juego"  , "default": "Set 4 Game 7" },
        "120" : {"Pinnacle": "period:52", "Unibet": "Juego"  , "default": "Set 4 Game 8" },
        "121" : {"Pinnacle": "period:53", "Unibet": "Juego"  , "default": "Set 4 Game 9" },
        "122" : {"Pinnacle": "period:54", "Unibet": "Juego"  , "default": "Set 4 Game 10"},
        "123" : {"Pinnacle": "period:55", "Unibet": "Juego"  , "default": "Set 4 Game 11"},
        "124" : {"Pinnacle": "period:56", "Unibet": "Juego"  , "default": "Set 4 Game 12"},
        "156" : {"Pinnacle": "period:67", "Unibet": "Juego"  , "default": "Set 4 Game 13"},
        "125" : {"Pinnacle": "period:57", "Unibet": "Juego"  , "default": "Set 5 Game 1" },
        "126" : {"Pinnacle": "period:58", "Unibet": "Juego"  , "default": "Set 5 Game 2" },
        "127" : {"Pinnacle": "period:59", "Unibet": "Juego"  , "default": "Set 5 Game 3" },
        "128" : {"Pinnacle": "period:60", "Unibet": "Juego"  , "default": "Set 5 Game 4" },
        "129" : {"Pinnacle": "period:61", "Unibet": "Juego"  , "default": "Set 5 Game 5" },
        "130" : {"Pinnacle": "period:62", "Unibet": "Juego"  , "default": "Set 5 Game 6" },
        "131" : {"Pinnacle": "period:63", "Unibet": "Juego"  , "default": "Set 5 Game 7" },
        "132" : {"Pinnacle": "period:64", "Unibet": "Juego"  , "default": "Set 5 Game 8" },
        "133" : {"Pinnacle": "period:65", "Unibet": "Juego"  , "default": "Set 5 Game 9" },
        "134" : {"Pinnacle": "period:66", "Unibet": "Juego"  , "default": "Set 5 Game 10"},
        "159" : {"Pinnacle": "period:68", "Unibet": "Juego"  , "default": "Set 5 Game 11"},
        "161" : {"Pinnacle": "period:69", "Unibet": "Juego"  , "default": "Set 5 Game 12"},
        "169" : {"Pinnacle": "period:70", "Unibet": "Juego"  , "default": "Set 5 Game 13"}
    },
    
    "Basketball" : {
        "3"   : {"Pinnacle": "period:0", "Unibet":  "Partido"      , "default": "Game"       },
        "10"  : {"Pinnacle": "period:1", "Unibet":  "Primer tiempo", "default": "1st Half"   },
        "13"  : {"Pinnacle": "period:2", "Unibet":  "Second Half"  , "default": "2nd Half"   },
        "5"   : {"Pinnacle": "period:3", "Unibet":  "1º cuarto"    , "default": "1st Quarter"},
        "6"   : {"Pinnacle": "period:4", "Unibet":  "2º cuarto"    , "default": "2nd Quarter"},
        "7"   : {"Pinnacle": "period:5", "Unibet":  "3º cuarto"    , "default": "3rd Quarter"},
        "8"   : {"Pinnacle": "period:6", "Unibet":  "4º cuarto"    , "default": "4th Quarter"}
        },
    
    "Soccer" : {
        "4"   : {"Pinnacle": "period:0", "Unibet":  "Tiempo reglamentario", "default": "Match"   },
        "5"   : {"Pinnacle": "period:1", "Unibet":  "Primer tiempo",        "default": "1st Half"},
        "6"   : {"Pinnacle": "period:2", "Unibet":  "Second Half",        "default": "2nd Half"}
        }
}

MARKETS = {
    "1":   {"Pinnacle": "Money Line%s – %s"          , "Unibet": "%s"                   }, # Team1 Win
    "2":   {"Pinnacle": "Money Line%s – %s"          , "Unibet": "%s"                   }, # Team2 Win
    "19":  {"Pinnacle": "Total%s – %s"               , "Unibet": "Total"      }, # Total Over(%s)
    "20":  {"Pinnacle": "Total%s – %s"               , "Unibet": "Total"      }, # Total Under(%s)
    "68":  {"Pinnacle": "Total – %s"                 , "Unibet": "Total"      }, # Total Over(%s) - Tie Break
    "69":  {"Pinnacle": "Total – %s"                 , "Unibet": "Total"      }, # Total Under(%s) - Tie Break
    "51":  {"Pinnacle": "Total (Corners) – %s"       , "Unibet": "Total"      }, # Total Over(%s) - Corners
    "52":  {"Pinnacle": "Total (Corners) – %s"       , "Unibet": "Total"      }, # Total Under(%s) - Corners
    "21":  {"Pinnacle": "Team Total – %s"        , "Unibet": "Total"      }, # Total Over(%s) for Team1
    "22":  {"Pinnacle": "Team Total – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team1
    "23":  {"Pinnacle": "Team Total – %s"        , "Unibet": "Total"      }, # Total Over(%s) for Team2
    "24":  {"Pinnacle": "Team Total – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team2
    "53":  {"Pinnacle": "Team Total (Corners) – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team1 - Corners
    "54":  {"Pinnacle": "Team Total (Corners) – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team1 - Corners
    "55":  {"Pinnacle": "Team Total (Corners) – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team2 - Corners
    "56":  {"Pinnacle": "Team Total (Corners) – %s"        , "Unibet": "Total"      }, # Total Under(%s) for Team2 - Corners
    "17":  {"Pinnacle": "Handicap%s – %s"        , "Unibet": "Hándicap"   }, # Asian Handicap1(%s)
    "18":  {"Pinnacle": "Handicap%s – %s"        , "Unibet": "Hándicap"   }, # Asian Handicap2(%s)
    "131": {"Pinnacle": "Handicap (Sets) – %s"   , "Unibet": "Hándicap"   }, # Asian Handicap1(%s) - Sets
    "132": {"Pinnacle": "Handicap (Sets) – %s"   , "Unibet": "Hándicap"   }, # Asian Handicap2(%s) - Sets
    "49":  {"Pinnacle": "Handicap (Corners) – %s", "Unibet": "Hándicap"   }, # Asian Handicap1(%s) - Corners
    "50":  {"Pinnacle": "Handicap (Corners) – %s", "Unibet": "Hándicap"   }, # Asian Handicap2(%s) - Corners
    "3":   {"Pinnacle": "Handicap – %s"          , "Unibet": "Apuesta sin empate"}, # Asian Handicap1(0.0)/Draw No Bet
    "4":   {"Pinnacle": "Handicap – %s"          , "Unibet": "Apuesta sin empate"}, # Asian Handicap2(0.0)/Draw No Bet
    "5":   {"Pinnacle": "Handicap – %s"          , "Unibet": "Hándicap"   }, # European Handicap1(%s)
    "7":   {"Pinnacle": "Handicap – %s"          , "Unibet": "Hándicap"   }  # European Handicap2(%s)
}

LINES = {
    "1":   {"Pinnacle": "%s"                       , "Unibet": "%s"            }, # Team1 Win
    "2":   {"Pinnacle": "%s"                       , "Unibet": "%s"            }, # Team2 Win
    "19":  {"Pinnacle": "Over %s"                  , "Unibet": "Más de %s"     }, # Total Over(%s)
    "20":  {"Pinnacle": "Under %s"                 , "Unibet": "Menos de %s"   }, # Total Under(%s)
    "68":  {"Pinnacle": "Over %s"                  , "Unibet": "Más de %s"     }, # Total Over(%s) - Tie Break
    "69":  {"Pinnacle": "Under %s"                 , "Unibet": "Menos de %s"   }, # Total Under(%s) - Tie Break
    "51":  {"Pinnacle": "Over %s Corners"                  , "Unibet": "Más de %s"     }, # Total Over(%s) - Corners
    "52":  {"Pinnacle": "Under %s Corners"                 , "Unibet": "Menos de %s"   }, # Total Under(%s) - Corners
    "21":  {"Pinnacle": "Over %s(1)"                  , "Unibet": "Más de %s"     }, # Total Over(%s) for Team1
    "22":  {"Pinnacle": "Under %s(1)"                 , "Unibet": "Menos de %s"   }, # Total Under(%s) for Team1
    "23":  {"Pinnacle": "Over %s(2)"                  , "Unibet": "Más de %s"     }, # Total Over(%s) for Team2
    "24":  {"Pinnacle": "Under %s(2)"                 , "Unibet": "Menos de %s"   }, # Total Under(%s) for Team2
    "53":  {"Pinnacle": "Under %s Corners(1)"          , "Unibet": "Total"      }, # Total Under(%s) for Team1 - Corners
    "54":  {"Pinnacle": "Over %s Corners(1)"          , "Unibet": "Total"      }, # Total Under(%s) for Team1 - Corners
    "55":  {"Pinnacle": "Under %s Corners(2)"          , "Unibet": "Total"      }, # Total Under(%s) for Team2 - Corners
    "56":  {"Pinnacle": "Over %s Corners(2)"          , "Unibet": "Total"      }, # Total Under(%s) for Team2 - Corners
    "17":  {"Pinnacle": "1 %s"                       , "Unibet": "1"             }, # Asian Handicap1(%s)
    "18":  {"Pinnacle": "2 %s"                       , "Unibet": "2"             }, # Asian Handicap2(%s)
    "131": {"Pinnacle": "1 %s"                       , "Unibet": "1"             }, # Asian Handicap1(%s) - Sets
    "132": {"Pinnacle": "2 %s"                       , "Unibet": "2"             }, # Asian Handicap2(%s) - Sets
    "49":  {"Pinnacle": "1 %s"                       , "Unibet": "1"             }, # Asian Handicap1(%s) - Corners
    "50":  {"Pinnacle": "2 %s"                       , "Unibet": "2"             }, # Asian Handicap2(%s) - Corners
    "3":   {"Pinnacle": "1 %s"                       , "Unibet": "1"             }, # Asian Handicap1(0.0)/Draw No Bet
    "4":   {"Pinnacle": "2 %s"                       , "Unibet": "2"             }, # Asian Handicap2(0.0)/Draw No Bet
    "5":   {"Pinnacle": "1 %s"                       , "Unibet": "1"             }, # European Handicap1(%s)
    "7":   {"Pinnacle": "2 %s"                       , "Unibet": "2"             }  # European Handicap2(%s)
}


def fetchData():    
    url = 'https://rest-api-lv.betburger.com/api/v1/arbs/bot_pro_search'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'access_token': API_KEY,
        'search_filter[]': FILTER_ID,
        'per_page': 20,
        'event_id': '',
        'show_event_arbs': '',
        'excluded_events[]': '',
        'sort_by': 'percent',
        'excluded_bets[]': '',
        'excluded_bk_events[]': '',
        'bookmakers2[]': '',
        'grouped': ''
    }

    while True:
        newEvents = []
        count = 0
        total_time = 0
        output = ""
        if clientIdList:
            response = requests.post(url, headers=headers, data=data)
            result = response.json()
            try:
                total_time = result["total_time"]
                if total_time >= TIME_LIMIT:
                    bets = result["bets"]
                    count = int(len(bets) / 2)
                    available_event_count = 0
                    for i in range(0, count):
                        L = 1 / bets[i * 2]["koef"] + 1 / bets[i * 2 + 1]["koef"]
                        net_percent = round((1 - L) * 100, 2)
                        if net_percent >= MIN_PROFIT and net_percent <= MAX_PROFIT:
                            bookmaker_data = {"Pinnacle" : {}, "Unibet" : {}}
                            bookmaker_data[BOOKMAKERS[str(bets[i * 2]["bookmaker_id"])]] = bets[i * 2]
                            bookmaker_data[BOOKMAKERS[str(bets[i * 2 + 1]["bookmaker_id"])]] = bets[i * 2 + 1]
                            if not (bookmaker_data["Unibet"] and bookmaker_data["Pinnacle"]):
                                continue
                            event = {"Pinnacle" : {}, "Unibet" : {}, "sports" : "", "percent" : net_percent}
                            for bookmaker in ["Pinnacle", "Unibet"]:
                                bet_data = bookmaker_data[bookmaker]
                                sports = SPORTS[str(bet_data["sport_id"])]["name"]
                                event["sports"] = sports
                                sports_icon = SPORTS[str(bet_data["sport_id"])]["icon"]
                                league = bet_data["bookmaker_league_name"]
                                event_name = bet_data["bookmaker_event_name"]
                                param = bet_data["market_and_bet_type_param"]
                                current_score = bet_data["current_score"]
                                
                                # Period
                                period = PERIODS[sports][str(bet_data["period_id"])][bookmaker]
                                period_default = PERIODS[sports][str(bet_data["period_id"])]["default"]

                                # Market
                                market_id = bet_data["market_and_bet_type"]
                                market = MARKETS[str(market_id)][bookmaker]
                                if bookmaker == "Pinnacle":
                                    if "Corners" in market:
                                        period = "leagueType:Corners"                                    
                                    if market_id == 1 or market_id == 2 or market_id == 17 or market_id == 18 or market_id == 19 or market_id == 20:
                                        prefix = ""
                                        if sports == "Tennis":
                                            if market_id == 1 or market_id == 2:
                                                prefix = " (Sets)"
                                                if "Game" in period_default:
                                                    prefix = " (Games)"
                                            else:
                                                prefix = " (Games)"
                                        market = market %(prefix, period_default)
                                    else:
                                        market = market % period_default
                                else:
                                    if "Corners" in market:
                                        period = "Tiros de Esquina"
                                    if market_id == 5 or market_id == 7:
                                        period = "Líneas Asiáticas"
                                    if market_id == 1 or market_id == 2:
                                        if sports == "Tennis":
                                            market = period_default.replace("Game", "- Juego")
                                        elif sports == "Basketball":
                                            market = market %("Prórroga incluida")
                                        elif sports == "Soccer":
                                            market = market %("Tiempo reglamentario")
                                        else:
                                            pass
                                    if period == "Set" and market == "Total":
                                        market += f" - Set {period_default[0]}"
                                
                                line = LINES[str(market_id)][bookmaker]
                                if market_id == 1 or market_id == 2:
                                    line = event_name.split(" - ")[market_id - 1]
                                else:
                                    if "Total" in market:
                                        line = str(line %param).replace(".0", "")
                                    else: # Handicap
                                        if param > 0:
                                            param = f"+{param}"
                                        else:
                                            param = str(param)
                                        
                                        if bookmaker == "Pinnacle":
                                            if "1" in line:
                                                line = line.replace("1", event_name.split(" - ")[0])
                                            elif "2" in line:
                                                line = line.replace("2", event_name.split(" - ")[1])
                                            else:
                                                pass

                                            if "." not in param:
                                                param += ".0"
                                            line = line %param
                                        if bookmaker == "Unibet":
                                            param  = param.replace(".0", "")
                                            line = f'{event_name.split(" - ")[int(line) - 1]} {param}'
                                            line = line.replace("(W)", "(F)")

                                # Odds
                                odds = bet_data["koef"]

                                if bookmaker == "Pinnacle":
                                    event_id = bet_data["direct_link"].split("/")[0]
                                    link_league = league.replace(' -', '').replace(' ', '-').replace(',', '').lower()
                                    link_event = event_name.replace(' -', '').replace(' ', '-').lower().replace('-(w)', '')
                                    link = f"https://www.pinnacle.com/en/{sports.lower()}/{link_league}/{link_event}/{event_id}/#{period}"
                                if bookmaker == "Unibet":
                                    link = f"https://betplay.com.co/apuestas#event/live/{bet_data['bookmaker_event_direct_link']}"

                                temp = period
                                if bookmaker == "Pinnacle":
                                    temp = period_default
                                event[bookmaker] = {"link":link,"league":league,"event":event_name,"period":temp,"market":market,"line":line,"odds":odds, "current_score" : current_score}
                            
                            if "Handicap (Sets)" in event["Pinnacle"]["market"]:
                                event["Unibet"]["market"] = "Hándicap de sets"
                            if "Handicap (Games)" in event["Pinnacle"]["market"]:
                                event["Unibet"]["market"] = "Hándicap de juegos"
                            if "Total (Games)" in event["Pinnacle"]["market"]:
                                event["Unibet"]["market"] = event["Unibet"]["market"].replace("Total", "Total de juegos")
                            if "Total (Sets)" in event["Pinnacle"]["market"]:
                                event["Unibet"]["market"] = event["Unibet"]["market"].replace("Total", "Total de sets")

                            available_event_count += 1
                            event_for_api = {}
                            event_for_api["no"] = available_event_count
                            event_for_api["sports"] = event["sports"]
                            event_for_api["percent"] = net_percent
                            event_for_api["time"] = total_time
                            event_for_api["bookmaker"] = f'Betplay<br>{event["Unibet"]["current_score"]}<br>Pinnacle<br>{event["Pinnacle"]["current_score"]}'
                            event_for_api["league"] = f'{event["Unibet"]["league"]}<br>{event["Pinnacle"]["league"]}'
                            event_for_api["event"] = f'{event["Unibet"]["event"]}<br>{event["Pinnacle"]["event"]}'
                            event_for_api["period"] = f'{event["Unibet"]["period"]}<br>{event["Pinnacle"]["period"]}'
                            event_for_api["market"] = f'{event["Unibet"]["market"]}<br>{event["Pinnacle"]["market"]}'
                            event_for_api["line"] = f'{event["Unibet"]["line"]}<br>{event["Pinnacle"]["line"]}'
                            event_for_api["odds"] = f'{event["Unibet"]["odds"]}<br>{event["Pinnacle"]["odds"]}'
                            event_for_api["link"] = f'{event["Unibet"]["link"]}<br>{event["Pinnacle"]["link"]}'
                            newEvents.append(event_for_api)
                            
            except Exception as e:
                pass
            output = f'{datetime.now().strftime("%H:%M:%S")}, {str(total_time).zfill(2)}s, {str(count).zfill(2)} Events'
        else:
            output = "No connected clients"
        print(f'{"-"*20} {output.center(25)} {"-"*20}\n')

        if newEvents:
            socketio.emit('server_to_client', newEvents)
            sleep(1.0)
        else:
            sleep(1.0)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    username = db.Column(db.String(1000), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_raw = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    only_visit = db.Column(db.Boolean, default=False)
    all_options = db.Column(db.Boolean, default=False)
    surebetExpireDate = db.Column(db.DateTime)
    mines = db.Column(db.Boolean, default=False)
    minesExpireDate = db.Column(db.DateTime)
    roulette = db.Column(db.Boolean, default=False)
    rouletteExpireDate = db.Column(db.DateTime)
    blackjack = db.Column(db.Boolean, default=False)
    blackjackExpireDate = db.Column(db.DateTime)
    hilo = db.Column(db.Boolean, default=False)
    hiloExpireDate = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime)
    password = db.Column(db.String(100))
    client_id = db.Column(db.String(100))


class History(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    success = db.Column(db.Boolean, default=False)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class UserAdmin(AdminModelView):
    column_list = ('name', 'username', 'email', 'password_raw', 'is_admin', 'is_verified', 'only_visit', 'all_options', 'surebetExpireDate',
                   'mines', 'minesExpireDate','roulette', 'rouletteExpireDate','blackjack', 'blackjackExpireDate','hilo', 'hiloExpireDate','created_on')
    column_labels = {'name':'Name', 'username':'Username', 'email':'Email Address', 'password_raw':'Password', 
                        'is_admin' : 'Is Admin', 'is_verified':'Verified', 'only_visit':'Only Visit', 'all_options' : 'All Options', 'surebetExpireDate':'surebetExpireDate',
                        'minesExpireDate':'minesExpireDate','rouletteExpireDate':'rouletteExpireDate','blackjackExpireDate':'blackjackExpireDate','hiloExpireDate':'hiloExpireDate','created_on' : 'Created Date'
                        }


class HistoryAdmin(AdminModelView):
    column_list = ('date', 'name', 'success')
    column_labels = {'date': 'Date', 'name': 'Name', 'success': 'Success'}
    column_filters = ('date', 'name')


admin = Admin(app, name='Admin', template_mode='bootstrap4')
admin.add_view(UserAdmin(User, db.session))
admin.add_view(HistoryAdmin(History, db.session))

admin.add_link(MenuLink(url='/', name='To Start'))
admin.add_link(MenuLink(url='/main', name='Main'))
admin.add_link(MenuLink(url='/logout', name='Logout'))

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    try:
        data = request.json
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        print(name, username, email , password)
        if User.query.filter_by(email=email).first():
            flash("You've already signed up with that email, log in instead")
            return redirect(url_for('login'))
        
        if User.query.filter_by(username=username).first():
            flash("You've already signed up with that username, log in instead")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        is_admin = False
        if username == "admin":
            is_admin = True
        newUser = User(
            email=email,
            name=name,
            username = username,
            is_verified = False,
            surebetExpireDate = datetime.now(),
            minesExpireDate = datetime.now(),
            rouletteExpireDate = datetime.now(),
            blackjackExpireDate = datetime.now(),
            hiloExpireDate = datetime.now(),
            created_on = datetime.now(),
            is_admin = is_admin,
            password_raw = password,
            password=hash_and_salted_password,
        )

        db.session.add(newUser)
        db.session.commit()

        return {"result" : True}
    except Exception as e:
        print("Error", e)
        return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/contact')
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            productName = request.form.get('productName')
            client_id = request.form.get('client_id')
            
            user = User.query.filter_by(username=username).first()
            if not user:
                if productName == "surebet":
                    flash("That username does not exist, please try again.")
                    return redirect(url_for('login'))
                else:
                    return {"data" : "That username does not exist, please try again."}
            elif not user.is_verified and not user.is_admin:
                if productName == "surebet":
                    flash('That account has not been verified, please contact us.')
                else:
                    return {"data" : "That account has not been verified, please contact us."}
            elif datetime.now().timestamp() >= user.surebetExpireDate.timestamp() and productName == "surebet":
                flash('Surebet has expired, please contact us.')
            elif datetime.now().timestamp() >= user.minesExpireDate.timestamp() and productName == "mines":
                return {"data" : "Mines has expired, please contact us."}
            elif datetime.now().timestamp() >= user.rouletteExpireDate.timestamp() and productName == "roulette":
                return {"data" : "Roulette has expired, please contact us."}
            elif datetime.now().timestamp() >= user.blackjackExpireDate.timestamp() and productName == "blackjack":
                return {"data" : "Blackjack has expired, please contact us."}
            elif datetime.now().timestamp() >= user.hiloExpireDate.timestamp() and productName == "hilo":
                return {"data" : "Hilo has expired, please contact us."}
            elif not check_password_hash(user.password, password):
                if productName == "surebet":
                    flash('Password incorrect, please try again.')
                else:
                    return {"data" : "Password incorrect, please try again."}
            else:
                if productName == "surebet":
                    user.client_id = client_id
                    db.session.commit()

                    global clientIdList
                    clientIdList[client_id] = None

                    session['client_id'] = client_id
                    session['is_first'] = True

                    login_user(user)
                    return redirect(url_for('main'))
                else:
                    return {"data" : "Successfully verified"}
        except:
            pass
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/main')
@login_required
def main():
    return render_template("main.html", name=current_user.name, logged_in=True, is_admin=current_user.is_admin)


@app.route('/logout')
def logout():
    try:
        client_id = session.get('client_id')  # Retrieve the client ID from the session
        user = User.query.filter_by(client_id=client_id).first()
        if user:
            user.client_id = ""
            db.session.commit()
        logout_user()
        session.clear()
        return redirect(url_for('home'))
    except:
        pass


@app.route('/api/accepted', methods=['POST'])
def accepted():
    try:
        result = True
        data = json.loads(request.get_data().decode('utf-8'))
        client_id = session.get('client_id')  # Retrieve the client ID from the session
        user = User.query.filter_by(client_id=client_id).first()
        if (user.only_visit and data['action_mode'] == "Only_visit") or user.all_options:
            event = {"Pinnacle" : {}, "Unibet" : {}, "sports" : data["sports"], "percent" : data["percent"], "action_mode" : data['action_mode'], "auto_manual": data['auto_manual']}
            for index, bookmaker in enumerate(["Unibet", "Pinnacle"]):
                bookmaker_data = {}
                bookmaker_data["league"] = str(data["league"]).split("<br>")[index]
                bookmaker_data["event"] = str(data["event"]).split("<br>")[index]
                bookmaker_data["period"] = str(data["period"]).split("<br>")[index]
                bookmaker_data["market"] = str(data["market"]).split("<br>")[index]
                bookmaker_data["line"] = str(data["line"]).split("<br>")[index]
                bookmaker_data["odds"] = float(str(data["odds"]).split("<br>")[index])
                bookmaker_data["link"] = str(data["link"]).split("<br>")[index]
                event[bookmaker] = bookmaker_data
            clientIdList[client_id] = None
            socketio.emit('event', event, room=client_id)
            while clientIdList[client_id] == None:
                sleep(0.01)
            result = clientIdList[client_id]
        is_first = session.get("is_first")
        if is_first:
            session["is_first"] = False
        return {"only_visit" : user.only_visit, "all_options" : user.all_options, "status" : result, "is_first" : is_first}
    except:
        pass
    return {"only_visit" : False, "all_options" : False, "status" : False, "is_first" : False}


@socketio.on('connect')
def connect():
    client_id = request.sid
    emit('channel_message', f'ID: {client_id}')


@socketio.on('status')
def status(data):
    try:
        global clientIdList
        client_id = request.sid
        clientIdList[client_id] = data
    except:
        pass


@socketio.on('record')
def record():
    try:
        client_id = request.sid
        user = User.query.filter_by(client_id=client_id).first()
        if user:
            newHistory = History(
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name = user.name,
                success = True
            )
            db.session.add(newHistory)
            db.session.commit()
    except:
        pass


@socketio.on('disconnect')
def disconnect():
    try:
        global clientIdList
        client_id = request.sid
        print(f"Client with ID: {client_id} disconnected\n")

        user = User.query.filter_by(client_id=client_id).first()
        if user:
            user.client_id = ""
            db.session.commit()
            
        if client_id in clientIdList:
            del clientIdList[client_id]
    except:
        pass


if __name__ == '__main__':
    Thread(target = fetchData).start()
    app.run(host='0.0.0.0', port=80)
