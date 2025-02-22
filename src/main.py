from data_collection.scraper import UFCStatsScraper
from agent import MMAAnalysisAgent

def main():
    # Initialize scraper and agent
    scraper = UFCStatsScraper()
    agent = MMAAnalysisAgent()
    
    # Example: Get data from a recent fight
    fight_url = "http://ufcstats.com/fight-details/7a0705378548744f"  # Example UFC fight
    
    print("Fetching fight data...")
    fight_data = scraper.get_fight_stats(fight_url)
    
    if fight_data:
        print("\nFight Data Retrieved:")
        print(f"Fighter 1: {fight_data['fighter1']['name']}")
        print(f"Fighter 2: {fight_data['fighter2']['name']}")
        
        print("\nAnalyzing fight...")
        analysis = agent.analyze_fight(fight_data)
        print("\nAnalysis Results:")
        print(analysis)
    else:
        print("Failed to retrieve fight data")

if __name__ == "__main__":
    main()