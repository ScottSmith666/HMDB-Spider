import os
import time
import pandas as pd
import traceback
import requests as req
from deep_translator import GoogleTranslator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import warnings

DEBUG = True

if not DEBUG:
    warnings.filterwarnings('ignore')

BASE_PATH = os.path.abspath("")
PATH_SEP = os.sep

session = req.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

PROXIES = {  # 谷歌翻译被墙，需要挂代理
    "https": "127.0.0.1:17890",
    "http": "127.0.0.1:17890",
}

HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "hmdb.ca",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
    }

PATH_SEP = os.sep

def tsl(source, target, content):
    '''翻译函数'''

    # 字数不超过5000字
    source_list = source.split(" ")
    if len(source_list) >= 5000:
        source = " ".join(source_list[:4900])

    try:
        if content == None:
            return "内容为空..."
        else:
            return GoogleTranslator(source=source, target=target, proxies=PROXIES).translate(content)
    except:
        if DEBUG:
            print(traceback.format_exc())
        return "翻译出错"

def query_translate_means(after_merge_data_path, file_name):
    print("现在开始代谢物含义的爬取...")
    print("正在处理%s..." % file_name)

    data = pd.read_csv("%s%s%s" % (after_merge_data_path, PATH_SEP, file_name))

    num = 1
    for index, item in data.iterrows():
        try:
            hmdb_id = item["compound_id"]
            if item["means_chs"] == "FETCH ERROR" or item["means_chs"] == "翻译出错" or item["means_chs"] == "" \
                or item["means_chs"] == None or item["means"] == "" or item["means"] == None or pd.isna(item["means_chs"]) or pd.isna(item["means"]):
                print("正在爬取https://hmdb.ca/metabolites/%s（第%d个，共%d个）..." % (hmdb_id, num, len(data)))

                hm = session.get("https://hmdb.ca/metabolites/%s" % hmdb_id, headers=HEADERS, proxies=PROXIES).text  # 如果速度慢就加上proxies=PROXIES参数
                soup = BeautifulSoup(hm, 'html.parser')
                    
                tag = soup.find_all("td", attrs={"class": "met-desc"})

                class_tag = soup.find_all("a", attrs={"class": "classyfire-taxnode wishart-link-out"})
                    
                print("正在写入class...")
                if len(class_tag) != 0:
                    for class_col in range(13, 17 + 1):  # 写入kingdom、SuperClass、Class、SubClass、DirectParent
                        data.iloc[index, class_col] = class_tag[class_col - 13].text
                else:
                    for class_col in range(13, 17 + 1):
                        data.iloc[index, class_col] = "无分类"

                print("正在翻译代谢物：%s..." % hmdb_id)
                if DEBUG:
                    print(hm)
                    print(soup)
                    print(class_tag)
                    print(tag)
                source_content = tag[0].text
                translated_content = tsl("en", "zh-CN", source_content)
                # 写入原文
                data.iloc[index, 11] = source_content
                # 写入译文
                data.iloc[index, 12] = translated_content
                print("翻译完成...")
            else:
                print("%s已翻译..." % hmdb_id)
        except:
            # 写入原文
            data.iloc[index, 11] = "FETCH ERROR"
            # 写入译文
            data.iloc[index, 12] = "FETCH ERROR"
            print("发生了未知错误...")
            if DEBUG:
                print(traceback.format_exc())
        num += 1
    
        # 保存文件
        data.to_csv("%s%s%s" % (after_merge_data_path, PATH_SEP, file_name), index=False, mode="w")
    print("%s保存成功..." % file_name)

    

def run(after_merge_data_path):
    for file_name in os.listdir(after_merge_data_path):
        query_translate_means(after_merge_data_path, file_name)
        # 检查错误
        print("代谢物含义初步抓取完成，正在检查错误...")
        while True:
            data = pd.read_csv("%s%s%s" % (after_merge_data_path, PATH_SEP, file_name))
            error_num = len(data[data["means_chs"] == "FETCH ERROR"])
            print("检查出%d条错误，正在处理..." % error_num)
            if error_num != 0:
                query_translate_means(after_merge_data_path, file_name)
            else:
                print("错误处理完成...")
                break
            time.sleep(1)
    
    print("所有步骤均已完成，exiting...")


if __name__ == "__main__":
    run(("%s%sout" % (BASE_PATH, os.sep)))
