from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
import pandas as pd

class MMAAnalysisAgent:
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(model="mistral")  # You can switch to other models like "llama2"
        
        # Define tools the agent can use
        self.tools = [
            Tool(
                name="FightStats",
                func=self._analyze_fight_stats,
                description="Analyzes fighter statistics including strikes, takedowns, and control time"
            ),
            Tool(
                name="FighterHistory",
                func=self._get_fighter_history,
                description="Retrieves and analyzes a fighter's past performance"
            )
        ]
        
        # Load prompt template
        self.prompt = hub.pull("hwchase17/react")
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def _analyze_fight_stats(self, fight_data: dict) -> str:
        """
        Analyzes fight statistics and returns insights
        """
        # This is a placeholder - we'll expand this with actual analysis logic
        template = """
        Analyze the following MMA fight statistics and provide insights:
        Fighter Stats: {stats}
        
        Consider:
        1. Strike accuracy and volume
        2. Takedown efficiency
        3. Ground control time
        4. Significant moments
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["stats"]
        )
        
        return self.llm.invoke(prompt.format(stats=str(fight_data)))
    
    def _get_fighter_history(self, fighter_name: str) -> str:
        """
        Retrieves fighter's historical data
        """
        # Placeholder - will be replaced with actual data fetching logic
        return f"Retrieved fight history for {fighter_name}"
    
    def analyze_fight(self, fight_data: dict) -> str:
        """
        Main method to analyze a fight
        """
        return self.agent_executor.invoke({
            "input": f"Analyze this fight data: {fight_data}"
        })

# Example usage
if __name__ == "__main__":
    # Sample fight data
    sample_fight = {
        "fighter1": {
            "name": "Fighter A",
            "strikes_landed": 89,
            "strikes_attempted": 211,
            "takedowns": 2,
            "takedown_attempts": 5,
            "control_time": "3:45"
        },
        "fighter2": {
            "name": "Fighter B",
            "strikes_landed": 76,
            "strikes_attempted": 182,
            "takedowns": 1,
            "takedown_attempts": 3,
            "control_time": "2:30"
        }
    }
    
    # Create and use the agent
    agent = MMAAnalysisAgent()
    analysis = agent.analyze_fight(sample_fight)
    print(analysis)