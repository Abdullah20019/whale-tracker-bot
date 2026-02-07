"""
Automatic tier promotion/demotion system
Whales move between tiers based on performance
"""

import json
import time
from datetime import datetime
from state import bot_state, save_bot_state
from config import WHALE_LIST_FILE

def evaluate_whale_tier(whale_address):
    """Evaluate if whale should be promoted or demoted"""
    
    perf = bot_state.get('whale_performance', {})
    
    if whale_address not in perf:
        return None
    
    stats = perf[whale_address]
    
    if stats['tokens_tracked'] < 5:
        return None
    
    success_rate = (stats['successful_calls'] / stats['tokens_tracked']) * 100
    avg_gain = stats['total_gain'] / stats['tokens_tracked']
    
    if success_rate >= 60 and avg_gain >= 50 and stats['tokens_tracked'] >= 10:
        return 1
    elif success_rate >= 50 and avg_gain >= 30 and stats['tokens_tracked'] >= 5:
        return 2
    elif success_rate >= 40 and avg_gain >= 10:
        return 3
    else:
        return 4

def update_whale_tiers():
    """Check all whales and update tiers based on performance"""
    
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    changes = 0
    tier_changes = bot_state.get('tier_changes', [])
    
    for whale in whales:
        address = whale['address']
        current_tier = whale.get('tier', 3)
        
        recommended_tier = evaluate_whale_tier(address)
        
        if recommended_tier and recommended_tier != current_tier:
            whale['tier'] = recommended_tier
            
            change_record = {
                'whale': address,
                'old_tier': current_tier,
                'new_tier': recommended_tier,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'reason': get_tier_change_reason(address, current_tier, recommended_tier)
            }
            
            tier_changes.append(change_record)
            changes += 1
            
            print(f"  {'⬆️' if recommended_tier < current_tier else '⬇️'} Whale {address[:8]}... moved: Tier {current_tier} → {recommended_tier}")
    
    if changes > 0:
        with open(WHALE_LIST_FILE, 'w') as f:
            json.dump(whales, f, indent=2)
        
        bot_state['tier_changes'] = tier_changes[-100:]
        save_bot_state()
        
        print(f"✅ Updated {changes} whale tiers")
    
    return changes

def get_tier_change_reason(whale_address, old_tier, new_tier):
    """Generate reason for tier change"""
    
    perf = bot_state.get('whale_performance', {}).get(whale_address, {})
    
    success_rate = (perf['successful_calls'] / perf['tokens_tracked'] * 100) if perf.get('tokens_tracked', 0) > 0 else 0
    avg_gain = perf['total_gain'] / perf['tokens_tracked'] if perf.get('tokens_tracked', 0) > 0 else 0
    
    if new_tier < old_tier:
        return f"Promoted: {success_rate:.0f}% SR, {avg_gain:+.0f}% avg"
    else:
        return f"Demoted: {success_rate:.0f}% SR, {avg_gain:+.0f}% avg"
