import os
import json
import random

def get_video_dataset(data_path):
    dataset = {}
    for action in os.listdir(data_path):
        action_path = os.path.join(data_path, action)
        if os.path.isdir(action_path):
            dataset[action] = [os.path.join(action, vid) for vid in os.listdir(action_path) if vid.endswith(('.mp4', '.avi', '.mkv'))]
    return dataset

def correct_action_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(actions) < 3:
            continue  # 确保有足够的类别可选

        # 选取 3 个不同的动作类别
        selected_actions = random.sample(actions, 3)
        
        # 确保每个类别至少有一个视频
        selected_videos = {}
        for action in selected_actions:
            if dataset[action]:
                selected_videos[action] = random.choice(dataset[action])

        # 如果有某个类别没有视频，跳过当前循环
        if len(selected_videos) < 3:
            continue

        # 选项 A, B, C
        Options = {
            "A": selected_videos[selected_actions[0]],
            "B": selected_videos[selected_actions[1]],
            "C": selected_videos[selected_actions[2]]
        }

        # 随机选一个类别作为正确答案
        correct_action = random.choice(selected_actions)
        correct_answer = next(k for k, v in Options.items() if v == selected_videos[correct_action])

        question = {
            "videos": list(Options.values()),
            "question": f"Which video is about the {correct_action} action?",
            "options": Options,
            "answer": correct_answer  # 返回 "A", "B", "C"
        }
        qa_list.append(question)
    
    return qa_list



def correct_video_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())

    for _ in range(num_questions):
        if len(actions) < 3:
            continue  # 确保有足够的类别可选

        selected_actions = random.sample(actions, 3)  # 选择 3 个不同的动作类别
        correct_action = random.choice(selected_actions)  # 从中选 1 个作为正确答案
        
        if len(dataset[correct_action]) < 3:
            continue  # 确保正确类别有足够的视频
        
        videos = random.sample(dataset[correct_action], 3)  # 选 3 个视频作为输入
        
        # 选项 A, B, C
        Options = {"A": selected_actions[0], "B": selected_actions[1], "C": selected_actions[2]}
        
        # 确定正确答案对应的选项 (A, B, or C)
        answer = [key for key, value in Options.items() if value == correct_action][0]

        question = {
            "videos": videos,
            "question": "What actions are these videos about?",
            "options": Options,
            "answer": answer  # A, B, 或 C
        }
        qa_list.append(question)

    return qa_list



def save_qa_dataset(qa_list, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    data_path = "data"  # 修改为实际路径
    choice_output_path = "cross_action__qa.json"
    judgment_output_path = "cross_video_qa.json"
    
    dataset = get_video_dataset(data_path)
    choice_qa_list = correct_action_questions(dataset, num_questions=50)
    judgment_qa_list = correct_video_questions(dataset, num_questions=50)
    
    save_qa_dataset(choice_qa_list, choice_output_path)
    save_qa_dataset(judgment_qa_list, judgment_output_path)
    
    print(f"corss_action问答数据集已保存至 {choice_output_path}")
    print(f"corss_video问答数据集已保存至 {judgment_output_path}")
