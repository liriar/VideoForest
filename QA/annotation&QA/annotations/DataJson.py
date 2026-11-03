import os
import json

def generate_annotation_outline(root_dir):
    for action_folder in os.listdir(root_dir):
        action_path = os.path.join(root_dir, action_folder)
        if os.path.isdir(action_path):
            annotation_outline = []
            
            for video_file in os.listdir(action_path):
                if video_file.endswith(('.mp4', '.avi', '.mkv')):  # 支持的视频格式
                    video_data = {
                        "video_name": video_file,
                        "annotations": []  # 这里可以填充具体的标注结构
                    }
                    annotation_outline.append(video_data)
            
            json_filename = os.path.join(root_dir, f"{action_folder}.json")
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(annotation_outline, f, indent=4, ensure_ascii=False)
            
            print(f"JSON 注释大纲已生成：{json_filename}")

if __name__ == "__main__":
    root_directory = "./"  # 当前目录
    generate_annotation_outline(root_directory)
