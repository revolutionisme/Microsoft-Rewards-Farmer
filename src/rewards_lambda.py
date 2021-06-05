import time
import json
from datetime import date, timedelta, datetime
import requests
import random
import urllib.parse
import ipapi
import os
import telegram_send
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementNotVisibleException,
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)


# Define user-agents
PC_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.19 Safari/537.36 Edg/86.0.622.63"
MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0. 3945.79 Mobile Safari/537.36"

POINTS_COUNTER = 0


BIN_DIR = "/tmp/bin"
CURR_BIN_DIR = os.getcwd()


def _subprocess_log(logs):
    res_str = logs.decode("utf-8")
    for line in res_str.splitlines():
        print(line)


def _init_bin():
    start = time.clock()
    # if not os.path.exists(BIN_DIR):
    #     print("Creating bin folder")
    #     os.makedirs(BIN_DIR)

    # print("Copying binaries for " + executable_name + " in /tmp/bin")
    # currfile = os.path.join(CURR_BIN_DIR, executable_name)
    # newfile = os.path.join(BIN_DIR, executable_name)
    # shutil.copy2(executable_name, newfile)
    res = subprocess.check_output(["mkdir", "/tmp/bin"])
    res = subprocess.check_output(["cp", "bin/chromedriver", "/tmp/bin/"])
    res = subprocess.check_output(["cp", "bin/chromium", "/tmp/bin/"])

    print("Giving new binaries permissions for lambda")
    subprocess.check_output(
        [
            "chmod",
            # "-R",
            "755",
            "/tmp/bin/chromedriver",
        ]
    )

    subprocess.check_output(
        [
            "chmod",
            # "-R",
            "755",
            "/tmp/bin/chromium",
        ]
    )
    res = subprocess.check_output(["ls", "-ltra", "/tmp/bin/"])
    _subprocess_log(res)

    # os.chmod(newfile, 0o775)
    elapsed = time.clock() - start
    # print(executable_name + " ready in " + str(elapsed) + "s.")


# Define browser setup function
def browserSetup(
    headless_mode: bool = False, user_agent: str = PC_USER_AGENT
) -> WebDriver:
    # _init_bin("headless-chromium")
    _init_bin()

    # Create Chrome browser
    from selenium.webdriver.chrome.options import Options

    options = Options()

    # lambda_options = [
    #     '--headless',
    #     '--disable-gpu',
    #     '--window-size=1280x1696',
    #     '--no-sandbox',
    #     '--hide-scrollbars',
    #     '--enable-logging',
    #     '--log-level=0',
    #     '--v=99',
    #     '--single-process',
    #     '--ignore-certificate-errors',
    #     # "--autoplay-policy=user-gesture-required",
    #     # "--disable-background-networking",
    #     # "--disable-background-timer-throttling",
    #     # "--disable-backgrounding-occluded-windows",
    #     # "--disable-breakpad",
    #     # "--disable-client-side-phishing-detection",
    #     # "--disable-component-update",
    #     # "--disable-default-apps",
    #     # "--disable-dev-shm-usage",
    #     # "--disable-domain-reliability",
    #     # "--disable-extensions",
    #     # "--disable-features=AudioServiceOutOfProcess",
    #     # "--disable-hang-monitor",
    #     # "--disable-ipc-flooding-protection",
    #     # "--disable-notifications",
    #     # "--disable-offer-store-unmasked-wallet-cards",
    #     # "--disable-popup-blocking",
    #     # "--disable-print-preview",
    #     # "--disable-prompt-on-repost",
    #     # "--disable-renderer-backgrounding",
    #     # "--disable-setuid-sandbox",
    #     # "--disable-speech-api",
    #     # "--disable-sync",
    #     # "--disk-cache-size=33554432",
    #     # "--hide-scrollbars",
    #     # "--ignore-gpu-blacklist",
    #     # "--ignore-certificate-errors",
    #     # "--metrics-recording-only",
    #     # "--mute-audio",
    #     # "--no-default-browser-check",
    #     # "--no-first-run",
    #     # "--no-pings",
    #     # "--no-sandbox",
    #     # "--no-zygote",
    #     # "--password-store=basic",
    #     # "--use-gl=swiftshader",
    #     # "--use-mock-keychain",
    #     # "--single-process",
    #     # "--headless",
    #     f"user-agent={user_agent}",
    #     f"lang={LANG.split('-')[0]}",
    # ]
    # for argument in lambda_options:
    #     options.add_argument(argument)

    options.add_argument("user-agent=" + user_agent)
    options.add_argument("lang=" + LANG.split("-")[0])
    if headless_mode:
        options.add_argument("--headless")
    options.add_argument("log-level=3")

    options.binary_location = "/tmp/bin/chromium"
    chrome_browser_obj = webdriver.Chrome(
        executable_path="/tmp/bin/chromedriver", options=options
    )
    return chrome_browser_obj


