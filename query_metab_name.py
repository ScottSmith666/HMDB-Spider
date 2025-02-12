import requests as req
import pandas as pd
from io import StringIO
import os
import traceback
import time
import warnings

import gen_all_metab_names
import query_means_by_html

BASE_PATH = os.path.abspath("")  # 该项目的根目录
PATH_SEP = os.sep  # 不同操作系统的路径分隔符不同，调用系统方法以便于跨平台
QUERY_URL = "https://hmdb.ca/spectra/ms/generate_csv.csv"  # HMDB导出csv的接口，传入指定的一系列参数可导出指定内容

DEBUG = False

if not DEBUG:
    warnings.filterwarnings('ignore')

# proxies = {
#     "https": "127.0.0.1:17890",
#     "http": "127.0.0.1:17890",
# }

def query(meta_id, url, mzmed, pn, path, sum, now, adduct_type, tolerance_value, unit):
    print("正在爬取代谢峰ID为%s，Ion Mode为%s，Adduct Type为%s，Tolerance为%s %s，质荷比为%s的可能代谢物（第%d个，共%d个）..." % (str(meta_id), pn, adduct_type, tolerance_value, unit, mzmed, now, sum))

    headers = {
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
    
    params = {
        "results[action]": "search",
        "results[adduct_type][]": adduct_type,
        "results[commit]": "Search",
        "results[controller]": "specdb/ms",
        "results[ms_search_ion_mode]": pn,
        "results[query_masses]": str(mzmed),
        "results[tolerance]": tolerance_value,
        "results[tolerance_units]": unit,
        "results[utf8]": "✓",
    }

    if not os.path.exists("%s%sMETAID_%s_MAYBE_NAMES.csv" % (path, PATH_SEP, str(meta_id))):
        csv_content = req.request("GET", url, headers=headers, params=params)  # 如果速度慢就加上proxies=proxies参数
        if csv_content.status_code / 100 < 4:  # response错误码为4或5开头时表示请求错误
            exp_df = pd.read_csv(StringIO(csv_content.text))
            if len(exp_df) != 0:
                exp_df.to_csv("%s%sMETAID_%s_MAYBE_NAMES.csv" % (path, PATH_SEP, str(meta_id)), index=False)
                print("数据爬取并写入完成...")
            else:
                print("查询成功，但无查询结果...")
            return csv_content.status_code
        else:
            print("爬取错误，错误代码%d..." % csv_content.status_code)
            return csv_content.status_code
    else:
        print("METAID_%s_MAYBE_NAMES.csv已存在，正在跳过..." % str(meta_id))
        return 0

if __name__ == "__main__":
    print("Welcome to use HMDB Spider!\nDeveloped by Scott Smith\n如果对您有帮助的话，可以请我一杯咖啡哦~")
    # 遍历多个文件查找代谢峰对应代谢物信息
    for origin_file_name in os.listdir("%s%sorigin_read_data" % (BASE_PATH, PATH_SEP)):
        with open("%s%serror.csv" % (BASE_PATH, PATH_SEP), "a") as e:  # 爬取错误的代谢峰信息写入“error.csv”中
            e.write("id,polar,mz,addt,tor,unit,solved\n")
            print("正在处理%s..." % origin_file_name)
            if not os.path.exists("%s%snames%s%s" % (BASE_PATH, PATH_SEP, PATH_SEP, origin_file_name)):
                os.mkdir("%s%snames%s%s" % (BASE_PATH, PATH_SEP, PATH_SEP, origin_file_name))
            source_ms_value_table = pd.read_csv("%s%sorigin_read_data%s%s" % (BASE_PATH, PATH_SEP, PATH_SEP, origin_file_name))[["id", "polar", "mz", "addt", "tor", "unit"]]

            b = 1
            for index, item in source_ms_value_table.iterrows():  # 按行遍历代谢峰表
                try:
                    status_code = query(item["id"], QUERY_URL, item["mz"], item["polar"], 
                                        "%s%snames%s%s" % (BASE_PATH, PATH_SEP, PATH_SEP, origin_file_name), len(source_ms_value_table), b, item["addt"], str(item["tor"]), item["unit"])
                    if status_code / 100 >= 4:
                        e.write("%s,%s,%s,%s,%s,%s,%d\n" % (str(item["id"]), item["polar"], item["mz"], item["addt"], str(item["tor"]), item["unit"], 0))
                except:
                    print("发生了未知错误...")
                    e.write("%s,%s,%s,%s,%s,%s,%d\n" % (str(item["id"]), item["polar"], item["mz"], item["addt"], str(item["tor"]), item["unit"], 0))
                    if DEBUG:
                        print(traceback.format_exc())
                b += 1
        time.sleep(0.1)  # 防止请求过快

        print("%s处理完成，正在检查错误..." % origin_file_name)

        error_df = pd.read_csv("%s%serror.csv" % (BASE_PATH, PATH_SEP))

        if len(error_df) == 0:
            print("所有代谢峰爬取成功，未发现错误...")
        else:
            print("发现错误！有%d条代谢峰爬取未成功，列出如下..." % len(error_df))
            print(error_df)
        
        while True:
            en = 1
            for err_index, err_item in error_df.iterrows():
                if error_df.iloc[err_index, 6] == 0:
                    try:
                        status_code = query(err_item["id"], QUERY_URL, err_item["mz"], err_item["polar"], 
                                            "%s%snames%s%s" % (BASE_PATH, PATH_SEP, PATH_SEP, origin_file_name), len(error_df), en, item["addt"], str(item["tor"]), item["unit"])
                        if status_code / 100 < 4:  # 错误的代谢峰爬取成功了
                            error_df.iloc[err_index, 6] = 1  # 将solved改成1，表示已解决这条错误
                    except:
                        print("发生了未知错误...")
                        if DEBUG:
                            print(traceback.format_exc())
                en += 1

            if 0 not in error_df["solved"].tolist():
                print("所有错误均已解决...")
                break

            time.sleep(1)  # 防止请求过快
        
        # 删除error.txt
        os.remove("%s%serror.csv" % (BASE_PATH, PATH_SEP))
        
        gen_all_metab_names.merge(BASE_PATH, origin_file_name)

    query_means_by_html.query_translate_means("%s%s%s" % (BASE_PATH, PATH_SEP, "out"))
