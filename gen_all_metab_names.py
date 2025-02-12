import os
import pandas as pd


def merge(path, origin_filename):
    PATH_SEP = os.sep

    all_csv_head = ["metab_num_id", "query_mass", "compound_id", "compound_name", "formula", "monoisotopic_mass", "adduct", "adduct_type", "adduct_m/z", "delta(ppm),", "ccs_value"]
    all_df = pd.DataFrame(columns=all_csv_head)

    for i in os.listdir("%s%s%s%s%s" % (path, PATH_SEP, "names", PATH_SEP, origin_filename)):
        m_df = pd.read_csv("%s%s%s%s%s%s%s" % (path, PATH_SEP, "names", PATH_SEP, origin_filename, PATH_SEP, i))
        m_df["metab_num_id"] = i.split("_")[1]
        all_df = pd.concat([all_df, m_df])
    
    # 添加待补充字段，如代谢物含义等
    all_df["means"] = ""
    all_df["means_chs"] = ""
    all_df["Kingdom"] = ""
    all_df["SuperClass"] = ""
    all_df["Class"] = ""
    all_df["SubClass"] = ""
    all_df["DirectParent"] = ""

    # 导出csv
    all_df.to_csv("%s%s%s%s%s_name_result.csv" % (path, PATH_SEP, "out", PATH_SEP, origin_filename), index=False)
    print("整合完成...")
