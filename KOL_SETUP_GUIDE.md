# 🐋 KOL Wallet Tracking System

Complete toolkit to discover, verify, and track crypto KOL (Key Opinion Leader) wallets.

## 📦 Files Created

1. **kol_scraper.py** - Main scraper for GMGN.ai, Dune Analytics, manual KOLs
2. **twitter_wallet_finder.py** - Extract wallets from tweets and screenshots
3. **integrate_kols.py** - Auto-add KOLs to your whale tracker bot
4. **KOL_SETUP_GUIDE.md** - This file

---

## 🚀 Quick Start (3 Steps)

### Step 1: Scrape KOL Wallets
```bash
python kol_scraper.py
```

**What it does:**
- ✅ Scrapes top 100 KOLs from GMGN.ai (Solana + Base)
- ✅ Pulls Dune Analytics KOL list
- ✅ Adds manually verified KOLs
- ✅ Filters by performance (40%+ winrate, 5+ trades)
- ✅ Removes duplicates
- ✅ Assigns tiers (1=Elite, 2=Active, 3=Semi, 4=Dormant)
- ✅ Saves to `kol_wallets.json`

**Output:**
```
📊 KOL WALLET STATISTICS
🎯 Total KOLs: 150

🔗 By Chain:
  SOL: 100
  BASE: 50

🏆 By Tier:
  Tier 1 - Elite (30s): 30
  Tier 2 - Active (3m): 60
  Tier 3 - Semi (10m): 50
  Tier 4 - Dormant (24h): 10
```

---

### Step 2: Integrate into Whale Tracker
```bash
python integrate_kols.py
```

**What it does:**
- ✅ Loads your existing `whales_tiered_final.json`
- ✅ Loads scraped KOLs from `kol_wallets.json`
- ✅ Checks for duplicates
- ✅ Adds only Tier 1-2 KOLs (high quality)
- ✅ Creates backup before modifying
- ✅ Saves updated whale list
- ✅ Generates integration report

**Output:**
```
📊 Integration Results:
  ✅ Added: 90 new KOLs
  🔄 Updated: 0 existing entries
  ⏭️ Skipped: 0 duplicates
  🎯 Total whales: 2,049
```

---

### Step 3: Deploy to Railway
```bash
git add .
git commit -m "Added KOL wallet tracking"
git push
```

Railway auto-deploys in 30 seconds! 🚀

---

## 🐦 Twitter Wallet Discovery (Advanced)

### Method 1: Extract from Tweets
```python
from twitter_wallet_finder import TwitterWalletFinder

finder = TwitterWalletFinder()

tweet = """
Just bought $BONK! 
Wallet: DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK
LFG! 🚀
"""

wallets = finder.find_wallets_in_text(tweet, 'crypto_kol')
print(wallets)
# {'solana': ['DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK'], 'evm': []}
```

### Method 2: Dexscreener Link Analysis
```python
tweet = "My buy: dexscreener.com/solana/token123?maker=wallet456"

dex_wallets = finder.analyze_dexscreener_links(tweet)
print(dex_wallets)
# [{'wallet': 'wallet456', 'token': 'token123', 'source': 'dexscreener'}]
```

### Method 3: Screenshot Verification
When KOL posts transaction screenshot:

1. Extract details from caption:
```python
screenshot = {
    'text': 'Bought $PEPE for $5,000 at 3:45 PM 🔥'
}

tx_data = finder.parse_transaction_screenshot(screenshot)
print(tx_data)
# {'amount': '5000', 'token': 'PEPE', 'time': '3:45 PM'}
```

2. Verify on Dexscreener:
   - Go to token page
   - Filter by timestamp: 3:45 PM
   - Filter by amount: $5,000
   - Check buyer wallet address
   - Add verified wallet to KOL list

---

## 📊 KOL vs Regular Whale Tracking

| Feature | Regular Whales | KOLs |
|---------|---------------|------|
| **Identity** | Anonymous | Known (Twitter handle) |
| **Alert Priority** | Standard | 🌟 KOL Alert! |
| **Pre-Tweet Edge** | N/A | 5-30 min before public |
| **Community Impact** | Low | High (followers will pump) |
| **Verification** | Wallet history | Twitter + Wallet |

---

## 🎯 KOL Alert Example

When a KOL buys, you get:

