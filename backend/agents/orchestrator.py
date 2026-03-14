from google.adk.agents import SequentialAgent
from agents.copy_agent import copy_agent
from agents.visual_agent import visual_agent
from agents.video_agent import video_agent
from agents.social_agent import social_agent
from agents.strategy_agent import strategy_agent

root_agent = SequentialAgent(
    name="pitchforge_orchestrator",
    description="Full marketing campaign generator",
    sub_agents=[strategy_agent, copy_agent, visual_agent, video_agent, social_agent]
)
