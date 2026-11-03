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
import time

#记得改Information路径
# test_list = ['./QA/cross_date.json','./QA/cross_place.json','./QA/cross_video.json','./QA/single_video.json']
video_information_dir = './QA/UCF/QA/UCF_information.json'

test_list = ['./QA/UCF/QA/cross_action_qa.json','./QA/UCF/QA/cross_video_qa.json','./QA/UCF/QA/qa_action_anomaly.json','./QA/UCF/QA/qa_action_compare.json']
# video_information_dir = './QA/crash/Crash/crash_video_information.json'
# test_list = ['./QA/crash/Crash/crash_accident_qa.json','./QA/crash/Crash/crash_anomaly_qa.json','./QA/crash/Crash/crash_ego_qa.json','./QA/crash/Crash/crash_timing_weather_qa.json']
for test_path in test_list:
    # 读取原始JSON文件
    # test_path = './QA/cross_date.json'
    with open(test_path, 'r',encoding='utf-8') as file:
        questions = json.load(file)



    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # json_path = os.path.join(current_dir, './video_information.json')
    json_path = os.path.join(current_dir, video_information_dir)
    with open(json_path, 'r') as f:
        data = json.load(f)
    video_information = json.dumps(data, indent=4)

    videoforest_crew = VideoForestcrew()


    for x in questions:
        if(x['return_answer']!=''):
            continue
        options = None
        try:
            # 调用函数并获取答案
            question = x['question']
            options = x['options']
            option_str = ",".join([f"{k}:{v}" for k, v in options.items()])
            input_str = question+' '+option_str

            start_time = time.time()

            result = videoforest_crew.run(input_str,video_information)
            result = str(result)

            end_time = time.time()
            execution_time = round(end_time - start_time, 2)
            
            # 更新答案
            print('*'*10,'\n',result)
            x['return_answer'] = result
            # x['return_answer'] = ''
            

            # usage = videoforest_crew.latest_usage if hasattr(videoforest_crew, 'latest_usage') else {}
            usage = getattr(videoforest_crew, 'latest_usage', None)
            # print(usage)
            # print(dir(usage))
            # x['return_answer'] = result
            x['execution_time_seconds'] = execution_time
            x['token_input'] = getattr(usage, 'prompt_tokens', 0)
            x['token_output'] = getattr(usage, 'completion_tokens', 0)
            x['token_total'] = getattr(usage, 'total_tokens', x['token_input'] + x['token_output'])
            x['token_cached'] = getattr(usage, 'cached_prompt_tokens', 0)  # 可选字段
            
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


