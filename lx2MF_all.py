import gzip
import json
import sys
import os

from sympy.codegen import Print


def parse_lxmc_and_save(file_path, output_file=None):
    """
    解析 .lxmc 文件并保存为格式化的 JSON 文件。

    Args:
        file_path (str): .lxmc 文件的路径。
        output_file (str, optional): 输出 JSON 文件的路径。如果为 None，则自动生成。
    """
    # 用 gzip 解压
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        data = json.load(f)

    # 确定输出文件名
    if output_file is None:
        base = os.path.splitext(file_path)[0]
        output_file = base + ".json"

    # 保存为格式化的 JSON 文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"lx歌单预处理文件已保存: {output_file}")

def extract_sources(input_file):
    """
    从JSON文件中提取指定 "source" 的条目，并将它们按 source 分别保存到字典中，
    然后将字典保存到新的JSON文件中。

    Args:
        input_file (str): 输入JSON文件的路径。
    """
    extracted_data = {
        'wy': [],
        'tx': [],
        'kw': [],
        'kg': []
    }
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item_list in data['data']:
            for item in item_list['list']:
                source = item['source']
                if source in extracted_data:
                    extracted_data[source].append(item)
    # 打印各个source的数量
    for source, items in extracted_data.items():
        print(f"音乐平台: {source}, 音乐数量: {len(items)}")
    return extracted_data

def convert_lx_wy_to_mf_wy(list_wy):
    mf_list_wy_yl = []
    for data in list_wy:
        for item in data:
            mf_item = {
                "id": item['meta']['songId'],
                "artist": item['singer'],
                "title": item['name'],
                "album": item['meta']['albumName'],
                "artwork": item['meta']['picUrl'],
                "url": f"https://share.duanx.cn/url/wy/{item['meta']['songId']}/128k",
                "qualities": {
                    "low": {},
                    "standard": {},
                    "high": {},
                    "super": {}
                },
                "copyrightId": 0,
                "platform": "元力WY",
                "$$ref": 1
            }
            mf_list_wy_yl.append(mf_item)
        print(f"网易云音乐数据转换完成: 共 {len(mf_list_wy_yl)} 条数据")
    return mf_list_wy_yl

def convert_lx_tx_to_mf_wy(list_tx):
    mf_list_tx_yl = []
    for data in list_tx:
        for item in data:
            tx_mf_item = {
                "id": item['meta']['id'],
                "songmid": item['meta']['songId'],
                "title": item['name'],
                "artist": item['singer'],
                "artwork": item['meta']['picUrl'],
                "album": item['meta']['albumName'],
                "albumid": item['meta']['albumId'],
                "albummid": item['meta']['albumId'],
                "platform": "元力QQ",
                "$$ref": 1
                }
            mf_list_tx_yl.append(tx_mf_item)
        print(f"QQ音乐数据转换完成: 共 {len(mf_list_tx_yl)} 条数据")
    return mf_list_tx_yl

def convert_lx_kw_to_mf_wy(list_kw):
    mf_list_kw_yl = []
    for data in list_kw:
        for item in data:
            kw_mf_item = {
                "id": item['meta']['songId'],
                "artwork": item['meta']['picUrl'],
                "title": item['name'],
                "artist": item['singer'],
                "album": item['meta']['albumName'],
                "albumId": item['meta']['albumId'],
                # "artistId": "1493", lx里并未提供
                "platform": "元力KW",
                "$$ref": 1
                }
            mf_list_kw_yl.append(kw_mf_item)
        print(f"酷我音乐数据转换完成: 共 {len(mf_list_kw_yl)} 条数据")
    return mf_list_kw_yl

