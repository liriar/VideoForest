import json
import os

def analyze_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    exec_time_sum = 0.0
    token_sum = 0

    for item in data:
        try:
            exec_time = float(item["execution_time_seconds"])
            total_token = int(item["token_total"])
            exec_time_sum += exec_time
            token_sum += total_token
            count += 1
        except KeyError as e:
            print(f"⚠️ 跳过 {file_path} 中缺字段项: {e}")
            continue

    return count, exec_time_sum, token_sum

def main():
    # base_path = "./QA"
    # target_files = [
    #     "cross_date.json",
    #     "cross_place.json",
    #     "cross_video.json",
    #     "single_video.json"
    # ]
    base_path = "./QA/new_qa"
    target_files = [
        "cross_action_qa.json",
        "cross_QA.json",
        "QA.json"
    ]

    total_count = 0
    total_exec_time = 0.0
    total_token_sum = 0

    for file in target_files:
        full_path = os.path.join(base_path, file)
        count, exec_sum, token_sum = analyze_json_file(full_path)
        print(f"✅ 处理 {file}：{count} 条记录")
        total_count += count
        total_exec_time += exec_sum
        total_token_sum += token_sum

    print("\n📊 总体统计结果：")
    print(f"总项数：{total_count}")
    if total_count > 0:
        print(f"平均执行时间（秒）：{total_exec_time / total_count:.2f}")
        print(f"平均 Token 总数：{total_token_sum / total_count:.2f}")
    else:
        print("⚠️ 没有可用记录！")

if __name__ == "__main__":
    main()
