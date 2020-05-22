import requests
from bs4 import BeautifulSoup
import csv
import os


URL = 'https://www.wildberries.ru/catalog/obuv/muzhskaya/kedy-i-krossovki/krossovki?brand=1031;166'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/81.0.4044.96 YaBrowser/20.4.0.1461 Yowser/2.5 Safari/537.36',
           'acept': '*/*'}
FILE = 'wb.csv'


def get_csv(items, path):
    with open(path, 'w', newline='') as file:
        write = csv.writer(file, delimiter=';')
        write.writerow(['Кампания', 'Названия кроссовок', 'Ссылка', 'Цена без акции', 'Скидка', 'Цена по акции'])
        for item in items:
            write.writerow([item['mark'], item['title'], item['link'],
                           item['price_old'], item['sale'], item['price']])


def clean_price(text):
    figures = [i for i in text if i.isdigit()]
    clean_text = ''.join(figures)
    if not clean_text:
        return None
    return clean_text


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('div', class_='pageToInsert')
    if pages:
        return int(clean_price(pages[-1].get_text())[-1])
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='dtList i-dtList j-card-item')
    cross = []
    for item in items:
        price_old = item.find('span', class_='price-old-block')
        if price_old:
            price_old = clean_price(price_old.get_text()[:-3]) + ' р'
        else:
            print('Error')
        sale = item.find('span', class_='price-old-block')
        if sale:
            sale = sale.get_text()[-3:-1] + ' %'
        else:
            print('Error')
        price = item.find('ins', class_='lower-price')
        if price:
            price = clean_price(price.get_text()) + ' р'
        else:
            print('Error')

        cross.append({
            'mark': item.find('strong', class_='brand-name').get_text(strip=True).replace('/', ''),
            'title': item.find('span', class_='goods-name').get_text(),
            'link': item.find('a', class_='ref_goods_n_p j-open-full-product-card').get('href'),
            'price_old': price_old,
            'sale': sale,
            'price': price
                    })
    return cross


def pars():
    html = get_html(URL)
    if html.status_code == 200:
        cross = []
        page_count = get_pages_count(html.text)
        for page in range(1, page_count + 1):
            print(f'Парсинг страницы {page} из {page_count}...')
            html = get_html(URL, params={'page': page})
            cross.extend(get_content(html.text))
        get_csv(cross, FILE)
        os.startfile('wb.csv')

    else:
        print('Error')


pars()
