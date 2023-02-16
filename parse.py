# author: rand0m
# year:   2023
# wari

import pandas as pd
from pprint import pprint
from lxml import html
from pydantic import BaseModel


class Service(BaseModel):
    name: str
    count: int
    country: str


def filter_iot_services(services):

    iot_services = {"DrayTek Vigor Router", "MikroTik RouterOS API Service", "MikroTik", "Hikvision IP Camera", "DD-WRT milli_httpd", "KB Vision NVR", "Access Remote PC smtpd",
                    "Dahua DVR", "ZTE ZXHN H198A", "KB Vision XVR", "KB Vision DVR", "Avtech AVN801 network camera", "MikroTik bandwidth-test server", "ASUS Wireless Router RT-AX55"}
    iot_insecam_list = {"Axis cameras", "Axis2 cameras", "Axismkii cameras", "Blueiris cameras", "Bosch cameras", "Canon cameras", "Channelvision cameras", "Defeway cameras", "Dlink cameras", "Dlink-Dcs-932 cameras", "Foscam cameras", "Foscamipcam cameras", "Fullhan cameras", "Gk7205 cameras", "Hi3516 cameras", "Linksys cameras",
                        "Megapixel cameras", "Mobotix cameras", "Motion cameras", "Panasonic cameras", "Panasonichd cameras", "Sony cameras", "Sony-Cs3 cameras", "Stardot cameras", "Streamer cameras", "Sunellsecurity cameras", "Toshiba cameras", "Tplink cameras", "Vije cameras", "Vivotek cameras", "Webcamxp cameras", "Wificam cameras", "Wym cameras", "Yawcam cameras"}
    res = set()

    for service in services:
        for iot_service in iot_services:
            if iot_service in service:
                res.add(service)

        for iot_insecam in iot_insecam_list:
            if iot_insecam in service:
                res.add(service)

    return res


def parse_html(file):

    # Make a request to the webpage
    with open(file, 'r') as f:
        response = f.read()

    # Parse the HTML content
    tree = html.fromstring(response)

    # Use XPath to extract the text

    def get_total():
        total = int(tree.xpath(
            '/html/body/div[3]/div[3]/div/h6/span/text()')[0][len("Total: "):].replace(',', ''))
        return total

    total = get_total()

    # Use XPath to extract the text and create a table
    rows = []
    for i in range(1, total):
        strong_xpath = f'/html/body/div[3]/div[3]/div/div[2]/div[{i}]/div[1]/a/strong/text()'
        span_xpath = f'/html/body/div[3]/div[3]/div/div[2]/div[{i}]/div[2]/text()'
        try:
            row = [tree.xpath(strong_xpath)[0], int(
                tree.xpath(span_xpath)[0].strip().replace(',', ''))]
            rows.append(row)
        except:
            break

    # Create a table using pandas
    df = pd.DataFrame(rows, columns=['Title', 'Count'])
    return total, df


countries = ['jp', 'sg', 'kr', 'tw', 'my', 'th', 'vn', 'au']
d: [pd.DataFrame] = {}

for country in countries:
    cnt, df = parse_html(f'Files/facet_{country}.html')
    print(f'{country}: {cnt}')

    df.to_csv(f'{country}.csv', index=False)
    d[country] = df

# Path: main.py
curated_list_of_top_30_iot_services = set()
for cn in countries:
    df = pd.read_csv(f'{cn}.csv')
    a = set(df['Title'].to_list())
    curated_list_of_top_30_iot_services = curated_list_of_top_30_iot_services.union(
        a)


print('-----------')

results = filter_iot_services(curated_list_of_top_30_iot_services)

for device in results:
    for country in countries:
        df = pd.read_csv(f'{country}.csv')
        df = df[df['Title'] == device]
        if df.empty:
            continue
        s = Service(name=device, count=df['Count'].to_list()[
                    0], country=country)
        # print the service and print the percentage
        print(s)

# make a table (rows: services, columns: countries)
# store as pandas dataframe, save as csv

export_data = pd.DataFrame(columns=countries)
for service in results:
    row = []
    for country in countries:
        df = pd.read_csv(f'{country}.csv')
        df = df[df['Title'] == service]
        if df.empty:
            row.append(0)
        else:
            row.append(df['Count'].to_list()[0])
    export_data.loc[service] = row
print(export_data)
export_data.to_csv('export_data.csv', index=True)
