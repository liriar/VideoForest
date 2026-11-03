import os
import json


def filter_videos(json_file, video_folder, output_json):
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    # 读取 JSON 数据
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：文件 {json_file} 不存在")
        return
    except json.JSONDecodeError:
        print(f"错误：文件 {json_file} 不是有效的 JSON 格式")
        return

    database = data.get("database", {})

    # 获取视频文件名（去掉前缀 'v_' 和后缀 '.mp4'）
    try:
        video_files = [f for f in os.listdir(video_folder)]
        video_ids = {f[2:] for f in video_files}  # 提取唯一标识符
        print("找到的视频 ID:", video_ids)
    except FileNotFoundError:
        print(f"错误：视频文件夹 {video_folder} 不存在")
        return

    # 筛选匹配的视频信息
    filtered_data = {"database": {}}
    for vid in video_ids:
        if vid in database:
            filtered_data["database"][vid] = database[vid]

    # 检查结果
    if not filtered_data["database"]:
        print("警告：没有找到匹配的视频数据")

    # 保存筛选后的 JSON 数据
    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=4, ensure_ascii=False)
        print(f"筛选完成，结果保存在 {output_json}")
    except Exception as e:
        print(f"错误：无法保存文件 {output_json}，原因：{e}")

if __name__=='__main__':
    # 设置文件路径
    json_file = "datadset/HACS-dataset-master/HACS_v1.1.1/HACS_segments_v1.1.1.json"  # 原始 JSON 文件
    video_folder = "Multivideo/preprocess/Carving_jack-o-lantrens/"  # 视频文件夹
    output_json = "Multivideo/preprocess/Carving_jack-o-lantrens/filtered_data.json"  # 结果 JSON 文件
    filter_videos(json_file, video_folder, output_json)
    
