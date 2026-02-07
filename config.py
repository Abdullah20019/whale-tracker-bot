"""
Classify whales into 4 tiers based on activity
Run this once to update your whale list
"""

import json

# Load your current whale list
with open('whales_tiered_final.json', 'r') as f:
    whales = json.load(f)

print("🔍 Classifying whales into tiers...")
print(f"Total whales: {len(whales)}")

# Tier criteria
tier_1_count = 0
tier_2_count = 0
tier_3_count = 0
tier_4_count = 0

for whale in whales:
    win_count = whale.get('win_count', 0)
    win_rate = whale.get('win_rate', 0)
    
    # Classify based on win_count and win_rate
    if win_count >= 10 and win_rate >= 60:
        whale['tier'] = 1
        whale['check_interval'] = 30  # 30 seconds
        whale['priority'] = 'high'
        tier_1_count += 1
    elif win_count >= 5 and win_rate >= 50:
        whale['tier'] = 2
        whale['check_interval'] = 180  # 3 minutes
        whale['priority'] = 'medium'
        tier_2_count += 1
    elif win_count >= 2 or win_rate >= 40:
        whale['tier'] = 3
        whale['check_interval'] = 600  # 10 minutes
        whale['priority'] = 'low'
        tier_3_count += 1
    else:
        whale['tier'] = 4
        whale['check_interval'] = 86400  # 24 hours
        whale['priority'] = 'dormant'
        tier_4_count += 1

# Save updated list
with open('whales_tiered_final.json', 'w') as f:
    json.dump(whales, f, indent=2)

print("\n✅ Classification complete!")
print(f"🔥 Tier 1 (Elite - 30s): {tier_1_count}")
print(f"⭐ Tier 2 (Active - 3m): {tier_2_count}")
print(f"📊 Tier 3 (Semi-Active - 10m): {tier_3_count}")
print(f"💤 Tier 4 (Dormant - 24h): {tier_4_count}")
print(f"\n🎯 Total: {len(whales)} whales classified")
