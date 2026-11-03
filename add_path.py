import json
import os

# # 原始 JSON 文件路径
# json_path = './video_information.json'

# # 指定的类别文件夹
# target_categories = [
#     "Archery",
#     "Canoeing",
#     "Carving_jack-o-lanterns",
#     "Getting_a_piercing",
#     "Polishing_forniture",
#     "Smoking_a_cigarette",
#     "Zumba"
# ]

# # 根路径
# base_path = './tree/new_set'

# # 读取原有 JSON 数据
# if os.path.exists(json_path):
#     with open(json_path, 'r') as f:
#         video_info_list = json.load(f)
# else:
#     video_info_list = []

# # 遍历目标类别
# for category in target_categories:
#     category_path = os.path.join(base_path, category)
#     if not os.path.isdir(category_path):
#         continue

#     # 遍历该类别下的 v_ 开头目录
#     for item in os.listdir(category_path):
#         if item.startswith('v_'):
#             segment_path = os.path.join(category_path, item, 'segment_video.pkl')
#             if os.path.isfile(segment_path):
#                 entry = {
#                     'information': '',
#                     'path': segment_path
#                 }
#                 video_info_list.append(entry)

# # 写回更新后的 JSON 文件
# with open(json_path, 'w') as f:
#     json.dump(video_info_list, f, indent=4)

# print(f"更新完成，当前总记录数：{len(video_info_list)}")
import json
import os
import re

# 你的 JSON 文件路径
input_file = "./video_information.json"
output_file = "./video_information.json"  # 如果你想直接覆盖原文件，也可以用 input_file

# 加载 JSON 数据
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 遍历每一项并修改 information 字段
for item in data:
    if(item['information']!=''):continue
    path = item.get("path", "")
    match = re.search(r"(v_[^\\/]+)", path)  # 匹配 v_ 开头的视频文件夹名
    if match:
        video_name = match.group(1) + ".mp4"
        item["information"] = video_name

# 写回 JSON 文件
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)