```
🌟 KOL ALERT! 🔥

💎 Pepe Unchained ($PEPU)
🐦 @ansem (Tier 1 KOL)

💰 Buy Details:
  Amount: $50,000
  Entry: $0.0000123

📊 Token Metrics:
  MC: $2.5M
  Liquidity: $450K
  24h Vol: $850K

⚡ EDGE: KOL bought 12 mins ago
       Tweet likely coming soon!

🔗 https://dexscreener.com/solana/xxxxx
```

---

## 🔧 Configuration Options

### Scraper Settings (kol_scraper.py)

```python
# Adjust performance filters
scraper.filter_kols(
    min_winrate=40,   # Minimum 40% win rate
    min_trades=5      # Minimum 5 total trades
)

# Change tier criteria
def _calculate_tier(winrate, pnl_7d, total_trades):
    # Tier 1: 80+ score (70%+ WR, $50K+ PnL, 100+ trades)
    # Tier 2: 60+ score
    # Tier 3: 40+ score
    # Tier 4: <40 score
```

### Integration Settings (integrate_kols.py)

```python
# Only add elite KOLs
integrator.add_kols_to_tracker(
    min_tier=1,                    # Only Tier 1
    overwrite_duplicates=False     # Skip existing
)

# Add more KOLs
integrator.add_kols_to_tracker(
    min_tier=3,                    # Tier 1-3
    overwrite_duplicates=True      # Update existing
)
```

---

## 📈 Performance Tracking

Your bot automatically tracks KOL performance:

- **Win Rate**: Percentage of profitable calls
- **Avg Gain**: Average profit per winning trade
- **7-Day P&L**: Recent performance
- **Total Calls**: Number of trades made

After 30 days, the bot auto-promotes/demotes KOLs based on performance!

---

## 🎯 Top KOL Sources

1. **GMGN.ai** - Real-time leaderboards
   - https://gmgn.ai

2. **Dune Analytics** - Community curated
   - https://www.dune.com/queries/4838225

3. **Kolscan** - Solana specific
   - https://solanabox.tools/tools/kolscan

4. **Twitter** - Manual discovery
   - Search: "bought", "entry", "aping"
   - Look for: wallet addresses, Dexscreener links

---

## 🐛 Troubleshooting

### "kol_wallets.json not found"
```bash
# Run scraper first
python kol_scraper.py
```

### "whales_tiered_final.json not found"
```bash
# Copy from your bot project folder
cp ../whale-tracker-bot/whales_tiered_final.json .
```

### "No KOLs added"
```bash
# Lower quality filters
# Edit kol_scraper.py line 150:
scraper.filter_kols(min_winrate=30, min_trades=3)
```

### GMGN.ai Rate Limiting
```bash
# Add delays between requests
# Edit kol_scraper.py:
time.sleep(5)  # Wait 5 seconds between chains
```

---

## 📊 Expected Results

After running the complete system:

✅ **150-200 KOL wallets** discovered  
✅ **90-120 high-quality KOLs** added to tracker  
✅ **Tier 1-2 KOLs** monitored every 30s - 3min  
✅ **5-30 min edge** before public tweets  
✅ **Higher conviction signals** from known experts  

---

## 🚀 Next Steps

1. ✅ Run `python kol_scraper.py`
2. ✅ Run `python integrate_kols.py`
3. ✅ Review `kol_wallets.json`
4. ✅ Push to GitHub
5. ✅ Watch Railway deploy
6. ✅ Check Telegram for KOL alerts!

---

## 🎯 Pro Tips

1. **Manual KOL Discovery**
   - Follow top crypto Twitter accounts
   - Look for wallet addresses in bios/pinned tweets
   - Add to kol_scraper.py manual_kols list

2. **Quality Over Quantity**
   - Focus on Tier 1-2 KOLs only
   - 50 elite KOLs > 500 random wallets

3. **Verify Before Trading**
   - KOL alerts = research starting point
   - Always check token metrics
   - Don't blindly follow

4. **Track Performance**
   - Use `/performance` command
   - Monitor which KOLs are most profitable
   - Adjust tiers manually if needed

---

## 📞 Need Help?

If you get stuck:
1. Check error messages carefully
2. Verify all files are in the same folder
3. Make sure you ran kol_scraper.py before integrate_kols.py
4. Check Railway logs for deployment issues

---

**Built for Whale Tracker Bot V4** 🐋  
**Happy hunting! 🚀💎**