# Define login function
def login(browser: WebDriver, email: str, pwd: str, isMobile: bool = False):
    # Access to bing.com
    browser.get("https://login.live.com/")
    # Wait complete loading
    waitUntilVisible(browser, By.ID, "loginHeader", 10)
    # Enter email
    print("[LOGIN]", "Writing email...")
    browser.find_element_by_name("loginfmt").send_keys(email)
    # Click next
    browser.find_element_by_id("idSIButton9").click()
    # Wait 2 seconds
    time.sleep(2)

    # Wait complete loading
    waitUntilVisible(browser, By.ID, "loginHeader", 10)
    waitUntilClickable(browser, By.ID, "idChkBx_PWD_KMSI0Pwd", 10)

    # value: WebElement = browser.find_element_by_id("idChkBx_PWD_KMSI0Pwd")
    # print(
    #     f"Keep signed in text - {value.is_selected()}, {value.is_enabled()}, {value.is_displayed()}"
    # )
    # if not value.is_selected():
    #     value.click()
    #     print(f"After click - {value.is_selected()}")

    number = browser.find_element_by_id("idRemoteNGC_DisplaySign")
    auth_number = number.text
    print(
        f"[LOGIN] Athentication code: {auth_number}, select this number on authenticator"
    )

    telegram_send.send(
        messages=[f"Athentication code: {auth_number}"], conf="telegram-send.conf"
    )
    # time.sleep(40)
    # Enter password
    # browser.find_element_by_id("i0118").send_keys(pwd)

    # browser.execute_script("document.getElementById('i0118').value = '" + pwd + "';")
    # print('[LOGIN]', 'Writing password...')
    # Click next
    # browser.find_element_by_id('idSIButton9').click()
    # Wait 5 seconds
    # time.sleep(5)
    # Click Security Check
    print("[LOGIN]", "Passing security checks...")
    try:
        browser.find_element_by_id("iLandingViewAction").click()
    except (NoSuchElementException, ElementNotInteractableException) as e:
        pass
    # Wait complete loading
    try:
        waitUntilVisible(browser, By.ID, "KmsiCheckboxField", 10)
    except (TimeoutException) as e:
        pass
    # Click next
    while True:
        try:
            browser.find_element_by_id("idSIButton9").click()
            # Wait 5 seconds
            time.sleep(5)
        except (ElementNotVisibleException,) as e1:
            print(f"[LOGIN] Waiting for 2FA Authetication, please select {auth_number}")
            telegram_send.send(
                messages=[f"Athentication code: {auth_number}"],
                conf="telegram-send.conf",
            )
            time.sleep(10)
        except (NoSuchElementException, ElementNotInteractableException) as e2:
            print(f"[LOGIN] Authntication Done")
            break

    print("[LOGIN]", "Logged-in !")
    # Check Login
    print("[LOGIN]", "Ensuring login on Bing...")
    checkBingLogin(browser, isMobile)


def checkBingLogin(browser: WebDriver, isMobile: bool = False):
    global POINTS_COUNTER
    # Access Bing.com
    browser.get("https://bing.com/")
    # Wait 8 seconds
    time.sleep(8)
    # Accept Cookies
    try:
        browser.find_element_by_id("bnp_btn_accept").click()
    except:
        pass

    if isMobile:
        try:
            # print("[LOGIN]", "First Try...")
            time.sleep(1)
            browser.find_element_by_id("mHamburger").click()
        except:
            try:
                browser.find_element_by_id("bnp_btn_accept").click()
            except:
                pass
            time.sleep(1)
            try:
                browser.find_element_by_id("mHamburger").click()
            except:
                pass

        try:
            # print("[LOGIN]", "Second Try...")
            time.sleep(1)
            browser.find_element_by_id("HBSignIn").click()
        except:
            pass

        try:
            # print("[LOGIN]", "Third Try...")
            time.sleep(2)
            browser.find_element_by_id("iShowSkip").click()
            time.sleep(3)
        except:
            if (
                str(browser.current_url).split("?")[0]
                == "https://account.live.com/proofs/Add"
            ):
                input(
                    "[LOGIN] Please complete the Security Check on "
                    + browser.current_url
                )
                exit()
    # Wait 2 seconds
    time.sleep(2)
    # Refresh page
    browser.get("https://bing.com/")
    # Wait 5 seconds
    time.sleep(10)
    # Update Counter
    try:
        if not isMobile:
            POINTS_COUNTER = int(
                browser.find_element_by_id("id_rc").get_attribute("innerHTML")
            )
        else:
            try:
                browser.find_element_by_id("mHamburger").click()
            except:
                try:
                    browser.find_element_by_id("bnp_btn_accept").click()
                except:
                    pass
                time.sleep(1)
                browser.find_element_by_id("mHamburger").click()
            time.sleep(1)
            POINTS_COUNTER = int(
                browser.find_element_by_id("fly_id_rc").get_attribute("innerHTML")
            )
    except:
        checkBingLogin(browser, isMobile)


