import requests
import os
import sys

URL = "http://localhost:8089/api/tr-run/"
SCREENSHOT_DIR_PATH = sys.argv[1]


def get_screenshot_dir_file_list(screenshot_dir_path: str) -> list[str]:
    """获取会议聊天记录截图目录中的所有图片文件

    Args:
        img_file_dir (str): 聊天记录的目录路径

    Returns:
        list[str]: 所有聊天记录的截图
    """
    return [
        img_file
        for img_file in os.listdir(screenshot_dir_path)
        if os.path.isfile(os.path.join(screenshot_dir_path, img_file))
        and img_file.split(".")[-1] in ["jpg", "png", "jpeg"]
    ]


def request_TrWebOCR(img_file_path: str) -> str:
    """调用TrWebOCR识别一张截图文件并获取有效的返回结果

    Args:
        img_file_path (str): 截图文件的路径

    Returns:
        str: TrWebOCR的返回结果有如下形式：
            {"code": 200,
             "msg": "\u6210\u529f",
             "data": {
                "img_detected": "data:image/jpeg;base64,/9j/4AAQSkZJR5t...",
                "raw_out": [[[11, 13, 402, 36], "\u753b\u51fa\u6587\u5b57\u533a\u57df\u7684\u56fe\u7247base64\u503c", 0.9999545514583588], [[11, 112, 215, 36], "\u8bc6\u522b\u7ed3\u679c\u7684\u8f93\u51fa", 0.999962397984096], [[11, 171, 158, 36], "\u8bc6\u522b\u7684\u8017\u65f6", 0.999971580505371]],
                "speed_time": 0.67}}
        而我们只需要raw_out的第一项， 即识别的文字结果
    """
    try:
        return requests.post(
            url=URL, data={"compress": 1600}, files={"file": open(img_file_path, "rb")}
        ).json()["data"]["raw_out"][1]
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

    return result


if __name__ == "__main__":
    print(ocr(get_screenshot_dir_file_list(SCREENSHOT_DIR_PATH)))
