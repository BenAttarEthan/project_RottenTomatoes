import csv
import grequests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import argparse
import selenium.common.exceptions
import json
import logging
import fill_rt_project

logging.basicConfig(filename='project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def open_json(filename):
    """ Searches the file passed in argument and make sure it opens correctly and return his content as a dict"""
    try:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        logging.critical(f"{filename} has not been found. No such file in this directory.")
        exit()


# CONSTANT
JSON_CONFIG = open_json('conf.json')


def scrape_api(titles):
    movies_requests = (grequests.get(JSON_CONFIG['api_base_url'] + title) for title in titles)
    responses = grequests.map(movies_requests)
    return [response.json().get('Metascore', -1) if response.ok else -1 for response in responses]


def send_thread_request(urls, datas):
    """ Sends requests of urls in variable urls using grequests and write all the datas recovered in a csv file """
    my_requests = (grequests.get(url) for url in urls)
    responses = grequests.map(my_requests)
    writer = csv.DictWriter(datas, fieldnames=JSON_CONFIG['columns'])
    movies_info = []
    titles = []
    for response in responses:
        if response.ok:
            movie_info = get_movie_info(response.text)
            titles.append(movie_info['Title'])
            movies_info.append(movie_info)
    metascores = scrape_api(titles)
    for i in range(len(metascores)):
        movies_info[i]['Metascore'] = metascores[i]
        writer.writerow(movies_info[i])
    logging.info("Successfully wrote 5 more movies to the csv file.")


def get_movies_url(text):
    """
    Get the url from all movies in the html page passed in the text argument
    """
    soup = BeautifulSoup(text)
    main_movies = soup.find_all('a', {'class': 'js-tile-link', 'href': True})
    return main_movies


def get_movie_info(text):
    """
    Finds all the infos about a movie on its url page
    """
    movie_soup = BeautifulSoup(text)
    movie_info = {'Title': movie_soup.find('score-board').find('h1').string,
                  'Tomatometer': movie_soup.find('score-board').get('tomatometerscore')}
    print(f'Retrieving datas of {movie_info["Title"]}')
    movie_info['Metascore'] = scrape_api(movie_info['Title'])
    movie_infos = movie_soup.find('ul', {'class': 'content-meta info'}).find_all('li')
    for content in movie_infos:
        if content.find('time') is not None:
            movie_info[content.find('div').string] = content.find("time", {"datetime": True}).string.strip()
        try:
            if content.find('div').string in JSON_CONFIG['categories']:
                movie_info[content.find('div').string] = content.find('div', {
                    'class': 'meta-value'}).string.get_text()
        except AttributeError:
            if content.find('div', {'class': 'meta-value'}).find_all('a') and \
                    content.find('div').string in JSON_CONFIG['categories']:
                movie_info[content.find('div').string] = [c.string.strip() for c in
                                                          content.find('div',
                                                                       {'class': 'meta-value'})
                                                          .find_all('a')]
    movie_info['cast'] = []
    cast_infos = movie_soup.find('div', {'class': 'castSection'}).find_all('div', {'data-qa': 'cast-crew-item'})
    for content in cast_infos:
        cast_job = content.find('span', {'class': 'characters subtle smaller'})
        if cast_job.get_text().strip() == 'Director':
            break
        else:
            movie_info['cast'].append(content.find('span', {'title': True}).string.strip())
    return movie_info


def get_all_movies_info(text, datas):
    """
    This function scrap the "AT HOME" movies from ROTTEN TOMATOES
    """
    packed_urls = []
    try:
        movies = list(set(get_movies_url(text)))
        # Let's go to the movie page to catch contents
        for movie_url in movies:
            packed_urls.append(JSON_CONFIG["base"] + movie_url['href'])
            if len(packed_urls) == 5:
                send_thread_request(packed_urls, datas)
                packed_urls = []
        if len(packed_urls) != 0:
            send_thread_request(packed_urls, datas)
    except ValueError as err:
        print(err)
        logging.error(f'An error occured: {err}')


def get_page(page_number, url, datas):
    """
    The function goes to the page numbered page_number
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    wd = webdriver.Chrome(ChromeDriverManager().install())
    wd.get(url)
    for i in range(page_number):
        try:
            python_button = wd.find_element(By.XPATH, JSON_CONFIG["button"])
            python_button.click()
            time.sleep(JSON_CONFIG["sleep"])
        except selenium.common.exceptions.ElementNotInteractableException:
            print(f'You asked for {page_number} pages but there is {i + 1} pages.')
            logging.error(f'You asked for {page_number} pages but there is {i + 1} pages.')
            break
    text = wd.page_source
    get_all_movies_info(text, datas)
    logging.info('Every wanted movies were added to the csv file.')
    wd.close()
    fill_rt_project.application()
    logging.info('The database has been created with all the movies from the csv file.')
    exit()


def main():
    """
    Allows the all script to be launched throught the command line with different possible arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('Number_of_pages', type=int)
    parser.add_argument('where', choices=['home', 'theater'])
    parser.add_argument('genres', choices=['all', 'action', 'adventure', 'animation', 'anime', 'biography', 'comedy',
                                           'crime', 'documentary', 'drama', 'entertainment',
                                           'faith and spirituality', 'fantasy', 'game_show', 'lgbtq',
                                           'health and wellness', 'history', 'holiday', 'horror',
                                           'house and garden', 'kids and family', 'music', 'musical',
                                           'mystery and thriller', 'nature', 'news', 'reality', 'romance',
                                           'sci fi', 'short', 'soap', 'special interest', 'sports', 'stand up',
                                           'talk show', 'travel', 'variety', 'war', 'western'],
                        nargs='*')
    args = parser.parse_args()
    page_number = args.Number_of_pages
    genre = ','.join(args.genres)
    datas = open('data_scrapped.csv', 'w', encoding='utf-8')
    writer = csv.DictWriter(datas, fieldnames=JSON_CONFIG["columns"])
    writer.writeheader()
    if genre == 'all':
        get_page(page_number - 1, JSON_CONFIG["base"] + JSON_CONFIG["where"][args.where], datas)
    else:
        get_page(page_number - 1, JSON_CONFIG["base"] + JSON_CONFIG["where"][args.where] + '/genres:' + genre, datas)
    datas.close()


if __name__ == '__main__':
    main()