def waitUntilVisible(
    browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10
):
    WebDriverWait(browser, time_to_wait).until(
        ec.visibility_of_element_located((by_, selector))
    )


def waitUntilClickable(
    browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10
):
    WebDriverWait(browser, time_to_wait).until(
        ec.element_to_be_clickable((by_, selector))
    )


def waitUntilQuestionRefresh(browser: WebDriver):
    tries = 0
    refreshCount = 0
    while True:
        try:
            browser.find_elements_by_class_name("rqECredits")[0]
            return True
        except:
            if tries < 10:
                tries += 1
                time.sleep(0.5)
            else:
                if refreshCount < 5:
                    browser.refresh()
                    refreshCount += 1
                    tries = 0
                    time.sleep(5)
                else:
                    return False


def waitUntilQuizLoads(browser: WebDriver):
    tries = 0
    refreshCount = 0
    while True:
        try:
            browser.find_element_by_xpath('//*[@id="rqStartQuiz"]')
            return True
        except:
            if tries < 10:
                tries += 1
                time.sleep(0.5)
            else:
                if refreshCount < 5:
                    browser.refresh()
                    refreshCount += 1
                    tries = 0
                    time.sleep(5)
                else:
                    return False


def findBetween(s: str, first: str, last: str) -> str:
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def getCCodeLangAndOffset() -> tuple:
    nfo = ipapi.location()
    lang = nfo["languages"].split(",")[0]
    geo = nfo["country"]
    if nfo["utc_offset"] == None:
        tz = str(0)
    else:
        tz = str(round(int(nfo["utc_offset"]) / 100 * 60))
    return (lang, geo, tz)


def getGoogleTrends(numberOfwords: int) -> list:
    search_terms = []
    i = 0
    while len(search_terms) < numberOfwords:
        i += 1
        r = requests.get(
            "https://trends.google.com/trends/api/dailytrends?hl="
            + LANG
            + "&ed="
            + str((date.today() - timedelta(days=i)).strftime("%Y%m%d"))
            + "&geo="
            + GEO
            + "&ns=15"
        )
        google_trends = json.loads(r.text[6:])
        for topic in google_trends["default"]["trendingSearchesDays"][0][
            "trendingSearches"
        ]:
            search_terms.append(topic["title"]["query"].lower())
            for related_topic in topic["relatedQueries"]:
                search_terms.append(related_topic["query"].lower())
        search_terms = list(set(search_terms))
    del search_terms[numberOfwords : (len(search_terms) + 1)]
    return search_terms


def getRelatedTerms(word: str) -> list:
    try:
        r = requests.get(
            "https://api.bing.com/osjson.aspx?query=" + word,
            headers={"User-agent": PC_USER_AGENT},
        )
        return r.json()[1]
    except:
        return []


def resetTabs(browser: WebDriver):
    try:
        curr = browser.current_window_handle

        for handle in browser.window_handles:
            if handle != curr:
                browser.switch_to.window(handle)
                time.sleep(0.5)
                browser.close()
                time.sleep(0.5)

        browser.switch_to.window(curr)
        time.sleep(0.5)
        browser.get("https://account.microsoft.com/rewards/")
    except:
        browser.get("https://account.microsoft.com/rewards/")


def getAnswerCode(key: str, string: str) -> str:
    t = 0
    for i in range(len(string)):
        t += ord(string[i])
    t += int(key[-2:], 16)
    return str(t)


def bingSearches(browser: WebDriver, numberOfSearches: int, isMobile: bool = False):
    global POINTS_COUNTER
    i = 0
    search_terms = getGoogleTrends(numberOfSearches)
    for word in search_terms:
        i += 1
        print("[BING]", str(i) + "/" + str(numberOfSearches))
        points = bingSearch(browser, word, isMobile)
        if points <= POINTS_COUNTER:
            relatedTerms = getRelatedTerms(word)
            for term in relatedTerms:
                points = bingSearch(browser, term, isMobile)
                if not points <= POINTS_COUNTER:
                    break
        if points > 0:
            POINTS_COUNTER = points
        else:
            break


