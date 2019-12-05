from transitions.extensions import GraphMachine

from utils import send_text_message

# web scraping
from bs4 import BeautifulSoup
from selenium import webdriver
import os


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.url = ""
        self.prev = ""
        self.next = ""

    def is_going_to_CLstate(self, event):
        text = event.message.text
        if text.strip() == "歐冠":
            self.url = "https://www.goal.com/zh-tw/%E6%AD%90%E6%B4%B2%E8%81%AF%E8%B3%BD%E5%86%A0%E8%BB%8D%E7%9B%83/%E8%B3%BD%E7%A8%8B-%E8%B3%BD%E6%9E%9C/4oogyu6o156iphvdvphwpck10"
            return True
        else:
            return False


    #def is_going_to_CLprev(self, event):
    #    text = event.message.text
    #    return text.lower() == "go to CLprev"

    def on_enter_CLstate(self, event):
        print("I'm entering CLstate")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=self.chrome_options)
        if self.url == "":
            reply_token = event.reply_token
            send_text_message(reply_token, "Do not have next competition")
            return
        driver.get(self.url)
        r = driver.execute_script("return document.documentElement.outerHTML")
        driver.quit()

        # for debug
        f = open("output.txt", "w")
        f.write(str(r))
        f.close()

        # goal.com
        soup = BeautifulSoup(r, "html.parser")
        time = soup.find("div", {"class": "nav-switch__label"}).text
        s = time + "\n"
        teams = soup.find_all("span", {"class": "match-row__team-name"})
        scores = soup.find_all("b", {"class": "match-row__goals"})
        status = soup.find_all("div", {"class": "match-row__status"})
        i = 0
        while i < len(status):
            state = status[i].find("span", {"class": "match-row__state"})
            if state != None:
                s = s + "\n" + teams[2*i].text + "  " + scores[2*i].text + ":" + scores[2*i+1].text + "  " + teams[2*i+1].text
            else:
                s = s + "\n" + teams[2*i].text + " vs " + teams[2*i+1].text
            i = i + 1

        prev = soup.find("a", {"class": "nav-switch__prev"})
        if prev is None:
            self.prev = ""
        else:
            self.prev = prev.get("href")
        next = soup.find("a", {"class": "nav-switch__next"})
        if next is None:
            self.next = ""
        else:
            self.next = next.get("href")

        # uefa.com
        """soup = BeautifulSoup(r, "html.parser")
        grouptimes = soup.select("li.tab.js-tabbify-tab.active")
        grouptime = grouptimes[0]["data-group"]
        time = grouptimes[0].find("span", {"class": "hidden-xs"}).text
        items = soup.find_all("div", {"class": "mm-match js-tabbify-elem col-xs-12 col-sm-6 col-lg-3"})
        str = time + ": \n"
        for item in items:
            hometeam = item.find("div", {"class": "team-home is-club"}).text.strip()
            awayteam = item.find("div", {"class": "team-away is-club"}).text.strip()
            str = str + "\n\t" + hometeam + " vs " + awayteam
        """

        reply_token = event.reply_token
        send_text_message(reply_token, s)
        #self.go_back()

    def is_CLprev(self, event):
        text = event.message.text
        if text.lower() == "prev":
            self.url = self.prev
            print("set url = prev")
            return True
        else:
            return False

    def is_CLnext(self, event):
        text = event.message.text
        if text.lower() == "next":
            self.url = self.next
            print("set url = next")
            return True
        else:
            return False

    #def on_exit_CLstate(self):
    #    print("Leaving CLstate")

    #def on_enter_CLprev(self, event):
    #    print("I"m entering CLprev")

    #    reply_token = event.reply_token
    #    send_text_message(reply_token, "Trigger CLprev")
    #    self.go_back()

    #def on_exit_CLprev(self):
    #    print("Leaving CLprev")

    #def on_enter_state3(self, event):
    #    print("I"m entering state3")

    #    reply_token = event.reply_token
    #    send_text_message(reply_token, "You are asshole, too")
    #    self.go_back()

    #def on_exit_state3(self):
    #    print("Leaving state3 and go to user state")
