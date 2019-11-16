import config
import utils
from datetime import datetime
from bs4 import BeautifulSoup
from google.oauth2 import service_account
import requests

session = requests.Session()


def get_nominas(username, password):

    login_page = session.get("https://documentos.otgir.com:444/default.aspx")
    login_soup = BeautifulSoup(login_page.content, "html.parser")
    eventValidation = login_soup.select("#__EVENTVALIDATION")[0].get("value")
    viewState = login_soup.select("#__VIEWSTATE")[0].get("value")

    login_form_data = {
        "__LASTFOCUS": "",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewState,
        "__EVENTVALIDATION": eventValidation,
        "ctl00$ContentPlaceHolder1$Login1$UserName": username,
        "ctl00$ContentPlaceHolder1$Login1$Password": password,
        "ctl00$ContentPlaceHolder1$Login1$LoginButton": "Iniciar sesión",
    }

    documents_page = session.post(
        "https://documentos.otgir.com:444/default.aspx", data=login_form_data
    )
    documents_soup = BeautifulSoup(documents_page.content, "html.parser")

    table_body = documents_soup.find(
        "table", {"id": "ctl00_ContentPlaceHolder1_gvDescargas"}
    )
    data = []
    rows = table_body.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        link = "https://documentos.otgir.com:444/MemberPages/" + cols[0].find("a").get(
            "href"
        )
        name = cols[1].text.strip()
        date = datetime.strptime(cols[6].text.strip(), "%d/%m/%Y")
        data.append({"link": link, "name": name, "date": date})

    return data


def send_to_telegram(tg_chat_id, tg_token, filename, content):
    return requests.post(
        f"https://api.telegram.org/bot{tg_token}/sendDocument",
        data={"chat_id": tg_chat_id},
        files={"document": (filename, doc)},
    )


for each_user in config.USERS:
    nominas = get_nominas(each_user["USERNAME"], each_user["PASSWORD"])
    nomina = nominas[0]
    doc = session.get(nomina["link"]).content
    send_to_telegram(
        each_user["TELEGRAM_CHAT_ID"],
        config.TELEGRAM_TOKEN,
        nomina["name"] + ".pdf",
        doc,
    )
    credentials = service_account.Credentials.from_service_account_info(
        config.SERVICE_ACCOUNT
    )
    try:
        parsed_data = utils.parse_pdf(doc)
        utils.upload_to_spreadsheet(
            each_user["SPREADSHEET_ID"], nomina["name"], credentials, parsed_data
        )
    except Exception as e:
        print("Error parsing nomina")
        print(e)
