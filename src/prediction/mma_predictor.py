# src/prediction/mma_predictor.py

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from typing import Dict, List, Tuple
import json

class MMAFightPredictor:
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(model="mistral")
        self.current_fight_data = None
        
        # Define prediction tools
        self.tools = [
            Tool(
                name="MomentumAnalysis",
                func=self._analyze_momentum,
                description="Analyzes fighters' career momentum and trajectory"
            ),
            Tool(
                name="MatchupAdvantages",
                func=self._analyze_matchup_advantages,
                description="Identifies key matchup advantages between fighters"
            ),
            Tool(
                name="StatisticalEdge",
                func=self._calculate_statistical_edge,
                description="Calculates statistical advantages and edge between fighters"
            ),
            Tool(
                name="StyleCounterAssessment",
                func=self._assess_style_counters,
                description="Assesses how each fighter's style counters the opponent's approach"
            )
        ]
        
        # Custom prompt for prediction agent
        prediction_template = """You are an expert MMA fight predictor tasked with determining the likely winner of an upcoming bout.
        Use the available tools to analyze different aspects of the matchup, then provide a prediction with a confidence level.
        
        When making your prediction, consider:
        1. Statistical advantages
        2. Stylistic matchups
        3. Recent form and momentum
        4. Historical performance against similar opponents
        5. Physical attributes and advantages
        
        For your final answer, include:
        - Your predicted winner
        - Confidence level (Low/Medium/High)
        - Key factors that led to your prediction
        - Potential paths to victory for both fighters
        - Any critical variables that could dramatically change the outcome
        
        {format_instructions}
        
        Human: {input}
        AI: """
        
        # Create the prediction agent
        self.prompt = PromptTemplate.from_template(prediction_template)
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def _analyze_momentum(self, fight_data_str: str) -> str:
        """
        Analyzes fighters' career momentum and recent trajectory
        """
        fight_data = self.current_fight_data
        template = """
        Analyze the career momentum for both fighters:
        
        {fighter1_name}:
        Record: {fighter1_record}
        Recent Fights: {fighter1_recent}
        
        {fighter2_name}:
        Record: {fighter2_record}
        Recent Fights: {fighter2_recent}
        
        Consider:
        1. Win/loss streaks
        2. Quality of recent opposition
        3. Performance improvements or declines
        4. Recovery from losses
        5. Activity level and layoffs
        
        Determine which fighter has more positive momentum coming into this fight.
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

    def _analyze_matchup_advantages(self, fight_data_str: str) -> str:
        """
        Identifies key matchup advantages between fighters
        """
        fight_data = self.current_fight_data
        template = """
        Analyze the specific matchup advantages between:
        
        {fighter1_name}:
        - Stance: {fighter1_stance}
        - Striking: {fighter1_slpm} strikes per minute
        - Takedowns: {fighter1_td} per 15 minutes
        - Submissions: {fighter1_sub} per 15 minutes
        
        {fighter2_name}:
        - Stance: {fighter2_stance}
        - Striking: {fighter2_slpm} strikes per minute
        - Takedowns: {fighter2_td} per 15 minutes
        - Submissions: {fighter2_sub} per 15 minutes
        
        Identify:
        1. Stance advantages (orthodox vs southpaw dynamics)
        2. Offensive output differentials
        3. Specific technical advantages
        4. Phase control advantages (striking vs grappling)
        5. Overall matchup dynamics
        
        Determine which fighter has more advantageous matchup factors.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_stance", "fighter1_slpm", "fighter1_td", "fighter1_sub",
                "fighter2_name", "fighter2_stance", "fighter2_slpm", "fighter2_td", "fighter2_sub"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_stance=f1['stats']['stance'],
            fighter1_slpm=f1['stats']['striking_stats']['strikes_landed_per_min'],
            fighter1_td=f1['stats']['grappling_stats']['takedowns_per_15min'],
            fighter1_sub=f1['stats']['grappling_stats']['submissions_per_15min'],
            fighter2_name=f2['name'],
            fighter2_stance=f2['stats']['stance'],
            fighter2_slpm=f2['stats']['striking_stats']['strikes_landed_per_min'],
            fighter2_td=f2['stats']['grappling_stats']['takedowns_per_15min'],
            fighter2_sub=f2['stats']['grappling_stats']['submissions_per_15min']
        ))

    def _calculate_statistical_edge(self, fight_data_str: str) -> str:
        """
        Calculates statistical advantages between fighters
        """
        fight_data = self.current_fight_data
        template = """
        Calculate the statistical edge between:
        
        {fighter1_name}:
        - Striking Accuracy: {fighter1_acc}
        - Striking Defense: {fighter1_def}
        - Strikes Landed/Min: {fighter1_slpm}
        - Strikes Absorbed/Min: {fighter1_sapm}
        - TD Accuracy: {fighter1_td_acc}
        - TD Defense: {fighter1_td_def}
        
        {fighter2_name}:
        - Striking Accuracy: {fighter2_acc}
        - Striking Defense: {fighter2_def}
        - Strikes Landed/Min: {fighter2_slpm}
        - Strikes Absorbed/Min: {fighter2_sapm}
        - TD Accuracy: {fighter2_td_acc}
        - TD Defense: {fighter2_td_def}
        
        Calculate:
        1. Net striking differential
        2. Offensive efficiency difference
        3. Defensive effectiveness difference
        4. Grappling control advantage
        5. Overall statistical edge percentage
        
        Determine which fighter has the greater statistical advantage and by what margin.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_acc", "fighter1_def", "fighter1_slpm", "fighter1_sapm", "fighter1_td_acc", "fighter1_td_def",
                "fighter2_name", "fighter2_acc", "fighter2_def", "fighter2_slpm", "fighter2_sapm", "fighter2_td_acc", "fighter2_td_def"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_acc=f1['stats']['striking_stats']['striking_accuracy'],
            fighter1_def=f1['stats']['striking_stats'].get('defense', 'N/A'),
            fighter1_slpm=f1['stats']['striking_stats']['strikes_landed_per_min'],
            fighter1_sapm=f1['stats']['striking_stats']['strikes_absorbed_per_min'],
            fighter1_td_acc=f1['stats']['grappling_stats']['takedown_accuracy'],
            fighter1_td_def=f1['stats']['grappling_stats']['takedown_defense'],
            fighter2_name=f2['name'],
            fighter2_acc=f2['stats']['striking_stats']['striking_accuracy'],
            fighter2_def=f2['stats']['striking_stats'].get('defense', 'N/A'),
            fighter2_slpm=f2['stats']['striking_stats']['strikes_landed_per_min'],
            fighter2_sapm=f2['stats']['striking_stats']['strikes_absorbed_per_min'],
            fighter2_td_acc=f2['stats']['grappling_stats']['takedown_accuracy'],
            fighter2_td_def=f2['stats']['grappling_stats']['takedown_defense']
        ))

    def _assess_style_counters(self, fight_data_str: str) -> str:
        """
        Assesses how each fighter's style counters the opponent
        """
        fight_data = self.current_fight_data
        template = """
        Assess style counter dynamics between:
        
        {fighter1_name}:
        - Stance: {fighter1_stance}
        - Record: {fighter1_record}
        - Striking Rate: {fighter1_slpm} strikes per minute
        - Takedown Rate: {fighter1_td} per 15 minutes
        
        {fighter2_name}:
        - Stance: {fighter2_stance}
        - Record: {fighter2_record}
        - Striking Rate: {fighter2_slpm} strikes per minute
        - Takedown Rate: {fighter2_td} per 15 minutes
        
        Analyze:
        1. How fighter 1's style specifically counters fighter 2's approach
        2. How fighter 2's style specifically counters fighter 1's approach
        3. History against similar stylistic opponents
        4. Adaptability factors for both fighters
        5. Whose style presents more problems for their opponent
        
        Determine whose fighting style creates more effective counters to their opponent's approach.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "fighter1_name", "fighter1_stance", "fighter1_record", "fighter1_slpm", "fighter1_td",
                "fighter2_name", "fighter2_stance", "fighter2_record", "fighter2_slpm", "fighter2_td"
            ]
        )
        
        f1 = fight_data['fighter1']
        f2 = fight_data['fighter2']
        
        return self.llm.invoke(prompt.format(
            fighter1_name=f1['name'],
            fighter1_stance=f1['stats']['stance'],
            fighter1_record=f1['stats']['record'],
            fighter1_slpm=f1['stats']['striking_stats']['strikes_landed_per_min'],
            fighter1_td=f1['stats']['grappling_stats']['takedowns_per_15min'],
            fighter2_name=f2['name'],
            fighter2_stance=f2['stats']['stance'],
            fighter2_record=f2['stats']['record'],
            fighter2_slpm=f2['stats']['striking_stats']['strikes_landed_per_min'],
            fighter2_td=f2['stats']['grappling_stats']['takedowns_per_15min']
        ))

    def predict_winner(self, fight_data: Dict) -> Dict:
        """
        Main method to predict the winner of a fight
        """
        # Store the fight data for tool access
        self.current_fight_data = fight_data
        
        result = self.agent_executor.invoke({
            "input": f"Predict the winner of the upcoming fight between {fight_data['fighter1']['name']} and {fight_data['fighter2']['name']} with confidence level and reasoning."
        })
        
        # Extract prediction details
        prediction = self._extract_prediction_details(result['output'], 
                                                     fight_data['fighter1']['name'], 
                                                     fight_data['fighter2']['name'])
        
        return {
            'prediction': prediction,
            'full_analysis': result['output']
        }
    
    def _extract_prediction_details(self, analysis: str, fighter1: str, fighter2: str) -> Dict:
        """
        Extract structured prediction data from the analysis text
        """
        # Default values
        prediction = {
            'predicted_winner': None,
            'confidence': 'Medium',
            'key_factors': [],
            'fighter1_path_to_victory': None,
            'fighter2_path_to_victory': None,
            'critical_variables': []
        }
        
        # Check for winner prediction
        if fighter1 in analysis and fighter2 in analysis:
            # Simple heuristic: who is mentioned more positively in the conclusion
            f1_mentions = analysis.lower().count(fighter1.lower())
            f2_mentions = analysis.lower().count(fighter2.lower())
            
            # This is a simple baseline - the LLM's actual prediction is in the text
            # A more robust implementation would use regex patterns or structured output
            if f1_mentions > f2_mentions:
                prediction['predicted_winner'] = fighter1
            else:
                prediction['predicted_winner'] = fighter2
                
            # Extract confidence level
            if "high confidence" in analysis.lower():
                prediction['confidence'] = "High"
            elif "low confidence" in analysis.lower():
                prediction['confidence'] = "Low"
                
        return prediction