def bingSearch(browser: WebDriver, word: str, isMobile: bool):
    browser.get("https://bing.com")
    time.sleep(2)
    searchbar = browser.find_element_by_id("sb_form_q")
    searchbar.send_keys(word)
    searchbar.submit()
    time.sleep(random.randint(10, 15))
    points = 0
    try:
        if not isMobile:
            points = int(browser.find_element_by_id("id_rc").get_attribute("innerHTML"))
        else:
            try:
                browser.find_element_by_id("mHamburger").click()
            except UnexpectedAlertPresentException:
                try:
                    browser.switch_to.alert.accept()
                    time.sleep(1)
                    browser.find_element_by_id("mHamburger").click()
                except NoAlertPresentException:
                    pass
            time.sleep(1)
            points = int(
                browser.find_element_by_id("fly_id_rc").get_attribute("innerHTML")
            )
    except:
        pass
    return points


def completePromotionalItems(browser: WebDriver):
    try:
        item = getDashboardData(browser)["promotionalItem"]
        if (
            (item["pointProgressMax"] == 100 or item["pointProgressMax"] == 200)
            and item["complete"] == False
            and item["destinationUrl"] == "https://account.microsoft.com/rewards"
        ):
            browser.find_element_by_xpath(
                '//*[@id="promo-item"]/section/div/div/div/a'
            ).click()
            time.sleep(1)
            browser.switch_to.window(window_name=browser.window_handles[1])
            time.sleep(8)
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
            time.sleep(2)
    except:
        pass


