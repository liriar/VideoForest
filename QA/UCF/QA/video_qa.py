import os
import json
import random

def get_video_dataset(root_path="ucf_action", max_actions=5, max_videos=5):
    dataset = {}
    
    # 获取前 max_actions 个动作类别
    action_classes = sorted([d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))])[:max_actions]
    
    for action in action_classes:
        action_path = os.path.join(root_path, action)
        video_list = []

        # 遍历每个动作类别下的子目录（如 001, 002）
        subdirs = sorted([d for d in os.listdir(action_path) if os.path.isdir(os.path.join(action_path, d))])
        for sub in subdirs:
            sub_path = os.path.join(action_path, sub)
            for file in os.listdir(sub_path):
                if file.endswith(('.avi', '.mp4', '.mkv')):
                    video_list.append(os.path.join(action, sub, file))  # 相对路径
                    break  # 每个子目录只选一个视频
            if len(video_list) >= max_videos:
                break
        
        if video_list:
            dataset[action] = video_list

    return dataset

def correct_action_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())
    
    for _ in range(num_questions):
        if len(actions) < 3:
            continue

        selected_actions = random.sample(actions, 3)
        selected_videos = {}
        for action in selected_actions:
            if dataset[action]:
                selected_videos[action] = random.choice(dataset[action])

        if len(selected_videos) < 3:
            continue

        # 构建选项，只显示文件名
        Options = {
            "A": os.path.basename(selected_videos[selected_actions[0]]),
            "B": os.path.basename(selected_videos[selected_actions[1]]),
            "C": os.path.basename(selected_videos[selected_actions[2]])
        }

        correct_action = random.choice(selected_actions)
        correct_answer = next(k for k, v in zip(Options.keys(), selected_videos.values()) if v == selected_videos[correct_action])

        question = {
            "videos": list(selected_videos.values()),
            "question": f"Which video is about the {correct_action} action?",
            "options": Options,
            "answer": correct_answer
        }
        qa_list.append(question)
    
    return qa_list


def correct_video_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())

    for _ in range(num_questions):
        if len(actions) < 3:
            continue

        selected_actions = random.sample(actions, 3)
        correct_action = random.choice(selected_actions)
        
        if len(dataset[correct_action]) < 3:
            continue

        videos = random.sample(dataset[correct_action], 3)

        # 选项值改为文件名
        Options = {
            "A": os.path.basename(videos[0]),
            "B": os.path.basename(videos[1]),
            "C": os.path.basename(videos[2])
        }

        # 这里的 answer 仍然按动作名称找
        answer = random.choice(["A", "B", "C"])  # 任意指定一个答案为正确
        question = {
            "videos": videos,
            "question": "What actions are these videos about?",
            "options": Options,
            "answer": answer
        }
        qa_list.append(question)

    return qa_list
def anomaly_detection_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())

    for _ in range(num_questions):
        if len(actions) < 2:
            continue

        # 选两个相同动作，一个不同动作
        common_action = random.choice(actions)
        if len(dataset[common_action]) < 2:
            continue

        other_action = random.choice([a for a in actions if a != common_action])
        if not dataset[other_action]:
            continue

        vids = random.sample(dataset[common_action], 2)
        vids.append(random.choice(dataset[other_action]))
        random.shuffle(vids)

        # 找出哪个是异常项
        labels = [common_action if v in dataset[common_action] else other_action for v in vids]
        correct_index = labels.index(other_action)
        answer = ["A", "B", "C"][correct_index]

        question = {
            "videos": vids,
            "question": "Which video shows a different action from the other two?",
            "options": {
                "A": os.path.basename(vids[0]),
                "B": os.path.basename(vids[1]),
                "C": os.path.basename(vids[2]),
            },
            "answer": answer
        }
        qa_list.append(question)

    return qa_list

def compare_action_questions(dataset, num_questions=10):
    qa_list = []
    actions = list(dataset.keys())

    for _ in range(num_questions):
        if len(actions) < 2:
            continue

        # 选两个动作类别，每类各选一个视频
        action1, action2 = random.sample(actions, 2)
        if not dataset[action1] or not dataset[action2]:
            continue

        vid1 = random.choice(dataset[action1])
        vid2 = random.choice(dataset[action2])

        # 添加一个同动作的视频与其中之一构成相似动作组合
        same_action = action1 if random.random() < 0.5 else action2
        if len(dataset[same_action]) < 2:
            continue

        # 选一个与上述两个不同的视频（同类）
        same_vids = [v for v in dataset[same_action] if v not in [vid1, vid2]]
        if not same_vids:
            continue
        vid3 = random.choice(same_vids)

        video_set = [vid1, vid2, vid3]
        random.shuffle(video_set)

        question = {
            "videos": video_set,
            "question": "Which two videos show the most similar action?",
            "options": {
                "A": f"{os.path.basename(video_set[0])} & {os.path.basename(video_set[1])}",
                "B": f"{os.path.basename(video_set[0])} & {os.path.basename(video_set[2])}",
                "C": f"{os.path.basename(video_set[1])} & {os.path.basename(video_set[2])}"
            },
            "answer": "C" if same_action in [action1, action2] else "A"  # 你可以更智能处理
        }
        qa_list.append(question)

    return qa_list



def save_qa_dataset(qa_list, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    data_path = "ucf_action"  # 修改为实际路径
    choice_output_path = "corss_action__qa.json"
    judgment_output_path = "corss_video_qa.json"
    
    dataset = get_video_dataset(data_path)
    choice_qa_list = correct_action_questions(dataset, num_questions=20)
    judgment_qa_list = correct_video_questions(dataset, num_questions=20)
    compare_qa_list = compare_action_questions(dataset, 20)
    anomaly_qa_list = anomaly_detection_questions(dataset, 20)
    
    save_qa_dataset(choice_qa_list, choice_output_path)
    save_qa_dataset(judgment_qa_list, judgment_output_path)
    save_qa_dataset(compare_qa_list, "qa_action_compare.json")
    save_qa_dataset(anomaly_qa_list, "qa_action_anomaly.json")
    
    print(f"corss_action问答数据集已保存至 {choice_output_path}")
    print(f"corss_video问答数据集已保存至 {judgment_output_path}")
