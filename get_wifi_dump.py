import sys
import os
import re
from ppadb.client import Client as AdbClient

def adb_dumpsys_wifi(workspace, file_name):
    try:
        # ADB 서버에 연결
        client = AdbClient(host="127.0.0.1", port=5037)     # Default is "127.0.0.1" and 5037
        devices = client.devices()

        if len(devices) == 0:
            print("[ERROR] There are no devices connected to the ADB.")
            sys.exit(1)

        # Select first device
        device = devices[0]
        print(f"Connected Device: {device}")

        # adb shell 명령 실행 (dumpsys wifi)
        output = device.shell("dumpsys wifi")
        filtered_lines = []
        pattern = re.compile(r".* - Networks filtered out due to low signal strength:.*")

        for line in output.splitlines():
            if pattern.match(line):
                filtered_lines.append(line)

        # 결과를 파일로 저장
        file_path = os.path.join(workspace, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(filtered_lines))

        return file_path

    except Exception as e:
        print(f"{e}")
        sys.exit(1)