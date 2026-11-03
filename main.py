from crewai import Crew
from textwrap import dedent
import json
from agents import VideoAnalysisAgents
from tasks import VideoAnalysisTasks
import os
from dotenv import load_dotenv
from typing import Type
load_dotenv()

class VideoForestcrew:

  def run(self,question,video_information):
    agents = VideoAnalysisAgents()
    tasks = VideoAnalysisTasks()

    video_filter = agents.VideoFilter()
    tree_searcher = agents.TreeSearcher()
    reflect_agent = agents.ReflectionAgent()
    result_merger = agents.ResultMerger()

    select_video_task = tasks.select_videos(video_filter,question,video_information)
    reflect_selection = tasks.reflect_selection(reflect_agent,question,video_information)
    search_tree_task = tasks.search_tree(tree_searcher,question)
    merge_result = tasks.merge_result(result_merger,question)
    # research_analyst_agent = agents.research_analyst()
    # financial_analyst_agent = agents.financial_analyst()
    # investment_advisor_agent = agents.investment_advisor()

    # research_task = tasks.research(research_analyst_agent)

    # recommend_task = tasks.recommend(investment_advisor_agent)

    crew = Crew(
      agents=[
        video_filter,
        reflect_agent,
        tree_searcher,
        result_merger

      ],
      tasks=[
        select_video_task,
        reflect_selection,
        search_tree_task,
        merge_result
      ],
      verbose=True,
      collect_usage = True
    )

    result = crew.kickoff()
    self.latest_usage = crew.usage_metrics if hasattr(crew, 'usage_metrics') else {}
    return result

if __name__ == "__main__":

  # 获取当前脚本所在目录
  current_dir = os.path.dirname(os.path.abspath(__file__))
  json_path = os.path.join(current_dir, './video_information.json')
  with open(json_path, 'r') as f:
    data = json.load(f)
  video_information = json.dumps(data, indent=4)

  videoforest_crew = VideoForestcrew()
  question = "On July 1st or 2nd, in office A was there any period when there is at least 1 person in the room?"

  result = videoforest_crew.run(question,video_information)
  print(result,type(result))
  result = str(result)
  print(result,type(result))
  print(f'result = \n{result}\n')
