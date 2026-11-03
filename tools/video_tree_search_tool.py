# tools/video_tree_search_tool.py
from crewai.tools import BaseTool
import pickle
from pathlib import Path
import json
import os
from pydantic import BaseModel
from typing import List, Dict
from typing import Type

class TreeSearchInput(BaseModel):
    tree_paths: List[Dict[str, str]]
    question: str

class VideoTreeSearchTool(BaseTool):
# class VideoTreeSearchTool():
    name:str = "video_tree_search_tool"
    description:str = "Searches through hierarchical video tree (pkl) to answer a question step by step.the input parameters are information(json list) and question(str) "
    args_schema: Type[BaseModel] = TreeSearchInput

    def _run(self, tree_paths: List[Dict[str, str]], question: str)->str:
        return self.search_and_respond_multiple_trees(tree_paths, question)

    def search_and_respond_multiple_trees(self, tree_paths, question):
        def format_information(node, index, information):
            # return f"[{index}] {node.get('description', '')} ({information})"
            # format_inf = f"In [{index}]({information}): at {node['time']}(second),{node['caption']} "
            format_inf = f"In [{index}]({information}): at {node['time']}(second),the people information is:{node['person_id']}.The caption is:{node['caption']} "
            return format_inf

        def generate_response(captions, question, information):
            from openai import OpenAI
            client = OpenAI()
            # print(f'caption[0]={captions[0]}\n')
            prompt = "answer the question based on current captions."
            
            """If you cannot answer yet, return a JSON with a list of `nodes_of_interest`, which are indices of the segments worth exploring further. 
            If you can answer, return a JSON like {{ "answer": "..." }}."""

            prompt = " Each node's sub-segments provide more detailed descriptions of the current node. If the provided knowledge is enough to answer the question, respond with the answer in JSON {'answer': answer}. If not, respond with a list of indices (starting from 0) of current nodes(the index sequence of caption starting from 0) that its sub_segment might contain the answer(no more than 10 nodes).respond in JSON {'nodes_of_interest': [list_of_indices]}."+ \
            "Additionally, if there are events occurring in multiple nodes within a 1-second interval, treat them as continuous. " + \
            "For example, if two people are present in nodes at 1-1.9s, 2.7-5s, and 5.9-10s,you can consider that from 1-10s there were always two people in the shot.  " + \
            " If the information is enough to infer the answer, return the answer immediately without searching further.The answer should include day and place information of the node. Do not search further unless the information is COMPLETELY insufficient."
   
            prompt += """
            If the question asks for information about multiple times or places (e.g., Day 1 and Day 2 in Office A ),
            but the current knowledge only contains one of the times/places, provide the answer based on the available knowledge.
            If the question asks for a value that spans multiple days or places, but the current knowledge only includes information for one of those days/places, return the answer for the matching day/place with day/place information and ignore the non-matching part.
            For example, the question ask for if there was anyone sitting both in July 1st and 2nd in office A,and current node is only about July 1st office A,then just answer if there was anyone sitting in July 1st office A.
            """
            prompt += """For example, if the question is "Was there anyone sitting in office A on day 1? If you can answer the question, return{'answer':'Yes,someone is sitting in office A on day 1'}.If not, return{'nodes_of_interst':[0,2,5]}"""

            prompt += f"""Follow the rules above, now you are analyzing video segments for {information}. Answer the question: "{question}.
            You are given the following segments:\n\n""" + "\n".join(captions)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response

        def traverse_and_match(node_list,question,information):
            current_level = node_list

            while current_level:
                captions = [format_information(node, i, information) for i, node in enumerate(current_level)]
                response = generate_response(captions, question, information)
                response_content = json.loads(response.choices[0].message.content)
                # print(f'response={response_content}')
                if "answer" in response_content:
                    return response_content["answer"]

                nodes_of_interest_ = response_content.get("nodes_of_interest", [])
                nodes_of_interest_num = []
                for x in nodes_of_interest_:
                    if type(x) is int or (isinstance(x, str) and x.isdecimal()):
                        index = int(x)
                        if 0 <= index < len(current_level):
                            nodes_of_interest_num.append(index)

                if not nodes_of_interest_num:
                    return "no matching node"

                nodes_of_interest = [current_level[i] for i in nodes_of_interest_num]
                next_level = []
                for node in nodes_of_interest:
                    if "sub_segments" in node and node["sub_segments"]:
                        next_level.extend(node["sub_segments"])

                if not next_level:
                    return "no matching node"
                
                current_level = next_level

            return "no matching node"

        # 多视频搜索入口
        all_results = []
        for path_info in tree_paths:
            path = path_info["path"]
            information = path_info["information"]
            # Model-selected paths must stay inside this project.
            project_root = Path(__file__).resolve().parents[1]
            tree_path = (project_root / path.replace("\\", "/")).resolve()
            if not tree_path.is_relative_to(project_root) or tree_path.suffix != ".pkl":
                raise ValueError("Video tree must be a .pkl file inside the project directory")
            # Pickle files must come from a trusted source.
            with tree_path.open("rb") as f:
                tree = pickle.load(f)
            result = traverse_and_match(tree["sub_segments"],question, information+' path:'+path)
            print(result)
            all_results.append({"information":path_info["information"],"path": path, "result": result})
        return json.dumps(all_results, indent=2)
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    os.environ.setdefault('OPENAI_MODEL_NAME', 'gpt-4o')
    a = VideoTreeSearchTool()
    
    res = a._run([{"information":"July 1st ,office A","path":"./tree/day_1.avi/segment_video.pkl"},
                #   {"information":"July 2nd ,office A","path":"./tree/day_2.avi/segment_video.pkl"}
                  ],
        #    " Did the situation when someone was standing happened both on July 1st and 2nd in office A?"
        # " Did the situation when someone was sitting happened  on July 1st  in office A?"
        " Was there anyone sitting on July 1st  in office A?"
           )
    print(res)
    print(type(res))
    res = str(res)
    print(res)