import os
import pandas as pd
import re
from natsort import natsorted
import argparse


def post_process(save_path, output_dir, srt_path):
    # First line of the file
    flight_info_id = "flight_info_id"
    data_no = "data_no"

    with open(save_path + ".txt", "w") as f:
        f.write(str(flight_info_id) + ", " + str(data_no) + "\n")

    # Other lines of the file

    # Read class dictionary
    class_df = pd.read_csv("class_dictionary.csv")
    class_dict = (
        class_df[["yolo_class_no", "1st_category", "2nd_category", "3rd_category"]]
        .set_index("yolo_class_no")
        .apply(tuple, axis=1)
        .to_dict()
    )

    # Read converted srt file
    srt_df = pd.read_csv(srt_path)

    label_dir = os.path.join(output_dir, "labels")

    final_content = pd.DataFrame()
    for file in natsorted(os.listdir(label_dir)):
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
        FrameCnt = int(re.search(r"(\d+)\.txt$", file).group(1))

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

    # Convert final_content to string
    content_txt = final_content.to_string(
        index=True, header=False, index_names=False, justify="left"
    )

    # Write content to txt file
    with open(save_path + ".txt", "a") as f:
        f.write(content_txt + "\n")


# post_process("runs\detect\object_tracking3\DJI_0051", "runs\detect\object_tracking3", "DJI_0051.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process detected objects")
    parser.add_argument("save_path", help="Save path for output file")
    parser.add_argument("output_dir", help="Directory containing label files")
    parser.add_argument("srt_path", help="Path to SRT file")

    args = parser.parse_args()

    save_path = args.save_path
    output_dir = args.output_dir
    srt_path = args.srt_path

    post_process(save_path, output_dir, srt_path)
