from bs4 import BeautifulSoup
import requests, json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

GOOGLE_FORM = 'https://forms.gle/1EZEnfgpZDBcDzcg8'
ZILLOW_URL = 'https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.30389632177734%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D'
CHROME_DRIVER_PATH = '<Chrome Driver Path>'
place_to_search = 'San Francisco, CA'
ZILLOW_MAIN_PAGE = 'https://www.zillow.com/'


class ZillowRent:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US'
    }

    def __init__(self):
        self.response = requests.get(ZILLOW_URL, headers=self.headers)
        self.zillow_results = self.response.text
        self.soup = BeautifulSoup(self.zillow_results, "html.parser")
        self.data = json.loads(str(self.soup.select_one("script[data-zrr-shared-data-key]").contents[0]).strip("!<>-"))

    def getHouseLinks(self):
        house_links = [
            result["detailUrl"]
            for result in self.data["cat1"]["searchResults"]["listResults"]
        ]

        house_links = [links.replace(links, ZILLOW_MAIN_PAGE+links) if not links.startswith("http") else links for links in house_links]
        return house_links

    def getHouseAddr(self):
        house_address = [
            result["address"]
            for result in self.data["cat1"]["searchResults"]["listResults"]
        ]
        return house_address

    def getRentPrice(self):
        house_rent = [
            int(result["units"][0]["price"].strip("$").replace(",", "").strip("+"))
            if "units" in result
            else result["unformattedPrice"]
            for result in self.data["cat1"]["searchResults"]["listResults"]
        ]
        return house_rent

class GoogleForm:
    def __init__(self):
        self.data = ZillowRent()
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        self.driver.get(GOOGLE_FORM)
        time.sleep(5)

    def getData(self):
        links = self.data.getHouseLinks()
        addr = self.data.getHouseAddr()
        rents = self.data.getRentPrice()
        return links, addr, rents

    def fillForm(self):
        links, addr, rents = self.getData()
        for index in range(len(links)):
            address_element = self.driver.find_element(By.XPATH, value='/html/body/div/div[2]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
            address_element.send_keys(addr[index])
            rent_element = self.driver.find_element(By.XPATH, value='/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
            rent_element.send_keys(rents[index])
            links_element = self.driver.find_element(By.XPATH, value='/html/body/div/div[2]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
            links_element.send_keys(links[index])
            submit = self.driver.find_element(By.XPATH, value='/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
            submit.click()
            time.sleep(3)
            next_response = self.driver.find_element(By.CSS_SELECTOR, value='.c2gzEf a')
            next_response.click()
            time.sleep(5)


form = GoogleForm()
form.fillForm()
