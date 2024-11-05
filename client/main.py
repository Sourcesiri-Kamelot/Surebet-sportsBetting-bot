import socketio
import keyboard
from time import sleep
from datetime import datetime
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.service import Service as ChromeService 

MAX_AMOUNT_PROFIT_1_3 = 10000
MAX_AMOUNT_PROFIT_3_6 = 10000
MAX_AMOUNT_PROFIT_OVER_6 = 10000

MAX_AMOUNT_ODDS_OVER_4DOT0 = 10000
MAX_AMOUNT_ODDS_2DOT0_4DOT0 = 10000
MAX_AMOUNT_ODDS_UNDER_2DOT0 = 10000

MIN_AMOUNT_BETPLAY = 500
MIN_AMOUNT_PINNACLE = {"USD" : 0.5, "EUR" : 0.5, "COP" : 500}

MAX_PROFIT = 100.0
MIN_PROFIT = 1.0

EXCHANGE_RATE = {"USD" : 4500, "EUR" : 4905, "COP" : 1}

finalOddsBetplay = -1.0
finalOddsPinnacle = -1.0
finalBetAmountBetplay = -1.0
finalBetAmountPinnacle = -1.0
oddsBetplay = -1.0
oddsPinnacle = -1.0
hasOddsBetplay = False
hasOddsPinnacle = False
readableOddsBetplay = False
readableOddsPinnacle = False
betLineElementBetplay = None
betLineElementPinnacle = None

bankrollBetplay = 0
bankrollPinnacle = 0.0
betAmountPinnacle = -1.0

allowedToBetPinnacle = False
clickedPlaceButton = False

playing = False
pressedKey = False

service = ChromeService(ChromeDriverManager().install())
optionBetplay = Options()
optionBetplay.add_experimental_option("debuggerAddress", "127.0.0.1:9015")
optionBetplay.add_argument("user-agent=Chrome/121.0.6167.185")
driverBetplay = webdriver.Chrome(service=service, options=optionBetplay)

optionPinnacle = Options()
optionPinnacle.add_experimental_option("debuggerAddress", "127.0.0.1:9020")
optionPinnacle.add_argument("user-agent=Chrome/121.0.6167.185")
driverPinnacle = webdriver.Chrome(service=service, options=optionPinnacle)

sio = socketio.Client()


