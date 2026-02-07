"""
Classify whales into 4 tiers based on performance
Distributes whales evenly across tiers
"""

import json

# Load your current whale list
with open('whales_tiered_final.json', 'r') as f:
    whales = json.load(f)

print("🔍 Classifying whales into tiers...")
print(f"Total whales: {len(whales)}")

# Sort whales by performance (win_rate * win_count for better scoring)
for whale in whales:
    win_count = whale.get('win_count', 0)
    win_rate = whale.get('win_rate', 0)
    # Calculate performance score
    whale['performance_score'] = (win_rate * win_count) + (win_count * 10)

# Sort by performance score
sorted_whales = sorted(whales, key=lambda x: x.get('performance_score', 0), reverse=True)

# Calculate tier sizes (distribute evenly)
total = len(sorted_whales)
tier_1_size = int(total * 0.10)  # Top 10% = Tier 1
tier_2_size = int(total * 0.20)  # Next 20% = Tier 2
tier_3_size = int(total * 0.50)  # Next 50% = Tier 3
# Remaining = Tier 4

print(f"\n📊 Tier Distribution:")
print(f"  Tier 1: Top {tier_1_size} ({(tier_1_size/total*100):.0f}%)")
print(f"  Tier 2: Next {tier_2_size} ({(tier_2_size/total*100):.0f}%)")
print(f"  Tier 3: Next {tier_3_size} ({(tier_3_size/total*100):.0f}%)")
print(f"  Tier 4: Remaining {total - tier_1_size - tier_2_size - tier_3_size} ({((total - tier_1_size - tier_2_size - tier_3_size)/total*100):.0f}%)")

# Assign tiers
tier_1_count = 0
tier_2_count = 0
tier_3_count = 0
tier_4_count = 0

for i, whale in enumerate(sorted_whales):
    if i < tier_1_size:
        whale['tier'] = 1
        whale['check_interval'] = 30
        whale['priority'] = 'high'
        tier_1_count += 1
    elif i < tier_1_size + tier_2_size:
        whale['tier'] = 2
        whale['check_interval'] = 180
        whale['priority'] = 'medium'
        tier_2_count += 1
    elif i < tier_1_size + tier_2_size + tier_3_size:
        whale['tier'] = 3
        whale['check_interval'] = 600
        whale['priority'] = 'low'
        tier_3_count += 1
    else:
        whale['tier'] = 4
        whale['check_interval'] = 86400
        whale['priority'] = 'dormant'
        tier_4_count += 1
    
    # Remove temp score
    if 'performance_score' in whale:
        del whale['performance_score']

# Save updated list
with open('whales_tiered_final.json', 'w') as f:
    json.dump(sorted_whales, f, indent=2)

print("\n✅ Classification complete!")
print(f"🔥 Tier 1 (Elite - 30s): {tier_1_count}")
print(f"⭐ Tier 2 (Active - 3m): {tier_2_count}")
print(f"📊 Tier 3 (Semi-Active - 10m): {tier_3_count}")
print(f"💤 Tier 4 (Dormant - 24h): {tier_4_count}")
print(f"\n🎯 Total: {len(sorted_whales)} whales classified")

# Show top 10 whales
print("\n🏆 TOP 10 WHALES (Now in Tier 1):")
for i, whale in enumerate(sorted_whales[:10], 1):
    print(f"{i}. {whale['address'][:16]}... | Wins: {whale.get('win_count', 0)} | WR: {whale.get('win_rate', 0):.1f}%")
