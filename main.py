import config
from datetime import datetime
from bs4 import BeautifulSoup
import requests

def send_nomina(username, password, tg_token, tg_chat_id):
    session = requests.Session()

    login_page = session.get('https://documentos.otgir.com:444/default.aspx')
    login_soup = BeautifulSoup(login_page.content, 'html.parser')
    eventValidation = login_soup.select('#__EVENTVALIDATION')[0].get('value')
    viewState = login_soup.select('#__VIEWSTATE')[0].get('value')

    login_form_data = {
        '__LASTFOCUS': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewState,
        '__EVENTVALIDATION': eventValidation,
        'ctl00$ContentPlaceHolder1$Login1$UserName': username,
        'ctl00$ContentPlaceHolder1$Login1$Password': password,
        'ctl00$ContentPlaceHolder1$Login1$LoginButton': 'Iniciar sesión'
    }

    documents_page = session.post('https://documentos.otgir.com:444/default.aspx', data=login_form_data)
    documents_soup = BeautifulSoup(documents_page.content, 'html.parser')

    table_body = documents_soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvDescargas'})
    data = []
    rows = table_body.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        link = 'https://documentos.otgir.com:444/MemberPages/' + cols[0].find('a').get('href')
        name = cols[1].text.strip()
        date = datetime.strptime(cols[6].text.strip(), '%d/%m/%Y')
        data.append({'link': link, 'name': name, 'date': date})

    doc = session.get(data[0]['link']).content
    requests.post(f'https://api.telegram.org/bot{tg_token}/sendDocument', data={'chat_id': tg_chat_id}, files={'document': (data[0]['name'] + '.pdf', doc)})


for each_user in config.USERS:
    send_nomina(each_user['USERNAME'], each_user['PASSWORD'], config.TELEGRAM_TOKEN, each_user['TELEGRAM_CHAT_ID'])
