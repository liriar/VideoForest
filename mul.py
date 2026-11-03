import pickle
import random
import openai
import os
from dotenv import load_dotenv
import json


# 设置 API 密钥
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
openai.api_key = os.getenv('OPENAI_API_KEY') 

def caption_filter(caption):
    
    prompt = f"Please simplify the following text by removing any content not related to people or people behavior. Keep only the parts that describe actions, behaviors, interactions,  emotions or anything related to  people.\n\nOriginal content: {caption}"
    prompt += 'If caption says no character is in the scene,just tell no one is in scene rather than say nothing.'
    prompt += "\nprovide the answer in JSON {'caption': answer}."
    # 调用 OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "you are a caption-simplifing assistant,simplify the caption by removing any content not related to people or people behavior. Keep only the parts that describe actions, behaviors, interactions,  emotions or anything related to  people.\n\n"},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    # 提取模型返回的内容
    return response

def node_filter(question,day,place):
    # print(question,day,place)
    prompt = f"Question: {question}\n\n"
    prompt += f"current Day: July {day}, Place: {place}\n\n"
    prompt += """
    Please check if the day and place mentioned in the question match the provided current day and place.

    - If the question asks for a specific day (e.g., day 1) and a specific place (e.g., office 2), match exactly.
    - If the question asks for a range of days (e.g., from day 1 to day 3) or range of place(e.g. office2 and 3), tell if the day or place is within that range(means match).
    - If the question asks for all days and places (e.g., all offices or all days), match any day and any place.
    
    Respond with 'Yes' if the provided day and place are relevant to the question. Otherwise, respond with 'No'.
    
    Provide the answer in JSON {'answer': 'Yes' or 'No'}.
    """
    # 调用 OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "You are a day and place matching assistant. Check if the provided day and place match the information in the question.\n\n"},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    # 提取模型返回的内容
    response_content = response.choices[0].message.content
            
    response_content = json.loads(response_content)
    res = response_content["answer"]
    return res


def format_output(question,result,question_type,options):
    
    prompt = f"Answer the question:{question},ONLY based on knowledge given:{result}.Each knowledge is given based on a single node,not every knowledge is useful for the question.select the  information from knowledge base. if knowledge contains something is not found,then just assume it didn't happen."
    if question_type == "duration":
        add_prompt = (
            "The answer should be given only as a float, representing the duration in seconds.if knowledge_base='no matching node',the answer should be 0.Do not include any other text, ONLY the numeric value of the duration (e.g., '45.52'). "
        )
    elif question_type == "judge":
        add_prompt = (
            "The answer should be either 'Yes' or 'No'.if knowledge_base='no matching node',the answer should be 'No'. Do not provide any other text, only the word 'Yes' or 'No'."
        )
    elif question_type == "comparison" and options != None:
        add_prompt = (
            f"The answer should be a choice.The options are{options} Do not include any other text, ONLY the choice(e.g., 'A')."
        )
    prompt += f'\n{add_prompt}'
    prompt += "\nprovide the answer in JSON {'answer': answer}."
    print(f'format_output:{result}')
    # 调用 OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": "you are a question-answering assistant,Answer the question ONLY based on the knowledge given.The knowledge base is the most relative information containing the answer to the question. "+f"\n{add_prompt}"+"respond in json {'answer':answer}"},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    # 提取模型返回的内容
    return response

from datetime import datetime, timedelta

def calculate_time(seconds):
    # 设置起始时间为 9:00:00
    start_time = datetime.strptime('09:00:00', '%H:%M:%S')
    
    # 计算经过的时间
    new_time1 = start_time + timedelta(seconds=float(seconds[0])*70)
    new_time2 = start_time + timedelta(seconds=float(seconds[1])*70)
    
    # 返回新的时间格式化为字符串
    return (new_time1.strftime('%H:%M:%S'),new_time2.strftime('%H:%M:%S'))