def wrap_mf_list(mf_list, output_file):
    wrapped = {
        "musicSheets": [
            {
                "id": "favorite",
                "title": "导入的音乐",
                "platform": "本地",
                "musicList": mf_list,
                "$$sortIndex": -1,
                "$sortIndex": -1,
                # artwork 设置为第一个音乐的 artwork
                "artwork": mf_list[0]['artwork'] if mf_list else "",
            }
        ]
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(wrapped, f, indent=4, ensure_ascii=False)



def deduplicate_and_merge(mf_list_wy_yl, mf_list_tx_yl, mf_list_kw_yl):
    """
    对来自不同平台的音乐列表进行去重（基于 'id' 字段），然后合并它们。

    Args:
        mf_list_wy_yl (list): 网易云音乐列表。
        mf_list_tx_yl (list): 腾讯音乐列表。
        mf_list_kw_yl (list): 酷我音乐列表。

    Returns:
        list: 去重和合并后的音乐列表。
    """
    merged_list = mf_list_wy_yl + mf_list_tx_yl + mf_list_kw_yl
    seen_ids = set()
    deduplicated_list = []
    platform_counts_before = {}  # 用于存储去重前平台计数
    platform_counts_after = {}  # 用于存储去重后平台计数

    # 统计去重前每个平台的数量
    for item in merged_list:
        platform = item.get('platform', '未知平台')
        platform_counts_before[platform] = platform_counts_before.get(platform, 0) + 1

    for item in merged_list:
        if item['id'] not in seen_ids:
            deduplicated_list.append(item)
            seen_ids.add(item['id'])
            platform = item.get('platform', '未知平台')
            platform_counts_after[platform] = platform_counts_after.get(platform, 0) + 1

    # 打印每个平台的数量
    for platform in platform_counts_before.keys():
        count_before = platform_counts_before.get(platform, 0)
        count_after = platform_counts_after.get(platform, 0)
        duplicate_count = count_before - count_after
        print(
            f"音乐平台: {platform}, 去重前数量: {count_before}条, 去重后数量: {count_after}条, 重复数量: {duplicate_count}条")
    return deduplicated_list


if __name__ == "__main__":
    #################这是通过脚本运行的入口###################
    # file_path ='lx_list.lxmc'  # 替换为你的 .lxmc 文件路径
    # parse_lxmc_and_save(file_path)
    # input_file = 'lx_list' + '.json'
    # extracted_data = extract_sources(input_file)
    # mf_list_wy_yl = convert_lx_wy_to_mf_wy([extracted_data['wy']])
    # mf_list_tx_yl = convert_lx_tx_to_mf_wy([extracted_data['tx']])
    # mf_list_kw_yl = convert_lx_kw_to_mf_wy([extracted_data['kw']])
    # mf_list = deduplicate_and_merge(mf_list_wy_yl, mf_list_tx_yl, mf_list_kw_yl)
    # print('wy + tx + kw的音乐数据处理完成，共计:', len(mf_list), '条')
    # output_file = 'lx_list_MusicFree.json'
    # wrap_mf_list(mf_list, output_file)
    # print(f"歌单转换已完成，文件位置: {output_file}")
    ######################################################

    ###############这是通过命令行运行的入口###################
    if len(sys.argv) < 2:
        print("用法: python lx2MF.py lxmc文件")
        sys.exit(1)
    if not sys.argv[1].endswith('.lxmc'):
        print("请输入有效的 .lxmc 文件")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("警告: 只会处理第一个参数作为文件路径，其他参数将被忽略")
    file_path = sys.argv[1]
    base = os.path.splitext(file_path)[0]
    parse_lxmc_and_save(file_path)
    input_file = base + '.json'
    extracted_data = extract_sources(input_file)
    mf_list_wy_yl = convert_lx_wy_to_mf_wy([extracted_data['wy']])
    mf_list_tx_yl = convert_lx_tx_to_mf_wy([extracted_data['tx']])
    mf_list_kw_yl = convert_lx_kw_to_mf_wy([extracted_data['kw']])
    mf_list = deduplicate_and_merge(mf_list_wy_yl, mf_list_tx_yl, mf_list_kw_yl)
    print('wy + tx + kw的音乐数据处理完成，共计:', len(mf_list), '条')
    output_file = 'lx_list_MusicFree.json'
    wrap_mf_list(mf_list, output_file)
    print(f"歌单转换已完成，文件位置: {output_file}")
    input("请按任意键退出...")
    ######################################################



