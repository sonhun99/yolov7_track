import re
import pandas as pd
import os


def process_srt_to_csv(input_file):
    # 입력 파일 이름에서 확장자를 제외한 부분을 가져옴
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # 출력 파일의 경로와 이름을 생성
    output_file = f"{base_name}.csv"

    with open(input_file, "r") as file:
        text = file.read()

    # 데이터 추출을 위한 정규 표현식
    pattern = r"(\d+)\n(.*?) --> (.*?)\n.*?FrameCnt: (\d+), DiffTime: (\d+)ms\n(.*?)\n\[iso: (\d+)\] \[shutter: ([\d\/.]+)\] \[fnum: ([\d.]+)\] \[ev: (-?\d+)\] \[ct: (\d+)\] \[color_md : (\w+)] \[focal_len: ([\d.]+)\] \[latitude: ([\d.]+)\] \[longitude: ([\d.]+)\] \[rel_alt: ([\d.]+) abs_alt: ([-\d.]+)\]"

    # 정규 표현식을 통해 데이터 추출
    matches = re.findall(pattern, text, re.DOTALL)

    # 추출된 데이터를 DataFrame으로 변환
    data = []
    for match in matches:
        (
            index,
            start_time,
            end_time,
            frame_cnt,
            diff_time,
            date_time,
            iso,
            shutter,
            fnum,
            ev,
            ct,
            color_md,
            focal_len,
            latitude,
            longitude,
            rel_alt,
            abs_alt,
        ) = match
        data.append(
            [
                int(index),
                start_time,
                end_time,
                int(frame_cnt),
                int(diff_time),
                pd.to_datetime(date_time),
                int(iso),
                str(shutter),
                float(fnum),
                int(ev),
                int(ct),
                color_md,
                float(focal_len),
                float(latitude),
                float(longitude),
                float(rel_alt),
                float(abs_alt),
            ]
        )

    df = pd.DataFrame(
        data,
        columns=[
            "Index",
            "StartTime",
            "EndTime",
            "FrameCnt",
            "DiffTime",
            "DateTime",
            "iso",
            "shutter",
            "fnum",
            "ev",
            "ct",
            "color_md",
            "focal_len",
            "latitude",
            "longitude",
            "rel_alt",
            "abs_alt",
        ],
    )

    df.to_csv(output_file, index=False)


# 함수 호출 (예시)
process_srt_to_csv("DJI_0051.srt")
