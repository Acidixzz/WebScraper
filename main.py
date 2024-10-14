from bs4 import BeautifulSoup
import requests
import csv

url = 'https://www.olympedia.org/'

years = {
    # 1870: "9009259",
    # 1896: "56026",
    # 1900: "56100",
    # 1904: "56146",
    # 1904: "925845",
    # 1906: "56238",
    # 1908: "56482",
    # 1912: "56829",
    # 1920: "57204",
    # 1924: "57490",
    # 1928: "57786",
    # 1932: "58045",
    # 1936: "58327",
    # 1948: "58659",
    # 1952: "59030",
    # 1956: "59415",
    # 1960: "59827",
    1964: "60258",
    1968: "60729",
    1972: "61226",
    1976: "61800",
    1980: "62367",
    1984: "62862",
    1988: "63505",
    1992: "64187",
    1996: "64866",
    2000: "65525",
    2004: "66205",
    2008: "257338",
    2012: "302423",
    2016: "358748",
    2020: "19000509"
}

csv_headers = ['Year', 'Athlete', 'NOC', 'Distance', 'Sex', 'Birth', 'Height (cm)', 'Weight (kg)']
csv_data = [csv_headers]

def is_num(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False

def result_parse(year):
    result_response = requests.get(url + 'results/' + years[year])

    if result_response.status_code == 200:
        # print(response.content)
        results = BeautifulSoup(result_response.content, 'html.parser')
        table = results.find(name='table', class_='table table-striped')
        row_indicies = {}
        header = table.find('thead').find_all('th')
        for i, col in enumerate(header):
            if col.text in csv_headers or col.text == 'Qualifying' or col.text == 'Final':
                row_indicies[col.text] = i
            if col.text == 'Competitor':
                row_indicies['Athlete'] = i

        print(row_indicies)
        rows = table.find_all('tr')
        for row in rows:
            print(f'next row for {year}...')
            data_row = [year]
            cols = row.find_all('td')
            if len(cols) == 0:
                continue
            data_row.append(cols[row_indicies['Athlete']].text)
            data_row.append(cols[row_indicies['NOC']].text)

            qual = cols[row_indicies['Qualifying']].text.split(' ')[0]
            final = cols[row_indicies['Final']].text.split(' ')[0]

            qual = float(qual) if is_num(qual) else 0
            final = float(final) if is_num(final) else 0
            distance = max(qual, final)
            if (distance == 0):
                continue
            data_row.append(distance)
            athlete_parse(cols[row_indicies['Athlete']].find('a')['href'], data_row)
    else: 
        print(f'Request exited with error {result_response.status_code}\n {result_response.content}')

def athlete_parse(link, data_row):
    athlete_response = requests.get(url+link)
    if athlete_response.status_code == 200:
        athlete = BeautifulSoup(athlete_response.content, 'html.parser')
        table = athlete.find(name='table', class_='biodata')
        bio_data = table.find_all('tr')
        for element in bio_data:
            if element.find('th').text == 'Sex':
                data_row.append(element.find('td').text)
            if element.find('th').text == 'Born':
                data_row.append(element.find('td').text)
            if element.find('th').text == 'Measurements':
                vals = element.find('td').text.split('/')

                height = vals[0].replace('cm', '').replace(' ', '')
                weight = vals[1].replace('kg', '').replace(' ', '')

                data_row.append(float(height))
                
                weight_range = weight.split('-')
                if len(weight_range) == 2:
                    weight = (float(weight_range[0])+float(weight_range[1]))/2
                data_row.append(float(weight))

        csv_data.append(data_row)
                

    else:
        print(f'Request exited with error {athlete_response.status_code}\n {athlete_response.content}')


for key in years.keys():
    result_parse(key)


print(csv_data)
with open('Olympic.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