def format_information(node,i,day,place):
    day=day
    person_id = node["person_id"]
    time = calculate_time(node["time"])
    # duration = float(time[1] - time[0])
    caption = node["caption"]
    # caption = caption_filter(caption)
    
    # caption_res = json.loads(caption.choices[0].message.content)
    # simplified_caption = caption_res["caption"]
    simplified_caption = caption
    # print(f'\ncaption = {simplified_caption}')
    len_sub_seg = len(node["sub_segments"])
    return f'On July {day} in Office {place} here is the caption of node{i}, this segment has {len_sub_seg} sub segments,person_id in frame based on reid is{person_id},starting in{time[0]} and ending in{time[1]},{simplified_caption}'


def generate_response(captions,question,day,place):
    # 向模型询问当前的知识是否足够回答问题
    print('inf=',day,place)
    prompt = f" question: {question}\nknowledge_base:\n" + "\n".join(captions)+"\n."+f"this is a caption in Office {place} on July {day}\n"+"Each node's sub-segments provide more detailed descriptions of the current node. If the provided knowledge is enough to answer the question, respond with the answer in JSON {'answer': answer}. If not, respond with a list of indices (starting from 0) of current nodes(the index sequence of caption starting from 0) that its sub_segment might contain the answer(no more than 10 nodes).respond in JSON {'nodes_of_interest': [list_of_indices]}."+ \
            "Additionally, if there are events occurring in multiple nodes within a 1-second interval, treat them as continuous. " + \
            "For example, if two people are present in nodes at 1-1.9s, 2.7-5s, and 5.9-10s,you can consider that from 1-10s there were always two people in the shot.  " + \
            "Please ensure that the time continuity of events across nodes is respected when answering the question. Please ensure that the time continuity of events across nodes is respected when answering the question. If the duration of something is asked, you can count by connecting the segments as described above (where events within a 1-second interval are treated as continuous), and calculate the total duration across multiple segments. This means if an event spans multiple nodes and involves overlapping time intervals, you should consider the total span of the event as continuous, and compute the duration accordingly, even if the event is split across different video segments(interval within 1 second). " + \
            " If the question regards of duration of some thing, return the answer With current knowledge. Do not search further."+ \
            " If the information is enough to infer the answer, return the answer immediately without searching further.The answer should include day and place information of the node. Do not search further unless the information is COMPLETELY insufficient."+ \
            f" If current knowledge include one of the required time/places,then return answer regarding current time/places. If no nodes match one of the specified time/place criteria, directly respond with answer:'not found in place(current knowlegde place fullname) on day(current knowlegde day fullname)'.  Additionally, all sub-nodes within the current node's knowledge base are guaranteed to contain content related only to the same date and place as the current node. Therefore, when searching within sub-nodes, you may assume that they are consistent with the current date ({day}) and place ({place}).If you believe that the knowledge is insufficient because part of the question pertains to a time/place not covered by the current knowledge, provide the answer based solely on the available knowledge. Do not continue searching. " 
   
    prompt += """
    If the question asks for information about multiple times or places (e.g., Day 1 and Day 2, Office A and Office B),
    but the current knowledge only contains one of the times/places, provide the answer based on the available knowledge.
      If the question asks for a value that spans multiple days or places, but the current knowledge only includes information for one of those days/places, return the answer for the matching day/place with day/place information and ignore the non-matching part. If the question ask for time when in the available situation(e.g. ask for person in B when A contains 2 people,and A information is available but B is not, then you can return the time when A contains two people.)
    For example, if the question asks about sum of number of people on Day 1 and Day 2, but the knowledge only contains information about Day 1(information of different day or place is not included in the sub_nodes), then return the number of people on Day 1 rather than search for more nodes. """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a question-answering assistant. Based on the following knowledge, determine if it is sufficient to answer the question. If sufficient, provide the answer in JSON {'answer': answer}. If not, return a list of indices of nodes (no more than 10 nodes)that might contain the answer in JSON {'nodes_of_interest': [list_of_indices]}. If the information is enough to infer the answer, return the answer immediately without searching further. Do not search further unless the information is COMPLETELY insufficient."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return response

