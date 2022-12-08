#!C:\Users\tdickens\OneDrive - Hydrogen Technology and Engineering Corporation\02_Models-Data\Web Scraping Data\WebScraper\venv\Scripts\python.exe
"""
Date: 2022-11-07
Author: Tyler Dickens
Description:
Program scrapes the H2 CA source to generate updated station timeseries data
"""

import requests
import pandas as pd
from requests_html import HTMLSession, AsyncHTMLSession
import asyncio
from datetime import datetime
import os

URL_CA = 'https://h2-ca.com/reports?id=2'

EUR_JSON_350_L = 'https://my.h2.live/ceemes/base.php?__type__=fuelstation&action=xmllist&__status_fueltype__=P350_LARGE&__language__=en&__transform__=json&__fieldsin__=idx,name,street,streetnr,zip,city,combinedstatuscombinedremark,has_350_large,has_350_small,has_700_small,image,opening_hours,latitude,longitude,operatorname,operatorlogo,hostname,operatorhotline,comments,news,date_commissioning_messageprogress_percent,progress_description,progress_extratext,countryshortname,funding,paymenttypespaymentinfo,price_message,activity_message,tec_recom_time,openinghours_nextchange_message&__t__=b13831e6243b9bcd4c74aeda55c1fe22'

EUR_JSON_350_S = 'https://my.h2.live/ceemes/base.php?__type__=fuelstation&action=xmllist&__status_fueltype__=P350_LARGE&__language__=en&__transform__=json&__fieldsin__=idx,name,street,streetnr,zip,city,combinedstatuscombinedremark,has_350_large,has_350_small,has_700_small,image,opening_hours,latitude,longitude,operatorname,operatorlogo,hostname,operatorhotline,comments,news,date_commissioning_messageprogress_percent,progress_description,progress_extratext,countryshortname,funding,paymenttypespaymentinfo,price_message,activity_message,tec_recom_time,openinghours_nextchange_message&__t__=b13831e6243b9bcd4c74aeda55c1fe22'

EUR_JSON_700 = 'https://my.h2.live/ceemes/base.php?__type__=fuelstation&action=xmllist&__status_fueltype__=P700_SMALL&__language__=en&__transform__=json&__fieldsin__=idx,name,street,streetnr,zip,city,combinedstatus,combinedremark,has_350_large,has_350_small,has_700_small,image,opening_hours,latitude,longitude,operatorname,operatorlogo,hostname,operatorhotline,comments,news,date_commissioning_message,progress_percent,progress_description,progress_extratext,countryshortname,funding,paymenttypes,paymentinfo,price_message,activity_message,tec_recom_time,openinghours_nextchange_message&__t__=b13831e6243b9bcd4c74aeda55c1fe22'

async def get_table():
    session = AsyncHTMLSession()
    r = await session.get(URL_CA)

    table = r.html.find('table')
    html = pd.read_html(table[2].html)
    df = html[0]
    df.iloc[0, 3] = 'Station Name'
    df.iloc[0, 6] = 'Status Alert'
    df.columns = df.iloc[0]
    df.drop(index=0, inplace=True)
    now = datetime.now().strftime("%Y-%m-%d_%H:%M")
    df['Datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    CA_XLSX = './webscrape_data/h2_ca.xlsx'

    if os.path.exists('./webscrape_data') and os.path.isfile(CA_XLSX):
        doc = pd.read_excel(CA_XLSX)

        with pd.ExcelWriter(CA_XLSX) as writer:
            new_doc = pd.concat([doc, df])
            new_doc.to_excel(writer, sheet_name='Data', index=False)

    else:
        os.mkdir('webscrape_data')
        df.to_excel(CA_XLSX, index=False)

    return r.status_code


def get_euro_stations():
    r_350_L = requests.get(EUR_JSON_350_L)
    r_350_S = requests.get(EUR_JSON_350_S)
    r_700 = requests.get(EUR_JSON_700)

    df_350_L = pd.DataFrame(r_350_L.json()['fuelstation'])
    df_350_S = pd.DataFrame(r_350_S.json()['fuelstation'])
    df_700 = pd.DataFrame(r_700.json()['fuelstation'])

    datetime.now().strftime('%Y-%m-%d %H:%M')

    for df in [df_350_L, df_350_S, df_700]:
        df['Datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    EUR_XLSX = './webscrape_data/h2_live_eur.xlsx'

    if os.path.exists('./webscrape_data') and os.path.isfile(EUR_XLSX):

        doc_350_S = pd.read_excel(EUR_XLSX, sheet_name='350 Small', )
        doc_350_L = pd.read_excel(EUR_XLSX, sheet_name='350 Large', )
        doc_700 = pd.read_excel(EUR_XLSX, sheet_name='700 Small', )

        with pd.ExcelWriter(EUR_XLSX) as writer:
            df_350_S = pd.concat([doc_350_S, df_350_S])
            df_350_S.to_excel(writer, sheet_name='350 Small', index=False)

            df_350_L = pd.concat([doc_350_L, df_350_L])
            df_350_L.to_excel(writer, sheet_name='350 Large', index=False)

            df_700 = pd.concat([doc_700, df_700])
            df_700.to_excel(writer, sheet_name='700 Small', index=False)

    else:
        with pd.ExcelWriter(EUR_XLSX) as writer:
            df_350_S.to_excel(writer, sheet_name='350 Small', index=False)
            df_350_L.to_excel(writer, sheet_name='350 Large', index=False)
            df_700.to_excel(writer, sheet_name='700 Small', index=False)

    return r_700.status_code


if __name__ == '__main__':
    print(f"H2 California Response Status Code: {asyncio.run(get_table())}")
    print(f"H2 Live Europe Response Status Code: {get_euro_stations()}")
