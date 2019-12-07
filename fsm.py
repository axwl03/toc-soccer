from transitions.extensions import GraphMachine

from utils import send_text_message, send_image_url

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

        print(s)
        reply_token = event.reply_token
        send_text_message(reply_token, s)

    def is_CLprev(self, event):
        text = event.message.text
        if text.lower() == "prev":
            self.url = self.prev
            return True
        else:
            return False

    def is_CLnext(self, event):
        text = event.message.text
        if text.lower() == "next":
            self.url = self.next
            return True
        else:
            return False

    def is_going_to_user(self, event):
        text = event.message.text
        return text.lower() == "user"

    def on_enter_user(self, event):
        reply_token = event.reply_token
        s = "輸入\"歐冠\" 看最近歐冠賽程\nnext和prev可以看不同日期賽程或結果\n\n\"找教學\"\n推薦不同項目的足球影片\n\n\"fsm\" 展示state diagram"
        send_text_message(reply_token, s)

    def on_enter_showfsm(self, event):
        reply_token = event.reply_token
        send_image_url(reply_token, "https://raw.githubusercontent.com/axwl03/toc-soccer/master/fsm.png")

    def is_going_to_showfsm(self, event):
        text = event.message.text
        return text.lower() == "fsm"

    def on_enter_tutorial(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "這邊有推薦的教學影片\n輸入想要學的項目\n帶球 or 射門 or 傳球")

    def is_going_to_tutorial(self, event):
        text = event.message.text
        return text == "找教學"

    def on_enter_dribble(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "帶球影片:\nhttps://www.youtube.com/watch?v=LRW3UpQrgPQ\nhttps://www.youtube.com/watch?v=D1FINJT_QIQ\nhttps://www.youtube.com/watch?v=0Zj3hhiYF0c")

    def is_going_to_dribble(self, event):
        text = event.message.text
        return text == "帶球"

    def on_enter_shooting(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "射門影片:\nhttps://www.youtube.com/watch?v=2wHXqTqVPFo\nhttps://www.youtube.com/watch?v=fb72F-NMkhM\nhttps://www.youtube.com/watch?v=XSOx4wMnNbA")

    def is_going_to_shooting(self, event):
        text = event.message.text
        return text == "射門"

    def on_enter_passing(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "傳球影片:\nhttps://www.youtube.com/watch?v=QioehtsQMxs\nhttps://www.youtube.com/watch?v=P-WeVjGcRss\nhttps://www.youtube.com/watch?v=E3sjcv0m1z4")

    def is_going_to_passing(self, event):
        text = event.message.text
        return text == "傳球"

    def on_enter_dribble2(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "50個腳感練習:\nhttps://www.youtube.com/watch?v=ObncYq18lMw\n\n過人方法:\nhttps://www.youtube.com/watch?v=Q0-qHJzn2gk\n\n必學練習:\nhttps://www.youtube.com/watch?v=jwIHc9rz7yo")

    def is_going_to_dribble2(self, event):
        text = event.message.text
        return text == "看更多"

    def on_enter_passing2(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "15個傳球練習:\nhttps://www.youtube.com/watch?v=ttbBSoovPc4\n\n地面快速傳球:\nhttps://www.youtube.com/watch?v=vNsqMKT98Ms\n\n所有傳球技巧:\nhttps://www.youtube.com/watch?v=5TgAUdK_kIs")

    def is_going_to_passing2(self, event):
        text = event.message.text
        return text == "看更多"

    def on_enter_shooting2(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "香蕉球:\nhttps://www.youtube.com/watch?v=wkcmthkXXfc\n\n下墜球:\nhttps://www.youtube.com/watch?v=0oJ8oIudXYs\n\n落葉球:\nhttps://www.youtube.com/watch?v=HRJg8--y-Q0")

    def is_going_to_shooting2(self, event):
        text = event.message.text
        return text == "看更多"
