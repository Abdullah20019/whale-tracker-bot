import json

print("="*60)
print("LOADING EXISTING BASE WHALES")
print("="*60)

# Load your original 2000 whale file
try:
    with open('top_2000_whales_final.json', 'r') as f:
        all_whales = json.load(f)
    print(f"\n✅ Loaded {len(all_whales)} total whales")
except FileNotFoundError:
    print("\n❌ ERROR: top_2000_whales_final.json not found!")
    print("Looking for alternative files...")
    
    # Try other possible filenames
    alternatives = [
        'top_2000_whales.json',
        'whales_complete.json',
        'all_whales.json',
        'whale_list.json'
    ]
    
    for filename in alternatives:
        try:
            with open(filename, 'r') as f:
                all_whales = json.load(f)
            print(f"✅ Found: {filename}")
            break
        except FileNotFoundError:
            continue
    else:
        print("\n❌ No whale files found. List your JSON files:")
        import os
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        for f in json_files:
            print(f"  - {f}")
        exit(1)

# Filter Base whales
base_whales = [w for w in all_whales if w.get('chain') == 'base']

print(f"✅ Found {len(base_whales)} Base whales")

# Tier them properly
tier_1 = []
tier_2 = []
tier_3 = []

for whale in base_whales:
    # Make sure it has required fields
    if 'address' not in whale:
        continue
    
    win_count = whale.get('win_count', 0)
    winning_tokens = whale.get('winning_tokens', [])
    
    # Tier based on win count
    if win_count >= 3 or len(winning_tokens) >= 3:
        whale['tier'] = 1
        tier_1.append(whale)
    elif win_count >= 2 or len(winning_tokens) >= 2:
        whale['tier'] = 2
        tier_2.append(whale)
    else:
        whale['tier'] = 3
        tier_3.append(whale)
    
    whale['is_active'] = True

# Load current Solana whales
with open('whales_tiered.json', 'r') as f:
    current = json.load(f)

# Keep only Solana
solana_whales = [w for w in current if w.get('chain') == 'solana']

# Combine all
final = solana_whales + base_whales

# Save
with open('whales_tiered_final.json', 'w') as f:
    json.dump(final, f, indent=2)

# Stats
sol_t1 = len([w for w in solana_whales if w.get('tier') == 1])

print(f"\n{'='*60}")
print("FINAL STATS")
print(f"{'='*60}")

print(f"\nBase Whales:")
print(f"  Tier 1 (Elite): {len(tier_1)}")
print(f"  Tier 2 (Active): {len(tier_2)}")
print(f"  Tier 3 (Semi): {len(tier_3)}")

print(f"\nSolana Tier 1: {sol_t1}")

print(f"\nTotal Tier 1: {len(tier_1) + sol_t1}")

print(f"\n🏆 Top 50 Base Tier 1 Whales:")

tier_1_sorted = sorted(tier_1, key=lambda x: x.get('win_count', 0), reverse=True)

for i, w in enumerate(tier_1_sorted[:50], 1):
    tokens = w.get('winning_tokens', [])
    token_str = ', '.join(tokens[:4]) if tokens else 'Unknown'
    win_count = w.get('win_count', len(tokens))
    
    print(f"{i:2d}. {w['address'][:16]}... | "
          f"Wins: {win_count:>2} | "
          f"{token_str}")

print(f"\n✅ Saved: whales_tiered_final.json")
print(f"🚀 NOW START THE TRACKING BOT!")
print(f"\nRun: python track_whales.py")
