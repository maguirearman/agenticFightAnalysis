# src/analysis/mma_agent.py

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from typing import Dict, List
import json

class MMAAnalysisAgent:
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(model="mistral")
        self.current_fight_data = None
        
        # Define analysis tools
        self.tools = [
            Tool(
                name="StyleMatchupAnalysis",
                func=self._analyze_style_matchup,
                description="Analyzes fighting style matchup between two fighters"
            ),
            Tool(
                name="StatisticalComparison",
                func=self._compare_statistics,
                description="Compares key statistics between fighters"
            ),
            Tool(
                name="FormAnalysis",
                func=self._analyze_recent_form,
                description="Analyzes fighters' recent performances"
            )
        ]
        
        # Create the agent with React framework
        self.prompt = hub.pull("hwchase17/react")
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

    def _analyze_style_matchup(self, fight_data_str: str) -> str:
        """
        Analyzes the stylistic matchup between fighters
        """
        # Convert the fight_data string back to a dictionary
        fight_data = self.current_fight_data
        template = """
        Analyze the fighting style matchup between these fighters:
        
        Fighter 1: {fighter1_name}
        - Stance: {fighter1_stance}
        - Strike Rate: {fighter1_slpm} strikes per minute
        - Takedown Rate: {fighter1_td} per 15 minutes
        
        Fighter 2: {fighter2_name}
        - Stance: {fighter2_stance}
        - Strike Rate: {fighter2_slpm} strikes per minute
        - Takedown Rate: {fighter2_td} per 15 minutes
        
        Consider:
        1. Stance matchup advantages
        2. Distance management implications
        3. Offensive vs defensive tendencies
        4. Grappling vs striking preferences
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_stance", "fighter1_slpm", "fighter1_td",
                "fighter2_name", "fighter2_stance", "fighter2_slpm", "fighter2_td"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_stance=f1['stats']['stance'],
            fighter1_slpm=f1['stats']['striking_stats']['strikes_landed_per_min'],
            fighter1_td=f1['stats']['grappling_stats']['takedowns_per_15min'],
            fighter2_name=f2['name'],
            fighter2_stance=f2['stats']['stance'],
            fighter2_slpm=f2['stats']['striking_stats']['strikes_landed_per_min'],
            fighter2_td=f2['stats']['grappling_stats']['takedowns_per_15min']
        ))

    def _compare_statistics(self, fight_data_str: str) -> str:
        """
        Provides statistical comparison between fighters
        """
        # Use the stored fight data
        fight_data = self.current_fight_data
        template = """
        Compare the statistical advantages between:
        
        {fighter1_name}:
        - Strike Accuracy: {fighter1_acc}
        - Strike Defense: {fighter1_def}
        - TD Accuracy: {fighter1_td_acc}
        - TD Defense: {fighter1_td_def}
        
        {fighter2_name}:
        - Strike Accuracy: {fighter2_acc}
        - Strike Defense: {fighter2_def}
        - TD Accuracy: {fighter2_td_acc}
        - TD Defense: {fighter2_td_def}
        
        Analyze:
        1. Striking efficiency differences
        2. Defensive capabilities
        3. Grappling effectiveness
        4. Overall statistical advantages
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_acc", "fighter1_def", "fighter1_td_acc", "fighter1_td_def",
                "fighter2_name", "fighter2_acc", "fighter2_def", "fighter2_td_acc", "fighter2_td_def"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_acc=f1['stats']['striking_stats']['striking_accuracy'],
            fighter1_def=f1['stats']['striking_stats']['defense'],
            fighter1_td_acc=f1['stats']['grappling_stats']['takedown_accuracy'],
            fighter1_td_def=f1['stats']['grappling_stats']['takedown_defense'],
            fighter2_name=f2['name'],
            fighter2_acc=f2['stats']['striking_stats']['striking_accuracy'],
            fighter2_def=f2['stats']['striking_stats']['defense'],
            fighter2_td_acc=f2['stats']['grappling_stats']['takedown_accuracy'],
            fighter2_td_def=f2['stats']['grappling_stats']['takedown_defense']
        ))

    def _analyze_recent_form(self, fight_data_str: str) -> str:
        """
        Analyzes fighters' recent performances
        """
        # Use the stored fight data
        fight_data = self.current_fight_data
        template = """
        Analyze recent fight history and form:
        
        {fighter1_name}:
        Record: {fighter1_record}
        Recent Fights:
        {fighter1_recent}
        
        {fighter2_name}:
        Record: {fighter2_record}
        Recent Fights:
        {fighter2_recent}
        
        Consider:
        1. Recent win/loss trends
        2. Quality of opposition
        3. Performance consistency
        4. Current momentum
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_record", "fighter1_recent",
                "fighter2_name", "fighter2_record", "fighter2_recent"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_record=f1['stats']['record'],
            fighter1_recent=json.dumps(fight_data['matchup_details']['recent_fights']['fighter1'], indent=2),
            fighter2_name=f2['name'],
            fighter2_record=f2['stats']['record'],
            fighter2_recent=json.dumps(fight_data['matchup_details']['recent_fights']['fighter2'], indent=2)
        ))

    def analyze_fight(self, fight_data: Dict) -> Dict:
        """
        Main method to analyze a fight
        """
        # Store the fight data as an instance variable so tools can access it
        self.current_fight_data = fight_data
        
        return self.agent_executor.invoke({
            "input": f"Analyze the upcoming fight between {fight_data['fighter1']['name']} and {fight_data['fighter2']['name']}"
        })