def betplay(driver, event):
    print("\n")
    global playing
    global pressedKey
    global allowedToBetPinnacle
    global clickedPlaceButton
    global betAmountPinnacle    
    global bankrollBetplay
    global finalOddsBetplay
    global finalBetAmountBetplay
    global oddsBetplay
    global oddsPinnacle
    global hasOddsBetplay
    global hasOddsPinnacle
    global readableOddsBetplay
    global readableOddsPinnacle

    playing = True
    pressedKey = False
    allowedToBetPinnacle = False
    clickedPlaceButton = False
    betAmountPinnacle = -1.0
    finalBetAmountBetplay = -1.0
    hasOddsBetplay = False
    hasOddsPinnacle = False

    start_time = datetime.now()

    link = event["Unibet"]["link"]
    period = event["Unibet"]["period"]
    market = event["Unibet"]["market"]
    line = event["Unibet"]["line"]
    action_mode = event["action_mode"]
    auto_manual = event["auto_manual"]

    try:
        username = driver.find_element(By.ID, 'userName')
        signin = findElement(driver, By.ID, 'btnLoginPrimary')
        clickButton(driver, signin, "", 0, "betplay")
        sleep(2.0)
        driver.get("https://betplay.com.co/apuestas#in-play")
        sleep(2.0)
    except:
        pass
    
    thread = Thread(target=pinnacle, args=(driverPinnacle, event, ))
    if not pressedKey:
        thread.start()
        driver.get(link)
        sleep(1.0)

    if action_mode == "Full_using":
        periodExist = False
        while not pressedKey:
            if driver.current_url != link:
                break
            menuBars = findElements(driver, By.CLASS_NAME, 'KambiBC-filter-menu')
            for menuBar in menuBars:
                try:
                    periodElements = menuBar.find_elements(By.TAG_NAME, 'li')
                    for periodElement in periodElements:
                        try:
                            if periodElement.text == period:
                                periodExist = True
                                clickButton(driver, periodElement, "", 0, "betplay")
                                sleep(0.5)
                                break
                        except:
                            pass
                    if periodExist:
                        break
                except:
                    pass
            if periodExist:
                break
            sleep(0.1)

        if periodExist:        
            print(f' {datetime.now().strftime("%H:%M:%S")} betplay , o [{period}] period\n') 
            marketExist = False
            marketElements = findElements(driver, By.CLASS_NAME, 'KambiBC-bet-offer-subcategory__container')
            for marketElement in marketElements:
                marketTitle = marketElement.find_element(By.TAG_NAME, 'h3').text
                if market in marketTitle:
                    print(f' {datetime.now().strftime("%H:%M:%S")} betplay , o [{market}] market\n')
                    marketExist = True

                    lineElements = marketElement.find_elements(By.TAG_NAME, 'button')
                    for lineElement in lineElements:
                        try:
                            if "Mostrar la lista" in lineElement.text:
                                clickButton(driver, lineElement, "", 0, "betplay")
                                sleep(0.2)
                                break
                        except:
                            pass

                    readableOddsBetplay = True
                    oddsThread = Thread(target=readOddsBetplay, args=(market, line, ))
                    oddsThread.start()

                    bankroll = bankrollBetplay
                    try:
                        bankrollButton = driver.find_element(By.ID, 'navbarDropdown2')
                        clickButton(driver, bankrollButton, "", 1, "betplay")
                        try:                          
                            bankroll = int(findElement(driver, By.TAG_NAME, 'table').find_element(By.TAG_NAME, 'tr').find_elements(By.TAG_NAME, 'td')[2].text.replace(',', '').split('.')[0])
                        except:
                            pass
                        clickButton(driver, bankrollButton, "", 1, "betplay")   
                    except:
                        pass
                    bankrollBetplay = bankroll

                    while not ((hasOddsBetplay and hasOddsPinnacle) or pressedKey):
                        sleep(0.1)

                    betAmountPinnacleTemp = 0.0
                    clickedLineElement = False
                    timeout = 0.0
                    while not pressedKey:
                        allowedToBet = False
                        if oddsBetplay > 1.0 and oddsPinnacle > 1.0:
                            L = 1 / oddsBetplay + 1 / oddsPinnacle
                            netProfit = round((1 - L) * 100, 2)
                            allowedToBet = netProfit >= MIN_PROFIT and netProfit <= MAX_PROFIT and bankrollBetplay >= MIN_AMOUNT_BETPLAY and bankrollPinnacle >= MIN_AMOUNT_PINNACLE[CURRENCY_CODE]
                            resultSign = 'x'
                            if allowedToBet:
                                resultSign = 'o'
                            if oddsBetplay == 1.01:
                                oddsBetplay = "-"
                                netProfit = "-"
                            if oddsPinnacle == 1.01:
                                oddsPinnacle = "-"
                                netProfit = "-"
                            print(f' {datetime.now().strftime("%H:%M:%S")}, {resultSign} {netProfit}% odds@ ({oddsBetplay}, {oddsPinnacle}), bank@ (COP {bankrollBetplay}, {CURRENCY_CODE} {bankrollPinnacle})\n')
                        else:
                            sleep(0.1)
                            continue
                        
                        if allowedToBet:
                            if not clickedLineElement:
                                clickButton(driver, betLineElementBetplay, "line", 1, "betplay")
                                clickedLineElement = True

                                # maxBetAmount = MAX_AMOUNT_PROFIT_OVER_6
                                # if netProfit > 1.0 and netProfit < 3.0:
                                #     maxBetAmount = MAX_AMOUNT_PROFIT_1_3
                                # elif netProfit >= 3.0 and netProfit < 6.0:
                                #     maxBetAmount = MAX_AMOUNT_PROFIT_3_6
                                # else:
                                #     pass

                                if oddsBetplay > 4.0: 
                                    maxBetAmount = MAX_AMOUNT_ODDS_OVER_4DOT0
                                else:                 
                                    maxBetAmount = MAX_AMOUNT_ODDS_2DOT0_4DOT0
                                    if oddsBetplay <= 2.0:  
                                        maxBetAmount = MAX_AMOUNT_ODDS_UNDER_2DOT0
                                
                                if maxBetAmount > bankroll:
                                    maxBetAmount = bankroll

                                betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * maxBetAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                if betAmountPinnacleTemp > bankrollPinnacle:
                                    maxBetAmount = int(maxBetAmount * bankrollPinnacle / betAmountPinnacleTemp)
                                    betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * maxBetAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)

                                stake = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-stake-input')
                                inputBetAmountToStake("betplay ", stake, maxBetAmount)
                                finalBetAmountBetplay = maxBetAmount
                            else:
                                try:
                                    button_place = driver.find_element(By.CLASS_NAME, 'mod-KambiBC-betslip__place-bet-btn')
                                    clickButton(driver, button_place, "place", 0, "betplay")
                                    finalOddsBetplay = oddsBetplay
                                    clickedPlaceButton = True
                                    timeout += 0.1
                                except:
                                    pass
                                if timeout >= 5.0:
                                    cancelButtons = findElements(driver, By.CLASS_NAME, "mod-KambiBC-betslip-outcome__close-btn")
                                    for cancelButton in cancelButtons:
                                        clickButton(driver, cancelButton, "cancel(timeout)", 0, "betplay")
                                    allowedToBetPinnacle = False
                                    betAmountPinnacle = 0.0
                                    break
                                try:
                                    betAmount = int(driver.find_element(By.CLASS_NAME, "mod-KambiBC-betslip-feedback__currency").text.replace("$", "").replace(",", "").split(".")[0])
                                    if betAmount > bankroll:
                                        betAmount = bankroll                   
                                    betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * betAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                    if betAmountPinnacleTemp > bankrollPinnacle:
                                        betAmount  = int(betAmount * bankrollPinnacle / betAmountPinnacleTemp)
                                        betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * betAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                    timeout = 0.0
                                    buttons = driver.find_elements(By.CLASS_NAME, 'mod-KambiBC-betslip-button')
                                    for button in buttons:
                                        if button.text == "Atrás":
                                            clickButton(driver, button, "back", 0, "betplay")
                                            break
                                    stake = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-stake-input')
                                    inputBetAmountToStake("betplay ", stake, betAmount)
                                    finalBetAmountBetplay = betAmount
                                except:
                                    pass
                                try:
                                    message = driver.find_element(By.CLASS_NAME, 'mod-KambiBC-betslip-feedback__title').text
                                    timeout = 0.0
                                    if "No hay dinero suficiente" in message:
                                        button_back = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-betslip-button')
                                        clickButton(driver, button_back, "back", 0, "betplay")
                                        stake = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-stake-input')
                                        inputBetAmountToStake("betplay ", stake, "999999999999")
                                    if "Error al realizar apuesta" in message:
                                        button_back = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-betslip-button')
                                        clickButton(driver, button_back, "back", 0, "betplay")
                                except:
                                    pass
                                try:
                                    button_close = driver.find_element(By.CLASS_NAME, 'mod-KambiBC-betslip-receipt__close-button')
                                    if not allowedToBetPinnacle:
                                        allowedToBetPinnacle = True
                                        betAmountPinnacle = betAmountPinnacleTemp
                                    clickButton(driver, button_close, "close", 0, "betplay")
                                    break
                                except:
                                    pass
                                try:
                                    message = driver.find_element(By.CLASS_NAME, 'mod-KambiBC-betslip-pba__description').text
                                    betAmount = int(str(message).removesuffix('.').replace("\n", " ").split("$")[-1].replace(",", "").split(".")[0])
                                    if betAmount > bankroll:
                                        betAmount = bankroll
                                    betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * betAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                    if betAmountPinnacleTemp > bankrollPinnacle:
                                        betAmount = int(betAmount * bankrollPinnacle / betAmountPinnacleTemp)
                                        betAmountPinnacleTemp = round(oddsBetplay / oddsPinnacle * betAmount / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                    timeout = 0.0
                                    buttons = driver.find_elements(By.CLASS_NAME, 'mod-KambiBC-betslip-button')
                                    for button in buttons:
                                        if button.text == "Atrás":
                                            clickButton(driver, button, "back", 0, "betplay")
                                            break
                                    stake = findElement(driver, By.CLASS_NAME, 'mod-KambiBC-stake-input')
                                    inputBetAmountToStake("betplay ", stake, betAmount)
                                    finalBetAmountBetplay = betAmount
                                except:
                                    pass
                                sleep(0.1)
                        else:
                            if not allowedToBetPinnacle:
                                betAmountPinnacle = 0.0
                                break
                        sleep(0.1)

                    readableOddsBetplay = False
                    while oddsThread.is_alive():
                        sleep(0.1)
                    break
            if not marketExist:
                print(f' {datetime.now().strftime("%H:%M:%S")} betplay , x [{market}] market\n') 
                allowedToBetPinnacle = False
                betAmountPinnacle = 0.0
        else:
            print(f' {datetime.now().strftime("%H:%M:%S")} betplay , x [{period}] period\n')
            allowedToBetPinnacle = False
            betAmountPinnacle = 0.0
    
    clickedPlaceButton = False
    
    while True:
        try:
            header = driver.find_element(By.CLASS_NAME, "mod-KambiBC-betslip__header")
            if header.text == "Sencillas" or header.text == "":
                break
            try:
                driver.find_element(By.CLASS_NAME, "mod-KambiBC-betslip-outcome__close-btn").click()
            except:
                pass
            buttons = driver.find_elements(By.CLASS_NAME, 'mod-KambiBC-betslip-button')
            for button in buttons:
                if button.text == "Atrás":
                    clickButton(driver, button, "back", 0, "betplay")
                    break
            try:
                header.click()
            except:
                pass
        except:
            pass
        sleep(0.1)
    
    while thread.is_alive():
        readableOddsPinnacle = False
        sleep(0.1)
        
    print(f' {datetime.now().strftime("%H:%M:%S")} {(datetime.now() - start_time).seconds}s\n')
    
    if auto_manual == "Auto":
        print(f' {datetime.now().strftime("%H:%M:%S")} Sleeping for 3s in Auto Mode\n')
        sleep(3.0)
    pressedKey = False
    playing = False 


def pinnacle(driver, event):
    global finalBetAmountPinnacle
    global finalOddsPinnacle
    global oddsPinnacle
    global hasOddsPinnacle
    global bankrollPinnacle
    global readableOddsPinnacle
    global allowedToBetPinnacle
    global betAmountPinnacle

    link = event["Pinnacle"]["link"].replace("www.pinnacle.com", DOMAIN)
    period = event["Pinnacle"]["period"]
    market = event["Pinnacle"]["market"]
    line = event["Pinnacle"]["line"]
    action_mode = event["action_mode"]

    driver = driverPinnacle
    try:
        username = driver.find_element(By.ID, 'username')
        signin = findElement(driver, By.CSS_SELECTOR, 'div[data-test-id="header-login-loginButton"]').find_element(By.TAG_NAME, 'button')
        clickButton(driver, signin, "", 0, "pinnacle")
        findElement(driver, By.CSS_SELECTOR, 'span[data-test-id="QuickCashier-BankRoll"]')
        sleep(2.0)
    except:
        pass

    if not pressedKey:
        # driver.get(f"https://{DOMAIN}/en/tennis/matchups/live/")
        # sleep(1.0)
        driver.get(link)
        sleep(0.5)

    if action_mode == "Full_using":
        bankroll = bankrollPinnacle
        while not pressedKey:
            try:
                text = findElement(driver, By.CSS_SELECTOR, 'span[data-test-id="QuickCashier-BankRoll"]').text.replace("USD", "").replace("COP", "").replace("EUR", "").replace(" ", "")
                
                temp = ""
                if "." in text and "," in text:
                    is_ok = True
                    for i in text[::-1]:
                        if (i == "." or i == ","):
                            if is_ok:
                                is_ok = False
                                temp = "." + temp
                        else:
                            temp = i + temp
                elif "." in text and "," not in text:
                    if len(text.split(".")) == 2:
                        temp = text
                    else:
                        temp = text.replace(".", "")
                elif "." not in text and "," in text:
                    if len(text.split(",")) == 2:
                        temp = text.replace(",", "")
                    else:
                        temp = text.replace(",", "")
                else:
                    temp = text

                bankroll = float(temp)
                break
            except:
                pass
            sleep(0.1)
        bankrollPinnacle = bankroll
    
        if driver.current_url == link:
            print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, o [{period}] period\n') 

            marketExist = False
            marketElements = []
            timeout = 0.0
            while not pressedKey and timeout < 5.0:
                marketElements = findElements(driver, By.CSS_SELECTOR, 'div[data-test-id="Collapse"]')
                if len(marketElements) >= 2:
                    break
                timeout += 0.1
                sleep(0.1)

            for marketElement in marketElements:
                marketTitle = marketElement.find_element(By.TAG_NAME, 'span').text
                if market in marketTitle:
                    print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, o [{market}] market\n') 
                    marketExist = True
                    buttons = marketElement.find_elements(By.TAG_NAME, 'button')
                    for button in buttons:
                        try:
                            if "See more" in button.text or "More information" in button.text:
                                clickButton(driver, button, "", 1, "pinnacle")
                                sleep(0.2)
                                break
                        except:
                            pass
                    
                    divider, buttonIndex, teamName = 1, 0, ""
                    if "Handicap" in market:
                        divider, buttonIndex = 2, 0
                        splits = line.split(" ")
                        line = splits[-1].replace(" ", "")
                        teamName = " ".join(splits[:-1]).split(" (")[0]
                        # teamName = " ".join(splits[:-1]).replace(" (W)", "").replace(" (F)", "")
                        subHeading = marketElement.find_element(By.CLASS_NAME, 'style_subHeading__mbxPy').text.replace(" (Games)", "").replace(" (Sets)", "")
                        if subHeading.find(teamName) > 0:
                            divider, buttonIndex = 2, 1
                    if 'Team Total' in market:
                        divider, buttonIndex = 2, 0
                        splits = line.split("(")
                        line = splits[0]
                        teamName = splits[1].replace(")", "").split(" (")[0]
                        # teamName = splits[1].replace(")", "").replace(" (W)", "").replace(" (F)", "")
                        subHeading = marketElement.find_element(By.CLASS_NAME, 'style_subHeading__mbxPy').text.replace(" (Games)", "").replace(" (Sets)", "")
                        if subHeading.find(teamName) > 0:
                            divider, buttonIndex = 2, 1

                    readableOddsPinnacle = True
                    oddsThread = Thread(target=readOddsPinnacle, args=(market, line, buttonIndex, divider, teamName, ))
                    oddsThread.start()
                    
                    while not pressedKey:
                        if allowedToBetPinnacle and betAmountPinnacle != 0.0:
                            L = 1 / finalOddsBetplay + 1 / oddsPinnacle
                            netProfit = round((1 - L) * 100, 2)
                            if netProfit >= MIN_PROFIT and netProfit <= MAX_PROFIT:
                                allowedToBetPinnacle = False
                                betAmountPinnacle = round(finalOddsBetplay / oddsPinnacle * finalBetAmountBetplay / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                if betAmountPinnacle <= bankrollPinnacle:
                                    findElement(driver, By.CSS_SELECTOR, 'a[data-test-id="Betslip-StakeWinInput-MaxWagerLimit"]')
                                    stake = findElement(driver, By.CSS_SELECTOR, 'input[aria-label="Currency Input"]')
                                    inputBetAmountToStake("pinnacle", stake, betAmountPinnacle)
                                    bet_button = findElement(driver, By.CSS_SELECTOR, 'button[data-test-id="Betslip-ConfirmBetButton"]')
                                    clickButton(driver, bet_button, "place", 1, "pinnacle")
                                    finalOddsPinnacle = oddsPinnacle
                                    finalBetAmountPinnacle = betAmountPinnacle
                                else:
                                    print(f' ~ ~ ~ Warning! Not enough money({CURRENCY_CODE} {betAmountPinnacle}) to bet, you need to decide what to do ~ ~ ~\n')
                                    break
                            else:
                                print(f' ~ ~ ~ Warning! Not available profit({netProfit}%), you need to decide what to do ~ ~ ~\n')
                                break
                            sleep(1.0)
                            timeout = 0.0
                            while not pressedKey:
                                try:
                                    min_amount = float(driver.find_element(By.CSS_SELECTOR, 'div[data-test-id="BetSlip-CardMessage-Body"]').text.split(" ")[-1].removesuffix(".").replace(",", ""))
                                    stake = findElement(driver, By.CSS_SELECTOR, 'input[aria-label="Currency Input"]')
                                    inputBetAmountToStake("pinnacle", stake, min_amount)
                                    print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, Min amount: {min_amount}{CURRENCY_CODE}\n') 
                                except:
                                    pass
                                try:
                                    bet_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test-id="Betslip-ConfirmBetButton"]')
                                    L = 1 / finalOddsBetplay + 1 / oddsPinnacle
                                    netProfit = round((1 - L) * 100, 2)
                                    if netProfit >= MIN_PROFIT and netProfit <= MAX_PROFIT:
                                        betAmountPinnacle = round(finalOddsBetplay / oddsPinnacle * finalBetAmountBetplay / EXCHANGE_RATE[CURRENCY_CODE], 2)
                                        if betAmountPinnacle <= bankrollPinnacle:
                                            findElement(driver, By.CSS_SELECTOR, 'a[data-test-id="Betslip-StakeWinInput-MaxWagerLimit"]')
                                            stake = findElement(driver, By.CSS_SELECTOR, 'input[aria-label="Currency Input"]')
                                            inputBetAmountToStake("pinnacle", stake, betAmountPinnacle)
                                            clickButton(driver, bet_button, "confirm", 1, "pinnacle")
                                            finalOddsPinnacle = oddsPinnacle
                                            finalBetAmountPinnacle = betAmountPinnacle
                                        else:
                                            print(f' ~ ~ ~ Warning! Not enough money({CURRENCY_CODE} {betAmountPinnacle}) to bet, you need to decide what to do ~ ~ ~\n')
                                            break
                                    else:
                                        print(f' ~ ~ ~ Warning! Not available profit({netProfit}%), you need to decide what to do ~ ~ ~\n')
                                        break
                                except:
                                    pass
                                try:
                                    message = driver.find_element(By.CSS_SELECTOR, 'div[data-test-id="Betslip-CardMessage"]').text                                
                                    if "Bet Accepted" in message:
                                        sio.emit("record")
                                        break
                                    elif "Odds Unavailable" in message:
                                        print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, The odds are no longer available for betting.\n') 
                                        break
                                    else:
                                        pass
                                except:
                                    pass
                                try:
                                    driver.find_element(By.ID, "betslip-empty").text
                                    sio.emit("record")
                                    break
                                except:
                                    pass
                                sleep(0.1)
                            break
                        if not allowedToBetPinnacle and betAmountPinnacle == 0.0:
                            break
                        sleep(0.1)

                    readableOddsPinnacle = False
                    while oddsThread.is_alive():
                        sleep(0.1)
                    break
            if not marketExist:
                oddsPinnacle = 1.01
                hasOddsPinnacle = True
                print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, x [{market}] market\n') 
        else:
            print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, x [{period}] period\n') 
            oddsPinnacle = 1.01
            hasOddsPinnacle = True
        
    while True:
        try:
            driver.find_element(By.ID, "betslip-empty").text
            break
        except:
            pass
        try:
            closeButton = driver.find_element(By.CLASS_NAME, 'betslip-close-button')
            closeButton.click()
        except:
            pass
        sleep(0.1)
        
    # sleep(1.0)
    # driver.get(f"https://{DOMAIN}/en/tennis/matchups/live/")
        

def readOddsBetplay(market, line):
    global oddsBetplay
    global hasOddsBetplay
    global betLineElementBetplay
    global readableOddsBetplay

    hasOddsBetplay = False
    betLineElementBetplay = None
    beforeValue = 0.0
    count = 0
    limitCount = 5

    while readableOddsBetplay and not pressedKey:
        updatedOdd = 1.0
        marketElements = []
        lineElements = []
        
        marketElements = findElements(driverBetplay, By.CLASS_NAME, 'KambiBC-bet-offer-subcategory__container')
        for marketElement in marketElements:
            try:
                marketTitle = marketElement.find_element(By.TAG_NAME, 'h3').text
                if market in marketTitle:    
                    lineElements = marketElement.find_elements(By.TAG_NAME, 'button')
                    break
            except:
                pass
            
        lineElementExist = False
        for lineElement in lineElements:
            try:
                text = lineElement.text
                line_text = " ".join(text.split("\n")[:-1])
                if line in line_text and (("." in line and "." in line_text) or ("." not in line and "." not in line_text)):
                    betLineElementBetplay = lineElement
                    lineElementExist = True
                    try:
                        updatedOdd = float(text.split("\n")[-1])
                    except:
                        pass
                    break
            except:
                pass
            
        if lineElementExist:
            if readableOddsBetplay:
                oddsBetplay = updatedOdd
                if updatedOdd != beforeValue or updatedOdd == 1.0:
                    beforeValue = updatedOdd
                    if updatedOdd == 1.0:
                        if count < limitCount:
                            count += 1
                        else:
                            hasOddsBetplay = True
                            print(f' {datetime.now().strftime("%H:%M:%S")} betplay , x [{line}] line Suspended\n')
                    else:
                        print(f' {datetime.now().strftime("%H:%M:%S")} betplay , o [{line}] line @{updatedOdd}\n') 
                        count = 0
                if not hasOddsBetplay and updatedOdd != 1.0:
                    hasOddsBetplay = True
        else:
            oddsBetplay = 1.01
            hasOddsBetplay = True
            readableOddsBetplay = False
            print(f' {datetime.now().strftime("%H:%M:%S")} betplay , x [{line}] line\n')
        sleep(0.1)


def readOddsPinnacle(market, line, buttonIndex, divider, teamName):
    global oddsPinnacle
    global hasOddsPinnacle
    global readableOddsPinnacle

    hasOddsPinnacle = False
    beforeValue = 0.0
    count = 0
    limitCount = 100
    clickedLineElement = False

    while readableOddsPinnacle and not pressedKey:
        updatedOdd = 1.0
        marketElements = []
        lineElements = []
        
        timeout = 0.0
        while not pressedKey and timeout < 5.0:
            marketElements = findElements(driverPinnacle, By.CSS_SELECTOR, 'div[data-test-id="Collapse"]')
            if len(marketElements) >= 2:
                break
            timeout += 0.1
            sleep(0.1)

        for marketElement in marketElements:
            try:
                marketTitle = marketElement.find_element(By.TAG_NAME, 'span').text
                if market in marketTitle:
                    lineElements = marketElement.find_elements(By.TAG_NAME, 'button')
                    break
            except:
                pass
        
        lineElementExist = False
        for index, lineElement in enumerate(lineElements):
            try:
                text = lineElement.text
                line_text = " ".join(text.split("\n")[:-1])
                if index % divider == buttonIndex and line in line_text and (("." in line and "." in line_text) or ("." not in line and "." not in line_text)):
                    lineElementExist = True
                    try:
                        updatedOdd = float(text.split("\n")[-1])
                        if not clickedLineElement:
                            clickedLineElement = True
                            clickButton(driverPinnacle, lineElement, "line", 1, "pinnacle")
                    except:
                        pass
                    break
            except:
                pass
        if lineElementExist:
            if readableOddsPinnacle:
                oddsPinnacle = updatedOdd
                if updatedOdd != beforeValue or updatedOdd == 1.0:
                    beforeValue = updatedOdd
                    if updatedOdd == 1.0:
                        if count < limitCount:
                            count += 1
                        else:
                            hasOddsPinnacle = True
                            if not (allowedToBetPinnacle or clickedPlaceButton):
                                oddsPinnacle = 1.01
                                readableOddsPinnacle = False
                            print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, x [{teamName} {line}] line Suspended\n')
                    else:
                        print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, o [{teamName} {line}] line @{updatedOdd}\n') 
                        count = 0
                if not hasOddsPinnacle and updatedOdd != 1.0:
                    hasOddsPinnacle = True
        else:
            oddsPinnacle = 1.01
            hasOddsPinnacle = True
            readableOddsPinnacle = False
            print(f' {datetime.now().strftime("%H:%M:%S")} pinnacle, x [{teamName} {line}] line\n')
        sleep(0.1)
                                

def inputBetAmountToStake(bookmakerName, stake, amount):
    try:
        stake.send_keys(Keys.CONTROL + "a")  # Select all text
        stake.send_keys(Keys.BACKSPACE)      # Delete the selected text
        stake.send_keys(str(amount))
        print(f' {datetime.now().strftime("%H:%M:%S")} {bookmakerName}, stake input: {amount}\n')
    except:
        pass


def findElement(driver, by, value):
    element = None
    while not (pressedKey or element):
        try:
            element = driver.find_element(by, value)
        except:
            pass
        sleep(0.1)
    return element


def findElements(driver, by, value):
    elements = []
    while not (pressedKey or elements):
        try:
            elements = driver.find_elements(by, value)
        except:
            pass
        sleep(0.1)
    return elements


def clickButton(driver, button, buttonName, mode, bookmaker):
    if mode == 0:
        try:
            button.click()
        except:
            driver.execute_script("arguments[0].click();", button)
    else:
        driver.execute_script("arguments[0].click();", button)
    if buttonName:
        print(f' {datetime.now().strftime("%H:%M:%S")} {bookmaker.ljust(8)}, button clicked <{buttonName}>\n')


def loginUser():  
    print("-" * 70, "\n")
    print(" Connecting to Betplay... ", "\n")
    try:
        username = driverBetplay.find_element(By.ID, 'userName')
        signin = driverBetplay.find_element(By.ID, 'btnLoginPrimary')
        clickButton(driverBetplay, signin, "", 0, "betplay")
        sleep(5.0)
        driverBetplay.get("https://betplay.com.co/apuestas#home")
        sleep(5.0)
        driverBetplay.get("https://betplay.com.co/apuestas#event/live/1020494864")
        sleep(2.0)
    except:
        pass
    if "https://betplay.com.co/apuestas#event/live/" not in driverBetplay.current_url:
        driverBetplay.get("https://betplay.com.co/apuestas#event/live/1020494864")

    print(" Connecting to Pinnacle...", "\n")
    
    domainName = 'www.pinnacle.com'
    if "www.pin1111.com" in driverPinnacle.current_url:
        domainName = "www.pin1111.com"
        
    try:
        username = driverPinnacle.find_element(By.ID, 'username')
        signin = driverPinnacle.find_element(By.CSS_SELECTOR, 'div[data-test-id="header-login-loginButton"]').find_element(By.TAG_NAME, 'button')
        clickButton(driverPinnacle, signin, "", 0, "pinnacle")
    except:
        pass
    
    # driverPinnacle.get(f"https://{domainName}/en/tennis/matchups/live/")
    
    currencyCode = None
    while not (pressedKey or currencyCode):
        try:
            text = findElement(driverPinnacle, By.CSS_SELECTOR, 'span[data-test-id="QuickCashier-BankRoll"]').text        
            if "USD" in text:
                currencyCode = "USD"
            if "COP" in text:
                currencyCode = "COP"
            if "EUR" in text:
                currencyCode = "EUR"
        except:
            pass
        sleep(0.1)

    return domainName, currencyCode


def pressKey():
    global pressedKey
    while True:
        if keyboard.is_pressed('esc'):
            pressedKey = True
            # print(f' {datetime.now().strftime("%H:%M:%S")} pressed ESC key\n')
        sleep(0.1)


@sio.event
def connect():
    pass


@sio.event
def channel_message(message):
    print(f' {message}\n\n{"-" * 70}\n')
    print(" It's ready for placing the bet.")


@sio.event
def event(event):
    if not playing:
        Thread(target=betplay, args=(driverBetplay, event, )).start()
    sio.emit("status", not playing)


@sio.event
def disconnect():
    print(f'Disconnected from Server\n\n{"-" * 70}\n')


if __name__ == "__main__":
    print("")
    print(" Notification! To pause/stop running the bot, press ESC key.\n")

    Thread(target=pressKey).start()
    
    DOMAIN, CURRENCY_CODE = loginUser()
    
    sio.connect('http://87.251.88.14:80')
    
    sio.wait()
    