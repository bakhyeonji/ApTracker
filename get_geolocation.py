
import csv
import requests

"""
    Geolocation API는 위도/경도 좌표와 정확도 반경을 반환.
    JSON 구조화된 요청.

    # params of function 'geolocate'
    {
        "homeMobileCountryCode": (number),
        "homeMobileNetworkCode": (number),
        "radioType": (string),
        "carrier": (string),
        "considerIp: true,
        "cellTowers": [ # optional
            {
                "cellId": (number),             # 셀 고유 식별자
                "newRadioCellId": (number),     # NR(5G) 셀의 고유 식별자
                "locationAreaCode": (number),   # radioType 값이 gsm, cdma 일 겨우 필수사항
                "mobileCountryCode": (number),  # 휴대폰 기지국 모바일 국가 코드; radioType이 gsm, wcdma, lte, nr 일 경우 필수사항
                "mobileNetworkCode": (number),  # 휴대폰 기지국 모바일 네트뭐크 코드; 필수사항
            },
        ],
        "wifiAccessPoints":[ # more than 2
            {
                "macAddress": (string),         # BSSID; 필수
                "signalStrength": (number),     # RSSI; 항상 음수
                "age": (number),                # 이 액세스 지점이 감지된 이후의 밀리초 단위 시간
                "channel": (number),            # 클라이언트가 액세스 지점과 통신 중인 채널
                "signalToNoisRatio": (number)   # dB 단위로 측정된 전류 신호 대 잡음비
            },
        ]
    }
"""

def get_average_positions(input_file):

    REQUEST_URL = "https://www.googleapis.com/geolocation/v1/geolocate?key={API_key}"
    headers = {'Content-Type': 'application/json'}
    
    output_file = input_file.rsplit('.')[0] + '_geolocation.csv'
    output = open(output_file, "w", encoding='utf-8')
    output.write('time,lat,lng,accuracy\n')

    # request parameters
    data = {
        "considerIp": "false"
    }
    wifi_access_points = []                                

    # wifi ap 정보 분류
    with open(input_file, "r", encoding='utf-8') as f:
        csvReader = csv.reader(f, delimiter=',')
        prev_time = ''

        for row in csvReader:
            if row[0] == 'time':
                continue

            if prev_time == '':
                prev_time = row[0]
            
            if prev_time == row[0]:
                ap_data = dict()
                ap_data["macAddress"] = row[2]
                try:
                    ap_data["signalStrength"] = int(row[3])
                except ValueError:
                    continue
                wifi_access_points.append(ap_data)
                continue
            else:
                # request
                data["wifiAccessPoints"] = wifi_access_points
                rep = requests.post(REQUEST_URL, json=data, headers=headers)
                
                # error
                if rep.status_code != 200:
                    if rep.status_code == 400:
                        content = rep.json()
                        domain = content["error"]["errors"]["domain"]
                        if domain == 'global':
                            print(f'[*] {prev_time}: Parse Error')
                        else:
                            print(f'[*] {prev_time}: Invalid Key')
                    elif rep.status_code == 403:
                        print(f'[*] {prev_time}: Limit Exceeded')
                    elif rep.status_code == 404:
                        print(f'[*] {prev_time}: Not Found')
                    else:
                        print(f'[*] {prev_time}: Undefined Error')
                else:
                    content = rep.json()
                    lat = content["location"]["lat"]
                    lng = content["location"]["lng"]
                    acc = content["accuracy"]
                    output.write(f'{prev_time},{lat},{lng},{acc}\n')
                    print(f'{prev_time}: {lat}, {lng}, {acc}')

                # initialize
                wifi_access_points = []
                prev_time = row[0]
                ap_data['macAddress'] = row[2]
                ap_data['signalStrength'] = int(row[3])
                wifi_access_points.append(ap_data)

    # last row
    data["wifiAccessPoints"] = wifi_access_points
    rep = requests.post(REQUEST_URL, json=data, headers=headers)
    if rep.status_code != 200:
        print(f'{prev_time}: no response, {rep.status_code}')
    else:
        content = rep.json()
        lat = content["location"]["lat"]
        lng = content["location"]["lng"]
        acc = content["accuracy"]
        output.write(f'{prev_time},{lat},{lng},{acc}\n')
        print(f'{prev_time}: {lat}, {lng}, {acc}')

    output.close()
    return output_file