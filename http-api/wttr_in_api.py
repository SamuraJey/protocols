import requests

inputCity = str(input('Enter city name or zip-code or airport code (SVX): '))
if inputCity == '':
    inputCity = 'Екатеринбург'
response = requests.get(f'http://wttr.in/{inputCity}?format=j1')
data = None

if response.status_code == 200:

    data = response.json()
else:
    print(f'Request failed with status code {response.status_code}')

if data != None:
    areaName = data['nearest_area'][0]['areaName'][0]['value']
    country = data['nearest_area'][0]['country'][0]['value']
    print(f'Weather forecast in {areaName}, {country} for 3 days:')
    for i in range(0, 3):
        date = data['weather'][i]['date']
        maxTemp = data['weather'][i]['maxtempC']
        minTemp = data['weather'][i]['mintempC']
        avgTemp = data['weather'][i]['avgtempC']
        windSpeed = data['weather'][i]['hourly'][0]['windspeedKmph']
        weatherDesc = data['weather'][i]['hourly'][0]['weatherDesc'][0]['value']
        averageWindSpeed = 0
        averagePressure = 0
        for j in range(0, 8):
            averageWindSpeed += int(data['weather']
                                    [i]['hourly'][j]['windspeedKmph'])
            averagePressure += int(data['weather'][i]['hourly'][j]['pressure'])
        averageWindSpeed = averageWindSpeed/8
        averagePressure = averagePressure/8

        print(f'{date}: Condition {weatherDesc}, Max/Min: {maxTemp}°C/{minTemp}°C, avg {avgTemp}°C, Average wind speed: {averageWindSpeed:.2f} km/h, Average pressure: {averagePressure:.2f} mm Hg')
