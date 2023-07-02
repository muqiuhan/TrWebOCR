import requests
import os
import sys
import re

URL = "http://localhost:8089/api/tr-run/"
SCREENSHOT_DIR_PATH = sys.argv[1]
OUTPUT_FILE = sys.argv[2]


def get_screenshot_dir_file_list(screenshot_dir_path: str) -> list[str]:
    """获取会议聊天记录截图目录中的所有图片文件

    Args:
        img_file_dir (str): 聊天记录的目录路径

    Returns:
        list[str]: 所有聊天记录的截图
    """
    return sorted(
        # 由于截图文件名一般带有截图日期，所以在这里做一次排序，保证进行识别的的顺序合理
        [
            img_file
            for img_file in os.listdir(screenshot_dir_path)
            if os.path.isfile(os.path.join(screenshot_dir_path, img_file))
            and img_file.split(".")[-1] in ["jpg", "png", "jpeg"]
        ]
    )


def request_TrWebOCR(img_file_path: str) -> list[str]:
    """调用TrWebOCR识别一张截图文件并获取有效的返回结果

    Args:
        img_file_path (str): 截图文件的路径

    Returns:
        list[str]: TrWebOCR的返回结果有如下形式：
            {"code": 200,
             "msg": "\u6210\u529f",
             "data": {
                "img_detected": "data:image/jpeg;base64,/9j/4AAQSkZJR5t...",
                "raw_out": [[[11, 13, 402, 36], "\u753b\u51fa\u6587\u5b57\u533a\u57df\u7684\u56fe\u7247base64\u503c", 0.9999545514583588], [[11, 112, 215, 36], "\u8bc6\u522b\u7ed3\u679c\u7684\u8f93\u51fa", 0.999962397984096], [[11, 171, 158, 36], "\u8bc6\u522b\u7684\u8017\u65f6", 0.999971580505371]],
                "speed_time": 0.67}}
        而我们只需要raw_out的第一项， 即识别的文字结果
    """
    raws = []

    try:
        raw_outs = requests.post(
            url=URL, data={"compress": 1600}, files={"file": open(img_file_path, "rb")}
        ).json()["data"]["raw_out"]

        for raw in raw_outs:
            raws.append(raw[1])

        return raws

    except KeyError:
        print(f"截图{img_file_path}识别失败，重试...")
        request_TrWebOCR(img_file_path)


def ocr(img_file_paths: list[str]) -> list[str]:
    """对图片列表批量调用`request_TrWebOCR`并返回对应结果

    Args:
        img_file_paths (list[str]): 所有截图文件的路径

    Returns:
        list[str]: 经过处理的有效TrWebOCR返回结果
    """
    result = []

    for img_file_path in img_file_paths:
        result.append(request_TrWebOCR(img_file_path))

    return result[0]


class Filter:
    """对OCR的结果进行微调"""
    
    @staticmethod
    def __is_time_info(history: str) -> bool:
        matched = re.search(r"\d{2}:\d{2}", history)
        if matched and matched.group() == history:
            return True
        else:
            return False

    @staticmethod
    def __merge_independ_time_info(chat_history: list[str]) -> list[str]:
        """合并聊天记录中单独出现的时间信息"""
        merged_strings = []
        previous_string = ""

        for history in chat_history:
            if Filter.__is_time_info(history):
                previous_string = f"{previous_string}{history}"
            else:
                merged_strings.append(previous_string)
                previous_string = history

        merged_strings.append(previous_string)
        return merged_strings

    @staticmethod
    def __remove_empty(chat_history: list[str]) -> list[str]:
        """删除聊天记录中的空白记录"""
        return list(filter(lambda history: history, chat_history))

    @staticmethod
    def __add_new_line(chat_history: list[str]) -> list[str]:
        """向每一条聊天记录末尾添加换行符"""
        return list(map(lambda history: f"{history}\n", chat_history))

    @staticmethod
    def __normalize_speaker_info(chat_history: list[str]) -> list[str]:
        def replace(history: str) -> str:
            matched = re.search(r"\d{2}:\d{2}", history)
            if matched:
                return f"o- {history[(matched.start()):]} {history[:(matched.start())]}"
            else:
                return f"| {history}"

        return list(map(replace, chat_history))

    @staticmethod
    def filter(strings: list[str]) -> list[str]:
        return Filter.__add_new_line(
            Filter.__normalize_speaker_info(
                Filter.__merge_independ_time_info(Filter.__remove_empty(strings))
            )
        )


if __name__ == "__main__":
    with open(OUTPUT_FILE, "w") as output:
        output.writelines(
            Filter.filter(ocr(get_screenshot_dir_file_list(SCREENSHOT_DIR_PATH)))
        )
