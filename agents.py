from crewai import Agent
import os
from tools.video_tree_search_tool import VideoTreeSearchTool
import datetime

import dotenv

# define llm 
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

os.environ.setdefault('OPENAI_MODEL_NAME', 'gpt-4o')



date = datetime.datetime.now().strftime("%Y-%m-%d")

class VideoAnalysisAgents():
    def extract_keywords_agent(self):
      return Agent(
            role='keywords_extracter',
            goal=f"""
Extract key information from the question and return a JSON array (may contain more than one item):
1. "entity" (the subject, such as a person or an object. For example, "no person" means no one is involved; "one person" means one person; "two person" means two people, and so on)
2. "behavior" (the action or activity)
3. "time" (the time when the behavior occurs, such as morning or afternoon. It can also be a specific time, like 7:30. If no time is mentioned, return "any time")
4. "location" (the place where it happens, if mentioned; otherwise, return "unknown")
5. "date" (the date)

            """,
            backstory="""The most seasoned keyword extracter based on the input question.""",
            verbose=True,
            tools=[
                # BrowserTools.scrape_and_summarize_website,
                # SearchTools.search_internet,
            ]
        )
    def VideoFilter(self):
      return Agent(
            role='a video Filter',
            goal="""
            Please select ALL matching videopath relative to question based on video information given. If the day and place mentioned in the question match the specific current day and place.
            return the json of ALL pkl path of matching video.

          - If the question asks for a specific day (e.g., day 1) and a specific place (e.g., office 2), match information of video exactly.
          - If the question asks for a range of days (e.g., from day 1 to day 3) or range of place(e.g. office2 and 3), tell if the day or place is within that range(means match).
          - If the question asks for all days and places (e.g., all offices or all days), match any day and any place.
    
            Provide the answer of All path of relative video in JSON ,for example [{'path':'./videotrees/day1.pkl'},{'path':'./videotrees/day2.pkl'}]
            """,
            backstory="""The most seasoned video Filter based on the input question and video information.""",
            verbose=True
            # allow_delegation=True
      )
    def ReflectionAgent(self):
      return Agent(
            role='an Agent that can reflect the answer from videofilter on whether current decision is correct.',
            goal="""
            your coworker videofilter have select relative video based on the question.Please reflect whether correct decision was made.The rules of selection are as follows:
            Please select ALL matching videopath relative to question based on video information given should be selected. 

          - If the question asks for a specific day (e.g., day 1) and a specific place (e.g., office 2), match information of video exactly.
          - If the question asks for a range of days (e.g., from day 1 to day 3) or range of place(e.g. office2 and 3), tell if the day or place is within that range(means match).
          - If the question asks for all days and places (e.g., all offices or all days), match any day and any place.
          Tell your coworker VideoFilter if the selection is correct.
            """,
            backstory="""The most seasoned Reflection Agent.""",
            verbose=True
            # allow_delegation=True
      )
    
    def TreeSearcher(self):
     return Agent(
      role="the agent that uses tool to search through video tree to get the answer of the question.",
      goal="Use videotreesearch tool to analyse tree structure.the input parameters of tool should be information from VideoFilter(json list) and question(str)",
      backstory="extract information from tree structure efficiently and get key information.",
      tools=[VideoTreeSearchTool()],
      # allow_code_execution=True,
      verbose=True
      )
    
    def ResultMerger(self):
      return Agent(
            role='a result merger who merges answers from different videos and respond to the question.',
            goal="""sum up the answer from single video provided by your coworker TreeSearcher ,and generate fianl analysis.If the question contains options, then select the closest answer and only respond the choice, else just sum up and respond the answer.
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
              "result": "No"
            }
            ]
            then return should be ONLY "A", NOT "A:yes".
            """,
            backstory="""proficient in gathering information and output structured and comprehensive summary.""",
            verbose=True
      )

      
  
if __name__ == "__main__":
  pass