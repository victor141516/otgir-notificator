from apiclient import discovery
import tabula
import tempfile
import math

NAME = "Nómiasdasdsadna Agosto de 2019"


def parse_pdf(content):
    f = tempfile.NamedTemporaryFile()
    f.write(content)
    raw_data = tabula.read_pdf(f.name, multiple_tables=True)[1]
    clean_data = raw_data.drop(1, 1).drop(index=1, axis=1)
    clean_data.columns = clean_data.iloc[0]
    clean_data = clean_data.drop(clean_data.index[0])
    clean_data["DÍAS / HORAS"] = [
        x.replace(".", "").replace(",", ".") if type(x) is str else x
        for x in clean_data["DÍAS / HORAS"]
    ]
    clean_data["IMP. PARCIAL."] = [
        x.replace(".", "").replace(",", ".") if type(x) is str else x
        for x in clean_data["IMP. PARCIAL."]
    ]
    clean_data["T O T A L E S"] = [
        x.replace(".", "").replace(",", ".") if type(x) is str else x
        for x in clean_data["T O T A L E S"]
    ]
    clean_data["DÍAS / HORAS"].astype(float)
    clean_data["IMP. PARCIAL."].astype(float)
    clean_data["T O T A L E S"].astype(float)

    for row in clean_data.iterrows():
        if type(row[1][0]) is float and math.isnan(row[1][0]):
            clean_data = clean_data.drop(row[0])

    data_list = [clean_data.columns.to_list()]
    for row in clean_data.iterrows():
        data_list.append(
            [
                "" if (type(e) is float and math.isnan(e)) else e
                for e in row[1].to_list()
            ]
        )

    return data_list


def upload_to_spreadsheet(spreadhsheet_id, sheet_name, credentials, data):
    service = discovery.build("sheets", "v4", credentials=credentials)

    add_sheet_params = {
        "spreadsheetId": spreadhsheet_id,
        "body": {
            "requests": [
                {"addSheet": {"properties": {"title": sheet_name, "index": 0,}}}
            ],
            "includeSpreadsheetInResponse": False,
        },
    }

    try:
        new_sheet_add = service.spreadsheets().batchUpdate(**add_sheet_params).execute()
    except Exception:
        pass

    service.spreadsheets().values().update(
        spreadsheetId=spreadhsheet_id,
        range="A1",
        body={"values": data},
        valueInputOption="RAW",
    ).execute()
