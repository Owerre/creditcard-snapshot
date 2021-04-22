# Created by Solomon Owerre.

# Imports
from selenium import webdriver
from bs4 import BeautifulSoup
import sys
import json


def make_soup(start_url):
    """Beautiful parser"""
    driver = webdriver.Chrome('/Users/sowerre/bin/chromedriver')
    driver.get(start_url)
    driver.implicitly_wait(100)
    html = driver.page_source
    bs = BeautifulSoup(html, 'lxml')
    return bs

# From: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3


def progress(count, total, status=''):
    """Displays an inline progress bar"""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def get_links(start_url):
    """Fetch all the links to the next page"""
    count = 0
    links = set()
    links.add(start_url)
    soup = make_soup(start_url)
    all_links = soup.find('div', class_="paginator").find_all('a')
    total = len(all_links)
    for link in all_links:
        if link:
            links.add('https://www.influenster.com/' + link['href'])
        progress(count, total - 1, "Fetching links")
        count += 1
    return links


# alternative links to next page
url_links = []
for i in range(1, 76):
    urls = 'url_page={}'.format(i)
    url_links.append(urls)


def get_data(start_url):
    """Fetch data from each link"""
    links = url_links  # get_links(start_url)
    count = 0
    total = len(links)
    content = []
    ratings = []

    for link in links:
        soup = make_soup(link)
        progress(count, total - 1, "Fetching data")
        count += 1
        for review in soup.find_all('div', class_="content-item-text review-text",
                                    itemprop="reviewBody"):
            content.append(review.text.strip('\n'))
        for rating in soup.find_all('div', class_='avg-stars'):
            star = float(rating['data-stars'])
            if star.is_integer() is True:
                ratings.append(star)

    review_dict = {'reviews': content}
    rating_dict = {'rating': ratings}

    with open('../raw_data/review.json', 'a') as f:
        json.dump(review_dict, f)
    with open('../raw_data/rating.json', 'a') as f:
        json.dump(rating_dict, f)
