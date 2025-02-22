# src/data_collection/data_processor.py

from typing import Dict, List, Any
import json

class FightDataProcessor:
    def __init__(self):
        pass

    def process_fight_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Process raw fight data into a structured format for analysis
        """
        processed_fights = []
        
        for fight in raw_data:
            matchup = fight.get('matchup', [])
            stats = fight.get('tale_of_the_tape', {})
            
            if len(matchup) != 2:
                continue
                
            fighter1, fighter2 = matchup
            
            processed_fight = {
                'fighter1': {
                    'name': fighter1,
                    'stats': self._extract_fighter_stats(stats, fighter1)
                },
                'fighter2': {
                    'name': fighter2,
                    'stats': self._extract_fighter_stats(stats, fighter2)
                },
                'weight_class': stats.get('Weight', {}).get(fighter1, 'Unknown'),
                'matchup_details': self._extract_matchup_details(stats, fighter1, fighter2)
            }
            
            processed_fights.append(processed_fight)
            
        return processed_fights

    def _extract_fighter_stats(self, stats: Dict, fighter_name: str) -> Dict:
        """
        Extract individual fighter statistics
        """
        return {
            'stance': stats.get('Stance', {}).get(fighter_name),
            'record': stats.get('Wins/Losses/Draws', {}).get(fighter_name),
            'height': stats.get('Height', {}).get(fighter_name),
            'reach': stats.get('Reach', {}).get(fighter_name),
            'age': stats.get('DOB', {}).get(fighter_name),
            'striking_stats': {
                'strikes_landed_per_min': float(stats.get('Strikes Landed per Min. (SLpM)', {}).get(fighter_name, 0)),
                'strikes_absorbed_per_min': float(stats.get('Strikes Absorbed per Min. (SApM)', {}).get(fighter_name, 0)),
                'striking_accuracy': stats.get('Striking Accuracy', {}).get(fighter_name),
                'defense': stats.get('Defense', {}).get(fighter_name)
            },
            'grappling_stats': {
                'takedowns_per_15min': float(stats.get('Takedowns Average/15 min.', {}).get(fighter_name, 0)),
                'takedown_accuracy': stats.get('Takedown Accuracy', {}).get(fighter_name),
                'takedown_defense': stats.get('Takedown Defense', {}).get(fighter_name),
                'submissions_per_15min': float(stats.get('Submission Average/15 min.', {}).get(fighter_name, 0))
            },
            'fight_metrics': {
                'avg_fight_time': stats.get('Average Fight Time', {}).get(fighter_name)
            }
        }

    def _extract_matchup_details(self, stats: Dict, fighter1: str, fighter2: str) -> Dict:
        """
        Extract relevant matchup details and recent fight history
        """
        # Get all keys that start with "Win" or "Loss"
        history_keys = [k for k in stats.keys() if k.startswith(('Win', 'Loss'))]
        
        return {
            'recent_fights': {
                'fighter1': {k: stats[k].get(fighter1) for k in history_keys if stats[k].get(fighter1)},
                'fighter2': {k: stats[k].get(fighter2) for k in history_keys if stats[k].get(fighter2)}
            }
        }