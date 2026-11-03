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
# test_list =  ['./QA/cross_place.json','./QA/cross_video.json','./QA/single_video.json']
test_list = ['./QA/crash/Crash/crash_accident_qa.json','./QA/crash/Crash/crash_anomaly_qa.json','./QA/crash/Crash/crash_ego_qa.json','./QA/crash/Crash/crash_timing_weather_qa.json']
# test_list = ['./QA/UCF/QA/cross_action_qa.json','./QA/UCF/QA/cross_video_qa.json','./QA/UCF/QA/qa_action_anomaly.json','./QA/UCF/QA/qa_action_compare.json']
# ['./QA/cross_date.json','./QA/cross_place.json','./QA/cross_video.json','./QA/single_video.json']
# test_list = ['./QA/new_qa/cross_action_qa.json','./QA/new_qa/cross_QA.json','./QA/new_qa/cross_video_qa.json','./QA/new_qa/QA.json']
for test_path in test_list:
    # 读取原始JSON文件
    # test_path = './QA/cross_date.json'
    with open(test_path, 'r',encoding='utf-8') as file:
        questions = json.load(file)

    for x in questions:
        x['return_answer'] = ''

            

    with open(test_path, 'w') as file:
        json.dump(questions, file, indent=4)


