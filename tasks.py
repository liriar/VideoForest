from crewai import Task
import datetime
from pydantic import BaseModel
from typing import List
date = datetime.datetime.now().strftime("%Y-%m-%d")


class VideoInfo(BaseModel):
    information:str
    path: str
class VideoInfoList(BaseModel):
    videos: List[VideoInfo]

class VideoAnalysisTasks():
  def extract_keywords(self,agent,question):
    return Task(description= f"""
    从以下问题中提取关键信息，返回 JSON 数组：
    1. "entity"（主体，如某人、某物。如果是“no person”，表示没有人参与；"one person" 表示一个人；"two person" 表示两个人，以此类推）
    2. "behavior"（行为）
    3. "time"（时间，行为发生的时间。比如上午或者下午。也可以是准确的时刻，比如7点30分。如果没有提到时间的话，那就是"any time"）
    4. "location"（地点，如果有的话，否则返回 "unknown"）
    5. "date"（日期）

    示例：
    用户问题："On day2,in office A, was there anyone who stood for over 10 seconds?"
    返回：
    [
        {{"entity": "one person", "behavior": "stood for over 10 seconds", "time":"any time", "date": "day2", "location": "office A"}}
    ]

    Question: "Which event happened earlier at the time of that day: the first shot in July 1st office A with at least two people or the first shot in July 2nd office A with no one present?"
    return:
    [
        {{"entity": "two person", "behavior": "first shot", "time":"any time", "date": "July 1st", "location": "office A"}},
        {{"entity": "no person", "behavior": "first shot", "time":"any time", "date": "July 2nd", "location": "office A"}}
    ]

      """, 
        expected_output = "JSON 数组",
      agent=agent
    )
  
  def select_videos(self,agent,question,video_information):
    return Task(description= '''
   Please select ALL matching videopath relative to question based on video information given and the question. If the day and place mentioned in the question match the specific current day and place.
            return the json of ALL pkl path of matching video.

          - If the question asks for a specific day (e.g., day 1) and a specific place (e.g., office 2), match information of video exactly.
          - If the question asks for a range of days (e.g., from day 1 to day 3) or range of place(e.g. office2 and 3), tell if the day or place is within that range(means match).
          - If the question asks for all days and places (e.g., all offices or all days), match any day and any place.
          - If the question or the options asks directly for specific video, match the videos.
    
            Provide the answer of All path of relative video in JSON ,for example 
            [
            {'path':'./videotrees/day1.pkl'},
            {'path':'./videotrees/day2.pkl'}
            ]
    example1：
    question："On day2,in office A, was there anyone who stood for over 10 seconds?"
    video_information:    [
        {"information": "day2,office A","path":"./video1.pkl"},
        {"information": "day2,office B","path":"./video2.pkl"}
    ]
    return：
    [
        {"information": "day2,office A","path":"./video1.pkl"}
    ]
    example2：
    Question: "Which event happened earlier at the time of that day: the first shot in July 1st office A with at least two people or the first shot in July 2nd office A with no one present?"
    video_information:    [
        {"information": "July 1st, office A","path":"./video1.pkl"},
        {"information": "July 2nd, office A","path":"./video2.pkl"}
    ]
    return:
    [
        {"information": "July 1st, office A","path":"./video1.pkl"},
        {"information": "July 2nd, office A","path":"./video2.pkl"}
    ]

    example3：
    video_information:    [
        {"information": "any", "path":"./video1.pkl"},
        {"information": "any", "path":"./video2.pkl"}
    ]
    question": "Which video is about the Zumba action?
            "A": "Carving_jack-o-lanterns\\v_K1tK7kNDQZg.mp4",
            "B": "Archery\\v_81hhcWrkRcE.mp4",
            "C": "Zumba\\v_C9fJiD_j8Xg.mp4"
    "
    return:
    [
        {"information": "any", "path":"./Carving_jack-o-lanterns\\v_K1tK7kNDQZg.mp4"},
        {"information": "any", "path":"./Archery\\v_81hhcWrkRcE.mp4"},
        {"information": "any", "path":"./video2.pkl"}
    ]
    '''+f' now the question is{question},video_information is {video_information}.'
    +"After selecting the video, pass the answer to your coworker ReflectAgent to ensure the selection is right(give the answer to ReflectAgent).If ReflectAgent tells the answer is wrong ,you need to select again and pass the answer to ReflectAgent again until ReflectAgent tells its right."
    "If ReflectAgent tells the answer is correct,you can move on and pass the answer to TreeSearcher."
    , 
      expected_output = "JSON list",
      agent=agent,
      output_pydantic=VideoInfoList
    )
  
  def reflect_selection(self,agent,question,video_information):
    return Task(description= '''
            your coworker videofilter have select relative video based on the question.Please reflect whether correct decision was made.The rules of selection are as follows:
            Please select ALL matching videopath relative to question based on video information given should be selected. 

          - If the question asks for a specific day (e.g., day 1) and a specific place (e.g., office 2), match information of video exactly.
          - If the question asks for a range of days (e.g., from day 1 to day 3) or range of place(e.g. office2 and 3), tell if the day or place is within that range(means match).
          - If the question asks for all days and places (e.g., all offices or all days), match any day and any place.
          Tell your coworker if the selection is correct or not.
    '''+f' the question is{question},and videos to be selected are {video_information}.Please tell if the answer from videofilter is correct and pass the result back to videofilter.'
    , 
      expected_output = "Answer if the selection is correct or not",
      agent=agent,
      output_pydantic=VideoInfoList
    )
  
  def search_tree(self,agent,question):
    return Task(
    description="""Use the video_tree_search_tool to search for the answer of the question. the information of needed video is given by your coworker VideoFilter.the input parameters of tool should be class TreeSearchInput(BaseModel):
    information: List[Dict[str, str]]
    question: str.
    For example, the information from VideoFilter is [
        {"information": "day2,office A","path":"./video1.pkl"}
    ]
    and question is :" Was there anyone sitting on July 1st  in office A?"
    then when using  the tool (if _run is the function),it should be _run([{"information": "day2,office A","path":"./video1.pkl"}]," Was there anyone sitting on July 1st  in office A?")
    then return the answer list from the tool.
    """+f'now the question is {question}.pass the answer to your coworker to ResultMerger.',

    expected_output="answer list",
    agent=agent
  )

  def merge_result(self,agent,question):
    return Task(
    description="""sum up the answer from videos provided by your coworker TreeSearcher ,and generate fianl analysis.If the question contains options, then select the closest answer and only respond the choice, else just sum up and respond the answer.
            For example,the question is:" Did the situation when someone was standing happened both on July 1st and 2nd in office A? A:Yes B:No"
            and the information from TreeSearcher is :result =
            [
            {
              "information": "July 1st ,office A",
              "path": "./tree/day_1.avi/segment_video.pkl",
              "result": "Yes"
            },
            {
              "information": "July 2nd ,office A",
              "path": "./tree/day_2.avi/segment_video.pkl",
              "result": "Yes"
            }
            ]
            then return should be ONLY "A", NOT "A:yes".
            If there is no enough information,just guess an answer or choose the one which is closest to the answer.
            """+f'now the question is{question}',

    expected_output="string",
    agent=agent
  )


