# src/main.py

from data_collection.data_processor import FightDataProcessor
from analysis.mma_agent import MMAAnalysisAgent
from prediction.mma_predictor import MMAFightPredictor
import json

def main():
    # Initialize components
    processor = FightDataProcessor()
    analyzer = MMAAnalysisAgent()
    predictor = MMAFightPredictor()
    
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
        
        # Ask user what they want to do
        print("\nOptions:")
        print("1. Analyze the fight")
        print("2. Predict the winner")
        print("3. Both analyze and predict")
        option = int(input("\nWhat would you like to do? (Enter number): "))
        
        if option == 1 or option == 3:
            # Get analysis
            print("\nGenerating fight analysis...")
            analysis = analyzer.analyze_fight(selected_fight)
            
            print("\nAnalysis Results:")
            print("================")
            print(analysis['output'])
        
        if option == 2 or option == 3:
            # Get prediction
            print("\nGenerating winner prediction...")
            prediction = predictor.predict_winner(selected_fight)
            
            print("\nPrediction Results:")
            print("=================")
            winner = prediction['prediction']['predicted_winner']
            confidence = prediction['prediction']['confidence']
            
            print(f"\nPredicted Winner: {winner}")
            print(f"Confidence Level: {confidence}")
            print("\nFull Analysis:")
            print(prediction['full_analysis'])
            
    else:
        print("Invalid fight selection.")

if __name__ == "__main__":
    main()