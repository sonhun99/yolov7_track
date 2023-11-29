import os
import pandas as pd
import re
from natsort import natsorted
import argparse


def post_process(
    save_dir,
    original_file_path,
    flight_info_id,
    data_no,
    vid_stride,
    class_dict_path="class_dictionary.csv",
):
    file_name = os.path.basename(original_file_path)
    txt_path = os.path.join(save_dir, os.path.splitext(file_name)[0] + ".txt")

    with open(txt_path, "w") as f:
        f.write(str(flight_info_id) + ", " + str(data_no) + "\n")

    # Read class dictionary
    class_df = pd.read_csv(class_dict_path)
    class_dict = (
        class_df[["yolo_class_no", "1st_category", "2nd_category", "3rd_category"]]
        .set_index("yolo_class_no")
        .apply(tuple, axis=1)
        .to_dict()
    )

    # Read converted srt file
    srt_path = os.path.splitext(original_file_path)[0] + ".csv"
    srt_df = pd.read_csv(srt_path)

    label_dir = os.path.join(save_dir, "labels")
    label_list = [
        file
        for file in os.listdir(label_dir)
        if re.search(r"^" + os.path.splitext(file_name)[0] + r"_(\d+)\.txt$", file)
    ]

    final_content = pd.DataFrame()
    for file in natsorted(label_list):
        # Read each file
        raw_content = pd.read_csv(os.path.join(label_dir, file), header=None, sep=" ")
        raw_content = raw_content[::-1].reset_index(drop=True)
        raw_content.columns = [
            "object_id",
            "class_id",
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "xcenter",
            "ycenter",
        ]

        # Find frame number
        FrameCnt = vid_stride * (int(re.search(r"(\d+)\.txt$", file).group(1)) - 1) + 1

        # Find "DateTime" from "FrameCnt" in srt_df
        DateTime = srt_df[srt_df["FrameCnt"] == FrameCnt]["DateTime"].values[0]

        # Create content for each frame
        content = raw_content.copy()

        # Add FrameCnt and DateTime
        content["FrameCnt"] = FrameCnt
        content["DateTime"] = DateTime

        # Add "1st_category", "2nd_category", "3rd_category" from "class_id"
        content[["1st_category", "2nd_category", "3rd_category"]] = pd.DataFrame(
            content["class_id"].map(class_dict).tolist(), index=content.index
        )

        # drop xcenter, ycenter, class_id
        content = content.drop(["xcenter", "ycenter", "class_id"], axis=1)

        content = content[
            [
                "FrameCnt",
                "object_id",
                "1st_category",
                "2nd_category",
                "3rd_category",
                "DateTime",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
            ]
        ]

        final_content = pd.concat([final_content, content], axis=0, ignore_index=True)

    final_content.reset_index(drop=True, inplace=True)
    final_content.index += 1
    final_content["bbox"] = (
        final_content["xmin"].astype(str)
        + " "
        + final_content["ymin"].astype(str)
        + " "
        + final_content["xmax"].astype(str)
        + " "
        + final_content["ymax"].astype(str)
    )
    final_content = final_content[
        [
            "FrameCnt",
            "object_id",
            "1st_category",
            "2nd_category",
            "3rd_category",
            "DateTime",
            "bbox",
        ]
    ]

    # Convert final_content to string
    content_txt = final_content.to_csv(index=True, header=False)
    content_txt = re.sub(r",", ", ", content_txt)

    # erase all \r in content_txt
    content_txt = re.sub(r"\r", "", content_txt)

    # Write content to txt file
    with open(txt_path, "a") as f:
        f.write(content_txt + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process detected objects")
    parser.add_argument(
        "--save_dir",
        type=str,
        default="",
        help="Directory where the result is saved",
    )
    parser.add_argument(
        "--original_file_path",
        type=str,
        default="",
        help="Path to the original file",
    )
    parser.add_argument(
        "--flight_info_id",
        type=str,
        default="no_id",
        help="Flight info id",
    )
    parser.add_argument(
        "--data_no",
        type=int,
        default=0,
        help="Data number",
    )
    parser.add_argument(
        "--vid_stride",
        type=int,
        default=4,
        help="Video stride",
    )
    parser.add_argument(
        "--class_dict_path",
        type=str,
        default="class_dictionary.csv",
        help="Path to the class dictionary",
    )

    args = parser.parse_args()

    post_process(
        args.save_dir,
        args.original_file_path,
        args.flight_info_id,
        args.data_no,
        args.vid_stride,
        args.class_dict_path,
    )