def search_and_respond_multiple_trees(tree_paths, question, question_type, options=None):
    """
    主搜索和回答函数：在多个视频树中寻找答案。
    
    参数:
        tree_paths (list): 视频树的路径列表（pickle 文件）。
        question (str): 用户提出的问题。
        question_type (str): 问题类型（如 'duration', 'judge', 'comparison'）。
        options (dict, optional): 答案选项（仅在 question_type='comparison' 时需要）。
    
    返回:
        str: 最终答案。
    """
    def traverse_and_match(node_list,day,place):
        """
        递归地搜索和匹配树中的节点，询问大模型是否能回答问题，若不能，则返回感兴趣的子节点。
        
        参数:
            node_list (list): 当前层的节点列表。
            threshold (float): 选择相关节点的最小评分阈值。
            search_width (int): 每一层最多搜索的节点数。
        
        返回:
            str: 最终的答案，或者返回感兴趣的节点列表。
        """
        current_level = node_list
        
        while current_level:
            captions = []
            for i in range(len(current_level)):
                node = current_level[i]
                captions.append(format_information(node,i,day,place))
            response = generate_response(captions,question,day,place)
            

            # 获取模型返回的内容
            response_content = response.choices[0].message.content
            
            response_content = json.loads(response_content)

            print(f'response:{response_content}')
            if "answer" in response_content:
                return response_content["answer"]  # 如果模型认为知识足够，直接返回答案

            # 如果模型认为知识不够，返回感兴趣的节点列表
            nodes_of_interest_ = response_content["nodes_of_interest"]
            nodes_of_interest_num = []
            for x in nodes_of_interest_:
                if (float(x)<len(current_level)):
                    nodes_of_interest_num.append(x)
            
            if not nodes_of_interest_num:
                return "no matching node"
            print(f'current_level={len(current_level)},nodes of interest={nodes_of_interest_num}')
            nodes_of_interest = [current_level[i] for i in nodes_of_interest_num]
            # 获取感兴趣节点的子节点，继续搜索
            next_level = []
            for node in nodes_of_interest:
                if "sub_segments" in node.keys() and node["sub_segments"] and node["sub_segments"]!=[]:
                    for x in node["sub_segments"]:
                        next_level.append(x)

            if (next_level == []):
                return "no matching node"

            # 继续在下一层进行搜索
            current_level = next_level
        
        return "no matching node"

    print(question)
    # 初始化全局知识库
    global_knowledge_base = []

    # 遍历每棵树
    for i,tree_path in enumerate(tree_paths):
        with open(tree_path, 'rb') as f:
            tree = pickle.load(f)
        day=i%3+1
        place=int(i/3)+1
        offi = {1:'A',2:'B',3:'C'}
        place = offi[place]
        # 从树根开始搜索
        node_list = tree["sub_segments"]
        filtered_node_list = node_filter(question,day,place)
        if(filtered_node_list=="Yes"):
            print(f'day={day},place={place}:')
        if(filtered_node_list == "Yes"):
            result = traverse_and_match(node_list,day,place)
            print(f'tree_res={result}')
            if result != "no matching node":
                global_knowledge_base.append(result)

    # 如果全局知识库为空，返回无匹配节点
    if not global_knowledge_base:
        return "No matching knowledge across all trees."
    
    # 整合所有树的知识基础，向模型生成最终答案
    global_knowledge_base = [str(x) for x in global_knowledge_base]
    combined_knowledge = "\n".join(global_knowledge_base)
    output = format_output(question, combined_knowledge, question_type, options)
    output_content = json.loads(output.choices[0].message.content)

    return output_content["answer"]

# if __name__ == "__main__":
#     # 示例：多个视频树路径
#     test_day = [1,2,6,15,16,17,18,19,20]
#     tree_paths = ['./preprocess1/day_'+str(x)+'.avi/segment_video.pkl' for x in test_day]
    
#     question = "On day2,in office 1, was there anyone who stand for over 10 senconds?"
#     question_type = 'judge'
    
#     answer = search_and_respond_multiple_trees(tree_paths, question, question_type)
#     print("Final Answer:", answer)










    
    
    

