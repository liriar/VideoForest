import os
import json
import random
import re

def load_annotations(annotation_path, max_videos=100):
    """Load annotations from the Crash-1500.txt file for the first max_videos."""
    dataset = {}
    with open(annotation_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_videos:
                break
            # 跳过空行
            if not line.strip():
                print(f"警告: 跳过第 {i+1} 行，因为它是空的")
                continue
            # 使用正则表达式匹配字段，保护 binlabels 字段
            pattern = r'^([^,]+),\s*(\[[\d,\s]*\]),([^,]+),([^,]+),([^,]+),([^,]+),([^,\n]+)$'
            match = re.match(pattern, line.strip())
            if not match:
                print(f"警告: 跳过第 {i+1} 行，格式不正确: {line.strip()}")
                continue
            try:
                vidname = match.group(1).strip()
                binlabels_str = match.group(2).strip()
                startframe = match.group(3).strip()
                youtubeID = match.group(4).strip()
                timing = match.group(5).strip()
                weather = match.group(6).strip()
                egoinvolve = match.group(7).strip()
                # 解析 binlabels 为 Python 列表
                binlabels = json.loads(binlabels_str)
                video_path = os.path.join('video', f'{vidname}.mp4')
                if os.path.exists(video_path):
                    dataset[vidname] = {
                        'video_path': video_path,
                        'binlabels': binlabels,
                        'startframe': startframe,
                        'youtubeID': youtubeID,
                        'timing': timing,
                        'weather': weather,
                        'egoinvolve': egoinvolve
                    }
                else:
                    print(f"警告: 视频文件 {video_path} 不存在，跳过视频 {vidname}")
            except Exception as e:
                print(f"错误: 解析第 {i+1} 行时出错: {line.strip()}. 错误信息: {str(e)}")
                continue
    if not dataset:
        raise ValueError("没有成功加载任何视频数据，请检查 Crash-1500.txt 文件格式或视频文件路径")
    return dataset

def correct_accident_questions(dataset, num_questions=10):
    """Generate questions about which video contains an accident in specific frames."""
    qa_list = []
    video_ids = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(video_ids) < 3:
            continue
        selected_videos = random.sample(video_ids, 3)
        selected_data = {vid: dataset[vid]['video_path'] for vid in selected_videos}
        
        # 确保至少有一个视频包含事故帧
        accident_vids = [vid for vid in selected_videos if any(dataset[vid]['binlabels'])]
        if not accident_vids:
            continue
        correct_vid = random.choice(accident_vids)
        
        # 获取事故帧范围
        binlabels = dataset[correct_vid]['binlabels']
        accident_frames = [i+1 for i, label in enumerate(binlabels) if label == 1]
        frame_range = f"帧 {accident_frames[0]}-{accident_frames[-1]}" if accident_frames else "无事故"
        
        Options = {
            "A": os.path.basename(selected_data[selected_videos[0]]),
            "B": os.path.basename(selected_data[selected_videos[1]]),
            "C": os.path.basename(selected_data[selected_videos[2]])
        }
        correct_answer = next(k for k, v in Options.items() if v == os.path.basename(selected_data[correct_vid]))
        
        question = {
            "videos": list(selected_data.values()),
            "question": f"哪个视频在 {frame_range} 包含事故？",
            "options": Options,
            "answer": correct_answer
        }
        qa_list.append(question)
    
    return qa_list

def timing_weather_questions(dataset, num_questions=10):
    """Generate questions about timing (Day/Night) or weather conditions."""
    qa_list = []
    video_ids = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(video_ids) < 3:
            continue
        selected_videos = random.sample(video_ids, 3)
        selected_data = {vid: dataset[vid]['video_path'] for vid in selected_videos}
        
        # 随机选择时间或天气问题
        attr = random.choice(['timing', 'weather'])
        attr_values = list(set(dataset[vid][attr] for vid in video_ids))
        if not attr_values:
            continue
        correct_value = random.choice(attr_values)
        correct_vids = [vid for vid in selected_videos if dataset[vid][attr] == correct_value]
        if not correct_vids:
            continue
        correct_vid = random.choice(correct_vids)
        
        Options = {
            "A": os.path.basename(selected_data[selected_videos[0]]),
            "B": os.path.basename(selected_data[selected_videos[1]]),
            "C": os.path.basename(selected_data[selected_videos[2]])
        }
        correct_answer = next(k for k, v in Options.items() if v == os.path.basename(selected_data[correct_vid]))
        
        question_text = f"哪个视频在 {correct_value} 条件下录制？" if attr == 'timing' else f"哪个视频在 {correct_value} 天气下录制？"
        question = {
            "videos": list(selected_data.values()),
            "question": question_text,
            "options": Options,
            "answer": correct_answer
        }
        qa_list.append(question)
    
    return qa_list

def ego_involvement_questions(dataset, num_questions=10):
    """Generate questions about ego vehicle involvement."""
    qa_list = []
    video_ids = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(video_ids) < 3:
            continue
        selected_videos = random.sample(video_ids, 3)
        selected_data = {vid: dataset[vid]['video_path'] for vid in selected_videos}
        
        correct_value = random.choice(['Yes', 'No'])
        correct_vids = [vid for vid in selected_videos if dataset[vid]['egoinvolve'] == correct_value]
        if not correct_vids:
            continue
        correct_vid = random.choice(correct_vids)
        
        Options = {
            "A": os.path.basename(selected_data[selected_videos[0]]),
            "B": os.path.basename(selected_data[selected_videos[1]]),
            "C": os.path.basename(selected_data[selected_videos[2]])
        }
        correct_answer = next(k for k, v in Options.items() if v == os.path.basename(selected_data[correct_vid]))
        
        question = {
            "videos": list(selected_data.values()),
            "question": f"哪个视频{'涉及' if correct_value == 'Yes' else '不涉及'}自车在事故中？",
            "options": Options,
            "answer": correct_answer
        }
        qa_list.append(question)
    
    return qa_list

def anomaly_detection_questions(dataset, num_questions=10):
    """Generate questions to identify the video with different timing or weather."""
    qa_list = []
    video_ids = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(video_ids) < 3:
            continue
        selected_videos = random.sample(video_ids, 3)
        selected_data = {vid: dataset[vid]['video_path'] for vid in selected_videos}
        
        # 选择属性（时间或天气）
        attr = random.choice(['timing', 'weather'])
        attr_values = [dataset[vid][attr] for vid in selected_videos]
        
        # 确保两个视频具有相同属性值，一个不同
        common_value = max(set(attr_values), key=attr_values.count)
        if attr_values.count(common_value) < 2:
            continue
        anomaly_vid = next((vid for vid in selected_videos if dataset[vid][attr] != common_value), None)
        if not anomaly_vid:
            continue
        
        Options = {
            "A": os.path.basename(selected_data[selected_videos[0]]),
            "B": os.path.basename(selected_data[selected_videos[1]]),
            "C": os.path.basename(selected_data[selected_videos[2]])
        }
        correct_answer = next(k for k, v in Options.items() if v == os.path.basename(selected_data[anomaly_vid]))
        
        question = {
            "videos": list(selected_data.values()),
            "question": f"哪个视频的 {attr} 条件与其他两个不同？",
            "options": Options,
            "answer": correct_answer
        }
        qa_list.append(question)
    
    return qa_list

def save_qa_dataset(qa_list, output_path):
    """Save the QA dataset to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    annotation_path = "Crash-1500.txt"
    try:
        dataset = load_annotations(annotation_path, max_videos=20)
        
        # 生成不同类型的问答数据集
        accident_qa_list = correct_accident_questions(dataset, num_questions=20)
        timing_weather_qa_list = timing_weather_questions(dataset, num_questions=20)
        ego_qa_list = ego_involvement_questions(dataset, num_questions=20)
        anomaly_qa_list = anomaly_detection_questions(dataset, num_questions=20)
        
        # 保存问答数据集
        save_qa_dataset(accident_qa_list, "crash_accident_qa.json")
        save_qa_dataset(timing_weather_qa_list, "crash_timing_weather_qa.json")
        save_qa_dataset(ego_qa_list, "crash_ego_qa.json")
        save_qa_dataset(anomaly_qa_list, "crash_anomaly_qa.json")
        
        print("事故问答数据集已保存至 crash_accident_qa.json")
        print("时间和天气问答数据集已保存至 crash_timing_weather_qa.json")
        print("自车涉及问答数据集已保存至 crash_ego_qa.json")
        print("异常检测问答数据集已保存至 crash_anomaly_qa.json")
    except Exception as e:
        print(f"运行时发生错误: {str(e)}")