import os
from datetime import datetime, timedelta
from http import HTTPStatus
import pandas as pd
import environ
import requests

ROOT_DIR = environ.Path(__file__) - 1
IMAGES_DIR = ROOT_DIR.path("rover_images")

env = environ.Env()
env.read_env(str(ROOT_DIR.path('.env')))


def collect_rover_data_from_api(date):
    response = requests.get(url=env('ENDPOINT'), params={
        "earth_date": date,
        "api_key": env('API_KEY')
    })
    if response.status_code == HTTPStatus.OK:
        data = response.json()
        return data.get('photos')
    else:
        return []


start_date = datetime(2024, 9, 1)
end_date = datetime(2024, 9, 30)
rover_data = list()

while start_date <= end_date:
    data_str = start_date.strftime("%Y-%m-%d")
    data = collect_rover_data_from_api(data_str)
    for item in data:
        rover_data.append({
            'photo_id': item['id'],
            'sol': item['sol'],
            'camera_id': item['camera']['id'],
            'camera_name': item['camera']['name'],
            'camera_full_name': item['camera']['full_name'],
            'img_src': item['img_src'],
            'earth_date': item['earth_date'],
            'rover_id': item['rover']['id'],
            'rover_name': item['rover']['name'],
            'rover_landing_date': item['rover']['landing_date'],
            'rover_launch_date': item['rover']['launch_date'],
            'rover_status': item['rover']['status'],
        })
    start_date += timedelta(days=1)

df = pd.DataFrame(rover_data)
df.to_csv('perseverance_data.csv', index=False)

for data in rover_data:
    data_directory = os.path.join(IMAGES_DIR, data['earth_date'])
    os.makedirs(data_directory, exist_ok=True)

    img_url = data.get('img_src')
    img_id = data.get('photo_id')
    img_name = os.path.join(str(data_directory), f"{img_id}.jpg")
    response = requests.get(img_url)
    if response.status_code == HTTPStatus.OK:
        with open(img_name, 'wb') as img_file:
            img_file.write(response.content)
    else:
        print("erro ao salvar imagem")