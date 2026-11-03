import json
from textwrap import dedent
import json

import os
from dotenv import load_dotenv
from typing import Type


total = 0
correct = 0
# for x in ['./QA/crash/Crash/crash_accident_qa.json','./QA/crash/Crash/crash_anomaly_qa.json','./QA/crash/Crash/crash_ego_qa.json','./QA/crash/Crash/crash_timing_weather_qa.json']:
for x in['./QA/UCF/QA/cross_action_qa.json','./QA/UCF/QA/cross_video_qa.json','./QA/UCF/QA/qa_action_anomaly.json','./QA/UCF/QA/qa_action_compare.json']:
# for x in['./QA/cross_date.json','./QA/cross_place.json','./QA/cross_video.json','./QA/single_video.json']:
# for x in['./QA/new_qa/cross_action__qa.json','./QA/new_qa/cross_QA.json','./QA/new_qa/QA.json']:
    print(x)
    cur_total,cur_correct = 0,0
    with open(x, 'r') as file:
        questions = json.load(file)
    for ques in questions:
        total += 1
        cur_total+=1
        if(ques["answer"]==ques["return_answer"]):
            correct+=1
            cur_correct+=1
    cur_rate = float(cur_correct/cur_total)
    print(cur_correct,cur_total,cur_rate)
rate = float(correct/total)
print(correct,total,rate)

# total = {"Person Identification":0,"Behavior Analysis":0,"Summaration and Reasoning":0}
# correct = {"Person Identification":0,"Behavior Analysis":0,"Summaration and Reasoning":0}
# for x in['./QA/cross_date.json','./QA/cross_place.json','./QA/cross_video.json','./QA/single_video.json']:
# # for x in['./QA/new_qa/cross_action__qa.json','./QA/new_qa/cross_QA.json','./QA/new_qa/QA.json']:
#     print(x)
#     cur_total,cur_correct = {"Person Identification":0,"Behavior Analysis":0,"Summaration and Reasoning":0},{"Person Identification":0,"Behavior Analysis":0,"Summaration and Reasoning":0}
#     with open(x, 'r') as file:
#         questions = json.load(file)
#     for ques in questions:
#         total[ques['category']] += 1
#         cur_total[ques['category']] +=1
#         if(ques["answer"]==ques["return_answer"]):
#             correct[ques['category']] +=1
#             cur_correct[ques['category']] +=1
#     # cur_rate = float(cur_correct/cur_total)
#     print(cur_correct,cur_total)
# # rate = float(correct/total)
# print(correct,total)







# # 遍历问题集
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
        
        
#         # 将当前问题的答案更新到JSON文件中
#         with open(test_path, 'w') as file:
#             json.dump(questions, file, indent=4)
#     except Exception as e:
#         # 如果函数调用失败，可以在这里处理异常，例如设置一个默认答案或记录错误
#         print(f"Error processing question: {x['question']}. Error: {e}")
#         continue
        

# # 注意：如果代码执行到这里，说明所有问题都已处理完毕，可以再次写入文件以确保最终状态被保存
# with open(test_path, 'w') as file:
#     json.dump(questions, file, indent=4)


