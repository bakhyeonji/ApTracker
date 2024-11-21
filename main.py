import re
import sys
import os
from get_wifi_dump import *
from get_geolocation import *
from visualize_location import *


def txt_to_csv(input_file):
    # txt to csv
    output_file = input_file.rsplit('.')[0] + '.csv'

    # read .txt line by line
    f1 = open(input_file, 'r', encoding='utf-8')
    lines = f1.readlines()

    # create csv file
    f2 = open(output_file, 'w', encoding='utf-8-sig')
    f2.write("time,SSID,BSSID,RSS\n")

    # process lines
    for line in lines:
        # preprocessing
        line = line.strip()
        line = re.sub(r'\([245.]+GHz\)', '', line)

        # wifi lists
        time, args = line.split(" - Networks filtered out due to low signal strength: ")
        args = args.split(" / ")

        # get arguments
        for arg in args:
            arg = arg.replace(' /', '')
            ssid, mac1, mac2, mac3, mac4, mac5, mac6 = arg.rsplit(':', 6)
            ssid = ssid.replace(',', '')
            mac6 = mac6.split('(')[0]
            rssi = arg.rsplit('-', 1)[1]

            # write csv file
            f2.write(f'{time},{ssid},{mac1}:{mac2}:{mac3}:{mac4}:{mac5}:{mac6},-{rssi}\n')

    f2.close()
    f1.close()

    return output_file


def main():
    # dump wifi ap log from smartphone
    WORKSPACE = input(f'[*] Please enter a workspace path (e.g., D:\\test): ')
    if not os.path.exists(WORKSPACE):
        os.makedirs(WORKSPACE)
        
    dump_file = input(f'[*] Please enter a name for the dump file to save (e.g., log.txt): ')
    dump_file_path = adb_dumpsys_wifi(WORKSPACE, dump_file)

    # convert to csv 
    output = txt_to_csv(dump_file_path)
    if not os.path.exists(output):
        print('[*] Cannot convert txt file to csv file.')
        sys.exit(1)
    print(f'[*] Completed! Check {output}')

    # get estimated positions
    check = input(f'[*] Do you want to get average positions? (Y/N): ').strip().lower()
    if check == 'y':
        geolocation_file = get_average_positions(output)
        if geolocation_file != None:
            print(f'[*] Completed! Check {geolocation_file}')
            
            # visualize
            check = input(f'[*] Do you want to visualize locations? (Y/N): ').strip().lower()
            if check == 'y':
                map_file = show_map(geolocation_file)
                print(f'[*] Completed! Check {map_file}')
        else:
            print('[*] Cannot get geolocations.')
    else:
        print('[*] good bye.')
        sys.exit(0)



if __name__ == '__main__':
    main()
else:
    sys.exit(1)