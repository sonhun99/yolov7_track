import re
import pandas as pd
import os
import argparse


def process_all(input_dir):
    # 입력 디렉토리 내의 모든 srt 파일을 가져옴
    srt_files = [
        os.path.join(input_dir, file)
        for file in os.listdir(input_dir)
        if file.endswith(".srt")
    ]

    for srt_file in srt_files:
        process_srt_to_csv(srt_file)


def process_srt_to_csv(input_file):
    # 입력 파일 이름에서 확장자를 제외한 부분을 가져옴
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # 출력 파일의 경로와 이름을 생성
    output_file = os.path.join("srt_converted", f"{base_name}.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

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
# process_srt_to_csv("DJI_0051.srt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert SRT to CSV")
    parser.add_argument("input", help="Input SRT file path")

    args = parser.parse_args()

    srt_input = args.input
    # 파일인지 디렉토리인지 확인하고 처리
    if os.path.isfile(srt_input):
        process_srt_to_csv(srt_input)
    elif os.path.isdir(srt_input):
        process_all(srt_input)
    else:
        print("Invalid input")
