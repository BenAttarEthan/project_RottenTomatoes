import requests
from bs4 import BeautifulSoup


def web_scraper():
    url = 'https://www.rottentomatoes.com/browse/movies_at_home/'
    response = requests.get(url)
    movies_url = []
    if response.ok:
        soup = BeautifulSoup(response.text)
        main_movies = soup.find_all('tile-dynamic', {'isvideo': 'true'})
        for movie_url in main_movies:
            movie_page = requests.get('https://www.rottentomatoes.com' +
                                      movie_url.find('button').get('data-video-player-overlay-media-url'))
            if movie_page.ok:
                movie_soup = BeautifulSoup(movie_page.text)
                movie_info = {'Title': movie_soup.find('score-board').find('h1').string,
                              'Tomatometer': movie_soup.find('score-board').get('tomatometerscore')}
                movie_infos = movie_soup.find('ul', {'class': 'content-meta info'}).find_all('li')
                for content in movie_infos:
                    try:
                        movie_info[content.find('div').string] = content.find('div', {'class': 'meta-value'}) \
                            .string.strip()
                    except AttributeError:
                        if content.find('div', {'class': 'meta-value'}).find_all('a'):
                            movie_info[content.find('div').string] = [c.string.strip() for c in
                                                                      content.find('div', {'class': 'meta-value'}) \
                                                                          .find_all('a')]
                        else:
                            movie_info[content.find('div').string] = content.find('div', {'class': 'meta-value'}) \
                                .find('time').string.strip()
                print(movie_info)
        print(movies_url)


def main():
    web_scraper()


# /html/body/div[4]/main/div[1]/div/div[3]/div/div/a[1]/tile-dynamic/div/span[2]
# /html/body/div[4]/main/div[1]/div/div[3]/div/div/a[3]/tile-dynamic/div/span[1]
if __name__ == '__main__':
    main()
