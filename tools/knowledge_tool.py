# tools/knowledge_tool.py

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel
from myclass import KnowledgeBase

# 单例模式实现（确保全局唯一知识库实例）
class GlobalKnowledgeBase:
    _instance = None

    @staticmethod
    def get_instance():
        if GlobalKnowledgeBase._instance is None:
            kb = KnowledgeBase()
            kb.load_from_json()  # 初始化时尝试加载
            GlobalKnowledgeBase._instance = kb
        return GlobalKnowledgeBase._instance


# 输入结构
class KnowledgeInput(BaseModel):
    entity: str
    behavior: str
    time: str
    date: str
    location: str
    query: str  # 原始问题


class KnowledgeUpdateInput(KnowledgeInput):
    confidence: int = 1


# 工具类：搜索
class KnowledgeSearchTool(BaseTool):
    name = "knowledge_search_tool"
    description = "使用已有知识条目查询当前问题是否可以回答。返回 Right / Partially Valid / Invalid / Wrong。"
    args_schema: Type[BaseModel] = KnowledgeInput

    def _run(self, entity, behavior, time, date, location, query):
        kb = GlobalKnowledgeBase.get_instance()
        result = kb.find_entry(entity, behavior, time, date, location)
        return result


# 工具类：更新
class KnowledgeUpdateTool(BaseTool):
    name = "knowledge_update_tool"
    description = "用于在分析视频结果后，将新信息写入知识库中。"
    args_schema: Type[BaseModel] = KnowledgeUpdateInput

    def _run(self, entity, behavior, time, date, location, query, confidence=1):
        kb = GlobalKnowledgeBase.get_instance()
        kb.add_entry(entity, behavior, time, date, location, confidence)
        kb.save_to_json()
        return f"Updated knowledge base with: entity={entity}, behavior={behavior}, time={time}, date={date}, location={location}, confidence={confidence}"
