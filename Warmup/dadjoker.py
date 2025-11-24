from dotenv import load_dotenv
import os
import asyncio
from agents import Agent, Runner, trace

load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')

async def joker():
    agent = Agent(
        name="DadJoker",
        instructions="You are comedian",
        model="gpt-4o-mini",
    )

    with trace("DadJoker"):
        result = await Runner.run(agent, "Tell me a dad joke")
        print(result.final_output)

if __name__ == '__main__':
    asyncio.run(joker())