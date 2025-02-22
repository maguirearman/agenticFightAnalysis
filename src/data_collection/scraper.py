from bs4 import BeautifulSoup
import requests
import pandas as pd
from typing import Dict, List, Optional
import time

class UFCStatsScraper:
    def __init__(self):
        self.base_url = "http://ufcstats.com/fight-details"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_fight_stats(self, fight_url: str) -> Dict:
        """
        Scrapes fight statistics from a specific UFC fight page
        
        Args:
            fight_url: URL of the fight details page
            
        Returns:
            Dictionary containing fight statistics
        """
        try:
            response = requests.get(fight_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get fighter names
            fighter_names = [name.text.strip() for name in soup.select('.b-fight-details__person-name')]
            
            # Get striking stats
            strikes_landed_attempted = [stats.text.strip() for stats in soup.select('.b-fight-details__table-col_type_scaled')]
            
            # Get takedown stats
            takedowns = [td.text.strip() for td in soup.select('.b-fight-details__table-col_type_td')]
            
            # Get control time
            control_time = [time.text.strip() for time in soup.select('.b-fight-details__table-col_type_control-time')]
            
            fight_data = {
                "fighter1": {
                    "name": fighter_names[0],
                    "strikes": self._parse_ratio(strikes_landed_attempted[0]),
                    "takedowns": self._parse_ratio(takedowns[0]),
                    "control_time": control_time[0] if control_time else "0:00"
                },
                "fighter2": {
                    "name": fighter_names[1],
                    "strikes": self._parse_ratio(strikes_landed_attempted[1]),
                    "takedowns": self._parse_ratio(takedowns[1]),
                    "control_time": control_time[1] if len(control_time) > 1 else "0:00"
                }
            }
            
            return fight_data
            
        except Exception as e:
            print(f"Error scraping fight data: {e}")
            return None

    def _parse_ratio(self, stat_string: str) -> Dict[str, int]:
        """
        Parses statistics in the format "47 of 123" into a dictionary
        """
        try:
            landed, attempted = stat_string.split(' of ')
            return {
                "landed": int(landed),
                "attempted": int(attempted)
            }
        except:
            return {"landed": 0, "attempted": 0}

    def get_event_fights(self, event_url: str) -> List[str]:
        """
        Gets all fight URLs from a UFC event page
        """
        try:
            response = requests.get(event_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            fight_links = soup.select('td.b-fight-details__table-col_type_name a')
            return [link['href'] for link in fight_links]
            
        except Exception as e:
            print(f"Error getting event fights: {e}")
            return []

# Example usage
if __name__ == "__main__":
    scraper = UFCStatsScraper()
    
    # Example fight URL - UFC 285: Jones vs Gane
    fight_url = "http://ufcstats.com/event-details/ce7871949b0ed2bf"
    
    # Get fight data
    fight_data = scraper.get_fight_stats(fight_url)
    print("\nFight Data:")
    print(pd.DataFrame(fight_data).transpose())
    
    # Example to get all fights from an event
    event_url = "http://ufcstats.com/event-details/5de6f1e46ac42ee9"
    fight_urls = scraper.get_event_fights(event_url)
    print(f"\nFound {len(fight_urls)} fights in the event")