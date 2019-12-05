from transitions.extensions import GraphMachine

from utils import send_text_message

# web scraping
from bs4 import BeautifulSoup
from selenium import webdriver
import os


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "championsleague"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def on_enter_state1(self, event):
        print("I'm entering state1")

        # web scraping
        url = 'https://www.google.com'

        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER PATH"), chrome_options=chrome_options)
        print(driver.get(url))
        """r = driver.execute_script('return document.documentElement.outerHTML')
        driver.quit()

        soup = BeautifulSoup(r, 'html.parser')
        grouptimes = soup.select('li.tab.js-tabbify-tab.active')
        grouptime = grouptimes[0]['data-group']

        time = grouptimes[0].find('span', {'class': 'hidden-xs'}).text

        items = soup.find_all('div', {'class': 'mm-match js-tabbify-elem col-xs-12 col-sm-6 col-lg-3'})
        str = time + ": \n"
        for item in items:
            hometeam = item.find('div', {'class': 'team-home is-club'}).text.strip()
            awayteam = item.find('div', {'class': 'team-away is-club'}).text.strip()
            str = str + '\n\t' + hometeam + ' vs ' + awayteam"""
        # scaping ends here

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state1")
        #self.go_back()

    #def on_exit_state1(self):
    #    print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")

    # testing
    def is_going_to_state3(self, event):
        print("executed is going to state3")
        text = event.message.text
        return text == "asshole"

    def on_enter_state3(self, event):
        print("I'm entering state3")

        reply_token = event.reply_token
        send_text_message(reply_token, "You are asshole, too")
        self.go_back()

    def on_exit_state3(self):
        print("Leaving state3 and go to user state")

    def is_state1_to_state2(self, event):
        text = event.message.text
        return text.lower() == "holy shit"