def completeDailySetSearch(browser: WebDriver, cardNumber: int):
    time.sleep(5)
    browser.find_element_by_xpath(
        '//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(random.randint(13, 17))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeDailySetSurvey(browser: WebDriver, cardNumber: int):
    time.sleep(5)
    browser.find_element_by_xpath(
        '//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    browser.find_element_by_id("btoption" + str(random.randint(0, 1))).click()
    time.sleep(random.randint(10, 15))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeDailySetQuiz(browser: WebDriver, cardNumber: int):
    time.sleep(2)
    browser.find_element_by_xpath(
        '//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    if not waitUntilQuizLoads(browser):
        resetTabs(browser)
        return
    browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
    waitUntilVisible(
        browser, By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 10
    )
    time.sleep(3)
    numberOfQuestions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.maxQuestions"
    )
    numberOfOptions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.numberOfOptions"
    )
    for question in range(numberOfQuestions):
        if numberOfOptions == 8:
            answers = []
            for i in range(8):
                if (
                    browser.find_element_by_id("rqAnswerOption" + str(i))
                    .get_attribute("iscorrectoption")
                    .lower()
                    == "true"
                ):
                    answers.append("rqAnswerOption" + str(i))
            for answer in answers:
                browser.find_element_by_id(answer).click()
                time.sleep(5)
                if not waitUntilQuestionRefresh(browser):
                    return
            time.sleep(5)
        elif numberOfOptions == 4:
            correctOption = browser.execute_script(
                "return _w.rewardsQuizRenderInfo.correctAnswer"
            )
            for i in range(4):
                if (
                    browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute(
                        "data-option"
                    )
                    == correctOption
                ):
                    browser.find_element_by_id("rqAnswerOption" + str(i)).click()
                    time.sleep(5)
                    if not waitUntilQuestionRefresh(browser):
                        return
                    break
            time.sleep(5)
    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeDailySetVariableActivity(browser: WebDriver, cardNumber: int):
    time.sleep(2)
    browser.find_element_by_xpath(
        '//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    try:
        browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
        waitUntilVisible(
            browser, By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 3
        )
    except (NoSuchElementException, TimeoutException):
        try:
            counter = str(
                browser.find_element_by_xpath(
                    '//*[@id="QuestionPane0"]/div[2]'
                ).get_attribute("innerHTML")
            )[:-1][1:]
            numberOfQuestions = max([int(s) for s in counter.split() if s.isdigit()])
            for question in range(numberOfQuestions):
                browser.execute_script(
                    "document.evaluate(\"//*[@id='QuestionPane"
                    + str(question)
                    + "']/div[1]/div[2]/a["
                    + str(random.randint(1, 3))
                    + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()'
                )
                time.sleep(5)
                browser.find_element_by_xpath(
                    '//*[@id="AnswerPane'
                    + str(question)
                    + '"]/div[1]/div[2]/div[4]/a/div/span/input'
                ).click()
                time.sleep(3)
            time.sleep(5)
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
            time.sleep(2)
            return
        except NoSuchElementException:
            time.sleep(random.randint(5, 9))
            browser.close()
            time.sleep(2)
            browser.switch_to.window(window_name=browser.window_handles[0])
            time.sleep(2)
            return
    time.sleep(3)
    correctAnswer = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.correctAnswer"
    )
    if (
        browser.find_element_by_id("rqAnswerOption0").get_attribute("data-option")
        == correctAnswer
    ):
        browser.find_element_by_id("rqAnswerOption0").click()
    else:
        browser.find_element_by_id("rqAnswerOption1").click()
    time.sleep(10)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeDailySetThisOrThat(browser: WebDriver, cardNumber: int):
    time.sleep(2)
    browser.find_element_by_xpath(
        '//*[@id="daily-sets"]/mee-card-group[1]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-daily-set-item-content/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    if not waitUntilQuizLoads(browser):
        resetTabs(browser)
        return
    browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
    waitUntilVisible(
        browser, By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 10
    )
    time.sleep(3)
    for question in range(10):
        answerEncodeKey = browser.execute_script("return _G.IG")

        answer1 = browser.find_element_by_id("rqAnswerOption0")
        answer1Title = answer1.get_attribute("data-option")
        answer1Code = getAnswerCode(answerEncodeKey, answer1Title)

        answer2 = browser.find_element_by_id("rqAnswerOption1")
        answer2Title = answer2.get_attribute("data-option")
        answer2Code = getAnswerCode(answerEncodeKey, answer2Title)

        correctAnswerCode = browser.execute_script(
            "return _w.rewardsQuizRenderInfo.correctAnswer"
        )

        if answer1Code == correctAnswerCode:
            answer1.click()
            time.sleep(8)
        elif answer2Code == correctAnswerCode:
            answer2.click()
            time.sleep(8)

    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def getDashboardData(browser: WebDriver) -> dict:
    dashboard = findBetween(
        browser.find_element_by_xpath("/html/body").get_attribute("innerHTML"),
        "var dashboard = ",
        ';\n        appDataModule.constant("prefetchedDashboard", dashboard);',
    )
    dashboard = json.loads(dashboard)
    return dashboard


def completeDailySet(browser: WebDriver):
    d = getDashboardData(browser)["dailySetPromotions"]
    todayDate = datetime.today().strftime("%m/%d/%Y")
    todayPack = []
    for date, data in d.items():
        if date == todayDate:
            todayPack = data
    for activity in todayPack:
        try:
            if activity["complete"] == False:
                cardNumber = int(activity["offerId"][-1:])
                if activity["promotionType"] == "urlreward":
                    print("[DAILY SET]", "Completing search of card " + str(cardNumber))
                    completeDailySetSearch(browser, cardNumber)
                if activity["promotionType"] == "quiz":
                    if (
                        activity["pointProgressMax"] == 50
                        and activity["pointProgress"] == 0
                    ):
                        print(
                            "[DAILY SET]",
                            "Completing This or That of card " + str(cardNumber),
                        )
                        completeDailySetThisOrThat(browser, cardNumber)
                    elif (
                        activity["pointProgressMax"] == 40
                        or activity["pointProgressMax"] == 30
                    ) and activity["pointProgress"] == 0:
                        print(
                            "[DAILY SET]", "Completing quiz of card " + str(cardNumber)
                        )
                        completeDailySetQuiz(browser, cardNumber)
                    elif (
                        activity["pointProgressMax"] == 10
                        and activity["pointProgress"] == 0
                    ):
                        searchUrl = urllib.parse.unquote(
                            urllib.parse.parse_qs(
                                urllib.parse.urlparse(activity["destinationUrl"]).query
                            )["ru"][0]
                        )
                        searchUrlQueries = urllib.parse.parse_qs(
                            urllib.parse.urlparse(searchUrl).query
                        )
                        filters = {}
                        for filter in searchUrlQueries["filters"][0].split(" "):
                            filter = filter.split(":", 1)
                            filters[filter[0]] = filter[1]
                        if "PollScenarioId" in filters:
                            print(
                                "[DAILY SET]",
                                "Completing poll of card " + str(cardNumber),
                            )
                            completeDailySetSurvey(browser, cardNumber)
                        else:
                            print(
                                "[DAILY SET]",
                                "Completing quiz of card " + str(cardNumber),
                            )
                            completeDailySetVariableActivity(browser, cardNumber)
        except:
            resetTabs(browser)


def getAccountPoints(browser: WebDriver) -> int:
    return getDashboardData(browser)["userStatus"]["availablePoints"]


def completePunchCard(browser: WebDriver, url: str, childPromotions: dict):
    browser.get(url)
    for child in childPromotions:
        if child["complete"] == False:
            if child["promotionType"] == "urlreward":
                browser.execute_script(
                    "document.getElementsByClassName('offer-cta')[0].click()"
                )
                time.sleep(1)
                browser.switch_to.window(window_name=browser.window_handles[1])
                time.sleep(random.randint(13, 17))
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0])
                time.sleep(2)
            if child["promotionType"] == "quiz":
                browser.execute_script(
                    "document.getElementsByClassName('offer-cta')[0].click()"
                )
                time.sleep(1)
                browser.switch_to.window(window_name=browser.window_handles[1])
                time.sleep(8)
                counter = str(
                    browser.find_element_by_xpath(
                        '//*[@id="QuestionPane0"]/div[2]'
                    ).get_attribute("innerHTML")
                )[:-1][1:]
                numberOfQuestions = max(
                    [int(s) for s in counter.split() if s.isdigit()]
                )
                for question in range(numberOfQuestions):
                    browser.execute_script(
                        "document.evaluate(\"//*[@id='QuestionPane"
                        + str(question)
                        + "']/div[1]/div[2]/a["
                        + str(random.randint(1, 3))
                        + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()'
                    )
                    time.sleep(5)
                    browser.find_element_by_xpath(
                        '//*[@id="AnswerPane'
                        + str(question)
                        + '"]/div[1]/div[2]/div[4]/a/div/span/input'
                    ).click()
                    time.sleep(3)
                time.sleep(5)
                browser.close()
                time.sleep(2)
                browser.switch_to.window(window_name=browser.window_handles[0])
                time.sleep(2)


