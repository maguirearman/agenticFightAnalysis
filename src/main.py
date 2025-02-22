# src/main.py

from data_collection.data_processor import FightDataProcessor
from analysis.mma_agent import MMAAnalysisAgent
import json

def main():
    # Initialize components
    processor = FightDataProcessor()
    agent = MMAAnalysisAgent()
    
    # Load event data
    with open('event_data.json', 'r') as f:
        event_data = json.load(f)
    
    # Process all fights
    processed_fights = processor.process_fight_data(event_data)
    
    print(f"Found {len(processed_fights)} fights to analyze.")
    
    # Let user choose which fight to analyze
    for i, fight in enumerate(processed_fights):
        print(f"\n{i+1}. {fight['fighter1']['name']} vs {fight['fighter2']['name']}")
    
    fight_choice = int(input("\nWhich fight would you like to analyze? (Enter number): ")) - 1
    
    if 0 <= fight_choice < len(processed_fights):
        selected_fight = processed_fights[fight_choice]
        
        print(f"\nAnalyzing: {selected_fight['fighter1']['name']} vs {selected_fight['fighter2']['name']}")
        print(f"Weight Class: {selected_fight['weight_class']}")
        
        # Get analysis
        analysis = agent.analyze_fight(selected_fight)
        
        print("\nAnalysis Results:")
        print("================")
        print(analysis['output'])
        
    else:
        print("Invalid fight selection.")

if __name__ == "__main__":
    main()