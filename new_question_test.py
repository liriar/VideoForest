import json
from crewai import Crew
from textwrap import dedent
import json
from agents import VideoAnalysisAgents
from tasks import VideoAnalysisTasks
import os
from dotenv import load_dotenv
from typing import Type
from main import VideoForestcrew



# 读取原始JSON文件
test_path = './QA/cross_date.json'
with open(test_path, 'r',encoding='utf-8') as file:
    questions = json.load(file)



# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, './video_information.json')
with open(json_path, 'r') as f:
    data = json.load(f)
video_information = json.dumps(data, indent=4)

videoforest_crew = VideoForestcrew()


for x in questions:
    # if(x['return_answer']!=''):
    #     continue
    # options = None
    try:
        # # 调用函数并获取答案
        # question = x['question']
        # options = x['options']
        # option_str = ",".join([f"{k}:{v}" for k, v in options.items()])
        # result = videoforest_crew.run(question+' '+option_str,video_information)
        # result = str(result)
        
        # # 更新答案
        # print('*'*10,'\n',result)
        # x['return_answer'] = result
        x['return_answer'] = ''
        
        
        # 将当前问题的答案更新到JSON文件中
        with open(test_path, 'w') as file:
            json.dump(questions, file, indent=4)
    except Exception as e:
        # 如果函数调用失败，可以在这里处理异常，例如设置一个默认答案或记录错误
        print(f"Error processing question: {x['question']}. Error: {e}")
        continue
        

# 遍历问题集
# for x in questions:
#     if(x['return_answer']!=''):
#         continue
#     options = None
#     try:
#         # 调用函数并获取答案
#         question = x['question']
#         options = x['options']
#         option_str = ",".join([f"{k}:{v}" for k, v in options.items()])
#         result = videoforest_crew.run(question+' '+option_str,video_information)
#         result = str(result)
        
#         # 更新答案
#         print('*'*10,'\n',result)
#         x['return_answer'] = result
#         # x['return_answer'] = ''
        
        
#         # 将当前问题的答案更新到JSON文件中
#         with open(test_path, 'w') as file:
#             json.dump(questions, file, indent=4)
#     except Exception as e:
#         # 如果函数调用失败，可以在这里处理异常，例如设置一个默认答案或记录错误
#         print(f"Error processing question: {x['question']}. Error: {e}")
#         continue
        

# 注意：如果代码执行到这里，说明所有问题都已处理完毕，可以再次写入文件以确保最终状态被保存
with open(test_path, 'w') as file:
    json.dump(questions, file, indent=4)


