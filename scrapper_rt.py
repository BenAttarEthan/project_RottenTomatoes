from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import requests


def get_page(page_number):
    """
    The function goes to the page numbered page_number
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome(ChromeDriverManager().install())
    wd.get("https://www.rottentomatoes.com/browse/movies_at_home")
    for i in range(page_number):
        python_button = wd.find_element(By.XPATH, '//*[@id="main-page-content"]/div/div[5]/button')
        python_button.click()
        time.sleep(3)
    text = wd.page_source
    web_scraper(text)
    wd.close()


def web_scraper(text):
    """
    This function scrap the "AT HOME" movies from ROTTEN TOMATOES
    """
    try:
        soup = BeautifulSoup(text)
        main_movies = soup.find_all('a', {'class': 'js-tile-link', 'href': True})
        # Let's go to the movie page to catch contents
        for movie_url in main_movies:
            movie_page = requests.get('https://www.rottentomatoes.com' + movie_url['href'])
            if movie_page.ok:
                movie_soup = BeautifulSoup(movie_page.text)
                movie_info = {'Title': movie_soup.find('score-board').find('h1').string,
                              'Tomatometer': movie_soup.find('score-board').get('tomatometerscore')}
                movie_infos = movie_soup.find('ul', {'class': 'content-meta info'}).find_all('li')
                for content in movie_infos:
                    try:
                        movie_info[content.find('div').string] = content.find('div', {
                            'class': 'meta-value'}).string.strip()
                    except AttributeError:
                        if content.find('div', {'class': 'meta-value'}).find_all('a'):
                            movie_info[content.find('div').string] = [c.string.strip() for c in
                                                                      content.find('div',
                                                                                   {'class': 'meta-value'})
                                                                      .find_all('a')]
                print(movie_info)
    except ValueError as err:
        print(err)


def main():
    get_page(int(input('Choose the number of pages you want to scrape : ')))


if __name__ == '__main__':
    main()
