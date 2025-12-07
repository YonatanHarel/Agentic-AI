
""" 
Planner agent - responsible for taking a query 
and execute several search agents who run based on 
that query in order to do deep reasearch.
"""

from agents import Agent
from pydantic import BaseModel, Field


HOW_MANY_SEARCHES = 3

INSTRUCTIONS = f"""You are a helpful research assistant. Given a query, come up with a set of web searches 
to perform to best answer the query. Output {HOW_MANY_SEARCHES} term to query for. """

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important th the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

planner_agent = Agent(
    name="Planner agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan
    )