def completePunchCards(browser: WebDriver):
    punchCards = getDashboardData(browser)["punchCards"]
    for punchCard in punchCards:
        try:
            if (
                punchCard["parentPromotion"] != None
                and punchCard["childPromotions"] != None
                and punchCard["parentPromotion"]["complete"] == False
                and punchCard["parentPromotion"]["pointProgressMax"] != 0
            ):
                url = punchCard["parentPromotion"]["attributes"]["destination"]
                path = url.replace(
                    "https://account.microsoft.com/rewards/dashboard/", ""
                )
                userCode = path[:4]
                dest = (
                    "https://account.microsoft.com/rewards/dashboard/"
                    + userCode
                    + path.split(userCode)[1]
                )
                completePunchCard(browser, dest, punchCard["childPromotions"])
        except:
            resetTabs(browser)
    time.sleep(2)
    browser.get("https://account.microsoft.com/rewards/")
    time.sleep(2)


def completeMorePromotionSearch(browser: WebDriver, cardNumber: int):
    browser.find_element_by_xpath(
        '//*[@id="more-activities"]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(random.randint(13, 17))
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeMorePromotionQuiz(browser: WebDriver, cardNumber: int):
    browser.find_element_by_xpath(
        '//*[@id="more-activities"]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    if not waitUntilQuizLoads(browser):
        resetTabs(browser)
        return
    browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
    waitUntilVisible(
        browser, By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 10
    )
    time.sleep(3)
    numberOfQuestions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.maxQuestions"
    )
    numberOfOptions = browser.execute_script(
        "return _w.rewardsQuizRenderInfo.numberOfOptions"
    )
    for question in range(numberOfQuestions):
        if numberOfOptions == 8:
            answers = []
            for i in range(8):
                if (
                    browser.find_element_by_id("rqAnswerOption" + str(i))
                    .get_attribute("iscorrectoption")
                    .lower()
                    == "true"
                ):
                    answers.append("rqAnswerOption" + str(i))
            for answer in answers:
                browser.find_element_by_id(answer).click()
                time.sleep(5)
                if not waitUntilQuestionRefresh(browser):
                    return
            time.sleep(5)
        elif numberOfOptions == 4:
            correctOption = browser.execute_script(
                "return _w.rewardsQuizRenderInfo.correctAnswer"
            )
            for i in range(4):
                if (
                    browser.find_element_by_id("rqAnswerOption" + str(i)).get_attribute(
                        "data-option"
                    )
                    == correctOption
                ):
                    browser.find_element_by_id("rqAnswerOption" + str(i)).click()
                    time.sleep(5)
                    if not waitUntilQuestionRefresh(browser):
                        return
                    break
            time.sleep(5)
    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeMorePromotionABC(browser: WebDriver, cardNumber: int):
    browser.find_element_by_xpath(
        '//*[@id="more-activities"]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    counter = str(
        browser.find_element_by_xpath('//*[@id="QuestionPane0"]/div[2]').get_attribute(
            "innerHTML"
        )
    )[:-1][1:]
    numberOfQuestions = max([int(s) for s in counter.split() if s.isdigit()])
    for question in range(numberOfQuestions):
        browser.execute_script(
            "document.evaluate(\"//*[@id='QuestionPane"
            + str(question)
            + "']/div[1]/div[2]/a["
            + str(random.randint(1, 3))
            + ']/div", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()'
        )
        time.sleep(5)
        browser.find_element_by_xpath(
            '//*[@id="AnswerPane'
            + str(question)
            + '"]/div[1]/div[2]/div[4]/a/div/span/input'
        ).click()
        time.sleep(3)
    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeMorePromotionThisOrThat(browser: WebDriver, cardNumber: int):
    browser.find_element_by_xpath(
        '//*[@id="more-activities"]/div/mee-card['
        + str(cardNumber)
        + "]/div/card-content/mee-rewards-more-activities-card-item/div/div[3]/a"
    ).click()
    time.sleep(1)
    browser.switch_to.window(window_name=browser.window_handles[1])
    time.sleep(8)
    if not waitUntilQuizLoads(browser):
        resetTabs(browser)
        return
    browser.find_element_by_xpath('//*[@id="rqStartQuiz"]').click()
    waitUntilVisible(
        browser, By.XPATH, '//*[@id="currentQuestionContainer"]/div/div[1]', 10
    )
    time.sleep(3)
    for question in range(10):
        answerEncodeKey = browser.execute_script("return _G.IG")

        answer1 = browser.find_element_by_id("rqAnswerOption0")
        answer1Title = answer1.get_attribute("data-option")
        answer1Code = getAnswerCode(answerEncodeKey, answer1Title)

        answer2 = browser.find_element_by_id("rqAnswerOption1")
        answer2Title = answer2.get_attribute("data-option")
        answer2Code = getAnswerCode(answerEncodeKey, answer2Title)

        correctAnswerCode = browser.execute_script(
            "return _w.rewardsQuizRenderInfo.correctAnswer"
        )

        if answer1Code == correctAnswerCode:
            answer1.click()
            time.sleep(8)
        elif answer2Code == correctAnswerCode:
            answer2.click()
            time.sleep(8)

    time.sleep(5)
    browser.close()
    time.sleep(2)
    browser.switch_to.window(window_name=browser.window_handles[0])
    time.sleep(2)


def completeMorePromotions(browser: WebDriver):
    morePromotions = getDashboardData(browser)["morePromotions"]
    i = 0
    for promotion in morePromotions:
        try:
            i += 1
            if promotion["complete"] == False and promotion["pointProgressMax"] != 0:
                if promotion["promotionType"] == "urlreward":
                    completeMorePromotionSearch(browser, i)
                elif (
                    promotion["promotionType"] == "quiz"
                    and promotion["pointProgress"] == 0
                ):
                    if promotion["pointProgressMax"] == 10:
                        completeMorePromotionABC(browser, i)
                    elif (
                        promotion["pointProgressMax"] == 30
                        or promotion["pointProgressMax"] == 40
                    ):
                        completeMorePromotionQuiz(browser, i)
                    elif promotion["pointProgressMax"] == 50:
                        completeMorePromotionThisOrThat(browser, i)
                else:
                    if (
                        promotion["pointProgressMax"] == 100
                        or promotion["pointProgressMax"] == 200
                    ):
                        completeMorePromotionSearch(browser, i)
        except:
            resetTabs(browser)


def getRemainingSearches(browser: WebDriver):
    dashboard = getDashboardData(browser)
    searchPoints = 1
    counters = dashboard["userStatus"]["counters"]
    if not "pcSearch" in counters:
        return 0, 0
    progressDesktop = (
        counters["pcSearch"][0]["pointProgress"]
        + counters["pcSearch"][1]["pointProgress"]
    )
    targetDesktop = (
        counters["pcSearch"][0]["pointProgressMax"]
        + counters["pcSearch"][1]["pointProgressMax"]
    )
    if targetDesktop == 33:
        # Level 1 EU
        searchPoints = 3
    elif targetDesktop == 55:
        # Level 1 US
        searchPoints = 5
    elif targetDesktop == 102:
        # Level 2 EU
        searchPoints = 3
    elif targetDesktop >= 170:
        # Level 2 US
        searchPoints = 5
    remainingDesktop = int((targetDesktop - progressDesktop) / searchPoints)
    remainingMobile = 0
    if dashboard["userStatus"]["levelInfo"]["activeLevel"] != "Level1":
        progressMobile = counters["mobileSearch"][0]["pointProgress"]
        targetMobile = counters["mobileSearch"][0]["pointProgressMax"]
        remainingMobile = int((targetMobile - progressMobile) / searchPoints)
    return remainingDesktop, remainingMobile


def prRed(prt):
    print("\033[91m{}\033[00m".format(prt))


def prGreen(prt):
    print("\033[92m{}\033[00m".format(prt))


def prPurple(prt):
    print("\033[95m{}\033[00m".format(prt))


def prYellow(prt):
    print("\033[93m{}\033[00m".format(prt))


LANG, GEO = "", ""


def main():
    prRed(
        """
    ███╗   ███╗███████╗    ███████╗ █████╗ ██████╗ ███╗   ███╗███████╗██████╗ 
    ████╗ ████║██╔════╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝██╔══██╗
    ██╔████╔██║███████╗    █████╗  ███████║██████╔╝██╔████╔██║█████╗  ██████╔╝
    ██║╚██╔╝██║╚════██║    ██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║███████║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗██║  ██║
    ╚═╝     ╚═╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝"""
    )
    prPurple("        by Charles Bel (@charlesbel)               version 1.1\n")

    LANG, GEO, TZ = getCCodeLangAndOffset()

    try:
        account_path = os.path.dirname(os.path.abspath(__file__)) + "/accounts.json"
        ACCOUNTS = json.load(open(account_path, "r"))
    except FileNotFoundError:
        with open(account_path, "w") as f:
            f.write(
                json.dumps(
                    [{"username": "Your Email", "password": "Your Password"}], indent=4
                )
            )
        prPurple(
            """
    [ACCOUNT] Accounts credential file "accounts.json" created.
    [ACCOUNT] Edit with your credentials and save, then press any key to continue...
        """
        )
        input()
        ACCOUNTS = json.load(open(account_path, "r"))

    # random.shuffle(ACCOUNTS)

    for account in ACCOUNTS:

        prYellow("********************" + account["username"] + "********************")
        browser = browserSetup(True, PC_USER_AGENT)
        print("[LOGIN]", "Logging-in...")
        login(browser, account["username"], account["password"])
        prGreen("[LOGIN] Logged-in successfully !")
        startingPoints = POINTS_COUNTER
        prGreen(
            "[POINTS] You have " + str(POINTS_COUNTER) + " points on your account !"
        )
        browser.get("https://account.microsoft.com/rewards/")
        print("[DAILY SET]", "Trying to complete the Daily Set...")
        completeDailySet(browser)
        prGreen("[DAILY SET] Completed the Daily Set successfully !")
        print("[PUNCH CARDS]", "Trying to complete the Punch Cards...")
        completePunchCards(browser)
        prGreen("[PUNCH CARDS] Completed the Punch Cards successfully !")
        print("[MORE PROMO]", "Trying to complete More Promotions...")
        completeMorePromotions(browser)
        prGreen("[MORE PROMO] Completed More Promotions successfully !")
        remainingSearches, remainingSearchesM = getRemainingSearches(browser)
        if remainingSearches != 0:
            print("[BING]", "Starting Desktop and Edge Bing searches...")
            bingSearches(browser, remainingSearches)
            prGreen("[BING] Finished Desktop and Edge Bing searches !")
        browser.quit()
        pc_points = POINTS_COUNTER - startingPoints
        prGreen(
            "[POINTS] You have earned " + str(pc_points) + " points for Desktop today !"
        )

        if remainingSearchesM != 0:
            browser = browserSetup(True, MOBILE_USER_AGENT)
            print("[LOGIN]", "Logging-in as mobile...")
            login(browser, account["username"], account["password"], True)
            print("[LOGIN]", "Logged-in successfully !")
            print("[BING]", "Starting Mobile Bing searches...")
            bingSearches(browser, remainingSearchesM, True)
            prGreen("[BING] Finished Mobile Bing searches !")
            browser.quit()
        mobile_points = POINTS_COUNTER - startingPoints - pc_points
        total_points = POINTS_COUNTER - startingPoints

        prGreen(
            "[POINTS] You have earned "
            + str(mobile_points)
            + " points for mobile today !"
        )
        prGreen(
            "[POINTS] You have earned " + str(total_points) + " points total today !"
        )

        # todays_date = date.today()

        # points_dict = {"reward_date":todays_date, "pc_points":pc_points, "mobile_points":mobile_points, "total_points":total_points}
        # df = pd.read_csv("points.csv")

        # df = df.append(points_dict, ignore_index=True)
        # df['reward_date'] = pd.to_datetime(df.reward_date, format='%Y-%m-%d')
        # df.to_csv('points.csv', index=False)
        prGreen("[POINTS] You are now at " + str(POINTS_COUNTER) + " points !\n")


# Execute Main
main()