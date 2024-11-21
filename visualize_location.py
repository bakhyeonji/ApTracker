import sys
import csv
import folium
from datetime import datetime, timedelta


def _get_avg_points(input_file):
    lat_sum = 0
    lng_sum = 0
    count = 0

    # csv 파일 읽기
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat_sum += float(row['lat'])
            lng_sum += float(row['lng'])
            count += 1
    
    # 평균값 계산
    avg_lat = lat_sum / count if count > 0 else 0
    avg_lng = lng_sum / count if count > 0 else 0

    return avg_lat, avg_lng


def show_map(input_file):
    # get average location
    avg_lat, avg_lng = _get_avg_points(input_file)
    if avg_lat == 0 or avg_lng == 0:
        print(f'Error! {input_file} is empty!')
        sys.exit(1)

    # create a map
    m = folium.Map(location=[avg_lat, avg_lng], tiles='CartoDB Positron No Labels', zoom_start=17)

    # locations for the polyline
    locations = []
    accuracy_threshold = 50

    # get locations and add special markers for start, end and turning points
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        last_time = None
        marker_number = 1

        for idx, row in enumerate(rows):
            time = row['time']
            lat = float(row['lat'])
            lng = float(row['lng'])
            accuracy = float(row['accuracy'])

            # remove inaccuate value
            if idx != len(rows) -1 and accuracy >= accuracy_threshold:
                continue

            current_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')

            # Start marker (green)
            if idx == 0:
                folium.Marker(location=[lat, lng], popup='Start: '+time, icon=folium.Icon(color='green')).add_to(m)
                last_time = current_time

            # End marker (red)
            elif idx == len(rows) - 1:
                folium.Marker(location=[lat, lng], popup='End: '+time, icon=folium.Icon(color='red')).add_to(m)

            else:
                if last_time is None or current_time >= last_time + timedelta(minutes=2):
                    # marker
                    folium.Marker(
                        location=[lat, lng],
                        tooltip=f"{marker_number}: {time}",
                        icon=folium.DivIcon(
                            html=f"""
                            <div style="position: relative; text-align: center;">
                                <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png"
                                style="width: 25px; height: 41px;">
                                <div style="position: absolute; top: 14px; left: 6px; width: 100%; font-size: 15px; font-weight: bold; color: black;">{marker_number}</div>
                            </div>
                            """)
                    ).add_to(m)

                    last_time = current_time
                    marker_number += 1

            locations.append([lat, lng])

    # add a polyline to connet the markers
    folium.PolyLine(locations, color="blue", weight=2.5, opacity=1).add_to(m)

    # save map as html
    file_name = input_file.rsplit('.', 1)[0] + '.html'
    m.save(file_name)

    return file_name