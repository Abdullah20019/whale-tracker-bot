"""
Whale Tracker Bot V4 - Multi-Tier System
Monitors 4 tiers of whales with different check intervals
"""

import json
import threading
import time
import requests
import traceback
from datetime import datetime

# Import modular components
from config import *
from state import bot_state, save_bot_state, load_bot_state
from utils import *
from commands import handle_command
from features import check_whale_for_new_buys

# Load bot state
load_bot_state()

print("="*60)
print("🐋 WHALE TRACKER BOT V4 - MULTI-TIER SYSTEM")
print("="*60)

# ============================================================
# Load ALL whales across ALL tiers
# ============================================================

with open(WHALE_LIST_FILE, 'r') as f:
    all_whales = json.load(f)

# Separate by tier
tier1_whales = [w for w in all_whales if w.get('tier', 3) == 1]
tier2_whales = [w for w in all_whales if w.get('tier', 3) == 2]
tier3_whales = [w for w in all_whales if w.get('tier', 3) == 3]
tier4_whales = [w for w in all_whales if w.get('tier', 3) == 4]

# Separate by chain
tier1_base = [w for w in tier1_whales if w['chain'] == 'base']
tier1_sol = [w for w in tier1_whales if w['chain'] == 'solana']

tier2_base = [w for w in tier2_whales if w['chain'] == 'base']
tier2_sol = [w for w in tier2_whales if w['chain'] == 'solana']

tier3_base = [w for w in tier3_whales if w['chain'] == 'base']
tier3_sol = [w for w in tier3_whales if w['chain'] == 'solana']

tier4_base = [w for w in tier4_whales if w['chain'] == 'base']
tier4_sol = [w for w in tier4_whales if w['chain'] == 'solana']

print(f"\n📊 Loaded Whales:")
print(f"  🔥 Tier 1: {len(tier1_whales)} (Base: {len(tier1_base)}, Sol: {len(tier1_sol)})")
print(f"  ⭐ Tier 2: {len(tier2_whales)} (Base: {len(tier2_base)}, Sol: {len(tier2_sol)})")
print(f"  📊 Tier 3: {len(tier3_whales)} (Base: {len(tier3_base)}, Sol: {len(tier3_sol)})")
print(f"  💤 Tier 4: {len(tier4_whales)} (Base: {len(tier4_base)}, Sol: {len(tier4_sol)})")
print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"  📊 TOTAL: {len(all_whales)} whales")

# Track known tokens per whale
whale_tokens = {}
for whale in all_whales:
    whale_tokens[whale['address']] = set()

print(f"\n📱 Telegram Configuration:")
print(f"  Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
print(f"  Private Chat: ✅ {TELEGRAM_CHAT_ID}")
print(f"  Group Chat: ✅ {TELEGRAM_GROUP_ID}")

if TELEGRAM_BOT_TOKEN:
    print(f"  Commands: ✅ Enabled")
    print(f"  🆕 Multi-Tier Tracking: ON")
    print(f"  🆕 Auto-Promotion System: ON")
    print(f"  🆕 Performance Tracking: ON")
    print(f"  🆕 Sell Detection: ON")

print(f"\n🎯 Filters:")
print(f"  Market Cap: ${DEFAULT_FILTERS['mc_min']:,} - ${DEFAULT_FILTERS['mc_max']:,}")
print(f"  Min Liquidity: ${DEFAULT_FILTERS['liq_min']:,}")

print(f"\n🚀 Starting 8 monitoring threads...")
print(f"  🔥 Tier 1: Check every 30 seconds")
print(f"  ⭐ Tier 2: Check every 3 minutes")
print(f"  📊 Tier 3: Check every 10 minutes")
print(f"  💤 Tier 4: Check every 24 hours")
print(f"  🎯 Performance: Auto-tier promotion")
print(f"  💬 Commands: Instant Telegram response")
print(f"  📈 Tracker: Price milestone alerts")
print(f"  🚨 Detector: Whale sell alerts")
print("="*60 + "\n")

# ============================================================
# Tier 1 Monitor (30s interval)
# ============================================================

def tier1_monitor():
    """Monitor Tier 1 elite whales (30s interval)"""
    print("✅ Tier 1 monitor started (30s)")
    
    first_run = True
    cycle = 0
    
    while True:
        try:
            cycle += 1
            
            if bot_state.get('paused'):
                time.sleep(30)
                continue
            
            print(f"\n🔥 [TIER 1] Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Reload whales to get updated tiers
            with open(WHALE_LIST_FILE, 'r') as f:
                whales = json.load(f)
            
            tier1 = [w for w in whales if w.get('tier') == 1]
            
            for whale in tier1:
                check_whale_for_new_buys(whale, whale_tokens, first_run)
                time.sleep(0.2)
            
            if first_run:
                first_run = False
                print("   ✅ Baseline complete")
            
            time.sleep(30)
        
        except Exception as e:
            print(f"Tier 1 error: {e}")
            time.sleep(30)

# ============================================================
# Tier 2 Monitor (3m interval)
# ============================================================

def tier2_monitor():
    """Monitor Tier 2 active whales (3min interval)"""
    print("✅ Tier 2 monitor started (3m)")
    
    first_run = True
    cycle = 0
    
    # Wait 1 minute before starting
    time.sleep(60)
    
    while True:
        try:
            cycle += 1
            
            if bot_state.get('paused'):
                time.sleep(180)
                continue
            
            print(f"\n⭐ [TIER 2] Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            with open(WHALE_LIST_FILE, 'r') as f:
                whales = json.load(f)
            
            tier2 = [w for w in whales if w.get('tier') == 2]
            
            for whale in tier2:
                check_whale_for_new_buys(whale, whale_tokens, first_run)
                time.sleep(0.3)
            
            if first_run:
                first_run = False
            
            time.sleep(180)
        
        except Exception as e:
            print(f"Tier 2 error: {e}")
            time.sleep(180)

# ============================================================
# Tier 3 Monitor (10m interval)
# ============================================================

def tier3_monitor():
    """Monitor Tier 3 semi-active whales (10min interval)"""
    print("✅ Tier 3 monitor started (10m)")
    
    first_run = True
    cycle = 0
    
    # Wait 2 minutes before starting
    time.sleep(120)
    
    while True:
        try:
            cycle += 1
            
            if bot_state.get('paused'):
                time.sleep(600)
                continue
            
            print(f"\n📊 [TIER 3] Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            with open(WHALE_LIST_FILE, 'r') as f:
                whales = json.load(f)
            
            tier3 = [w for w in whales if w.get('tier') == 3]
            
            for whale in tier3:
                check_whale_for_new_buys(whale, whale_tokens, first_run)
                time.sleep(0.5)
            
            if first_run:
                first_run = False
            
            time.sleep(600)
        
        except Exception as e:
            print(f"Tier 3 error: {e}")
            time.sleep(600)

# ============================================================
# Tier 4 Monitor (24h interval)
# ============================================================

def tier4_monitor():
    """Monitor Tier 4 dormant whales (24h interval)"""
    print("✅ Tier 4 monitor started (24h)")
    
    first_run = True
    cycle = 0
    
    # Wait 5 minutes before starting
    time.sleep(300)
    
    while True:
        try:
            cycle += 1
            
            if bot_state.get('paused'):
                time.sleep(3600)
                continue
            
            print(f"\n💤 [TIER 4] Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            with open(WHALE_LIST_FILE, 'r') as f:
                whales = json.load(f)
            
            tier4 = [w for w in whales if w.get('tier') == 4]
            
            for whale in tier4:
                check_whale_for_new_buys(whale, whale_tokens, first_run)
                time.sleep(1)
            
            if first_run:
                first_run = False
            
            time.sleep(86400)  # 24 hours
        
        except Exception as e:
            print(f"Tier 4 error: {e}")
            time.sleep(3600)

# ============================================================
# Auto-Tier Promotion System
# ============================================================

def tier_promotion_monitor():
    """Check whale performance and auto-promote/demote"""
    print("✅ Tier promotion system started")
    
    # Wait 10 minutes before first check
    time.sleep(600)
    
    while True:
        try:
            print(f"\n🎯 [AUTO-TIER] Checking whale performance...")
            
            from tier_manager import update_whale_tiers
            
            changes = update_whale_tiers()
            
            if changes > 0:
                print(f"   ✅ Updated {changes} whale tiers")
            
            # Check every hour
            time.sleep(3600)
        
        except Exception as e:
            print(f"Tier promotion error: {e}")
            time.sleep(3600)

# ============================================================
# Command Listener Thread
# ============================================================

def command_listener():
    """Listen for Telegram commands"""
    print("✅ Command listener started")
    
    while True:
        try:
            if not TELEGRAM_BOT_TOKEN:
                time.sleep(10)
                continue
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {
                'offset': bot_state.get('last_update_id', 0) + 1,
                'timeout': 10
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                time.sleep(5)
                continue
            
            data = response.json()
            
            if not data.get('ok'):
                time.sleep(5)
                continue
            
            if data.get('result'):
                for update in data['result']:
                    bot_state['last_update_id'] = update['update_id']
                    
                    if 'message' in update and 'text' in update['message']:
                        text = update['message']['text']
                        user_id = update['message']['from']['id']
                        chat_id = update['message']['chat']['id']
                        
                        if text.startswith('/'):
                            print(f"\n💬 COMMAND: {text}")
                            
                            try:
                                reply = handle_command(text, user_id)
                                
                                if reply:
                                    success = send_telegram_message(reply, chat_id)
                                    
                                    if success:
                                        print(f"   ✅ Response sent!\n")
                                    else:
                                        print(f"   ❌ Failed to send\n")
                            
                            except Exception as e:
                                print(f"   ❌ Command error: {e}\n")
                                traceback.print_exc()
                
                save_bot_state()
        
        except Exception as e:
            time.sleep(5)

# ============================================================
# Performance Tracker Thread
# ============================================================

def performance_tracker():
    """Track token performance and send milestone alerts"""
    print("✅ Performance tracker started")
    
    time.sleep(60)  # Wait 1 min before starting
    
    while True:
        try:
            time.sleep(60)  # Check every minute
            
            tracked = bot_state.get('tracked_tokens', {})
            
            for token_addr, data in list(tracked.items()):
                if data.get('status') != 'active':
                    continue
                
                if time.time() - data.get('last_check_time', 0) < 60:
                    continue
                
                # Update token performance
                token_info = get_token_info(token_addr, data['chain'])
                
                if token_info:
                    current_price = token_info['price']
                    initial_price = data['initial_price']
                    
                    current_gain = ((current_price - initial_price) / initial_price) * 100
                    
                    data['current_price'] = current_price
                    data['current_gain'] = current_gain
                    data['last_check_time'] = time.time()
                    
                    if current_gain > data.get('max_gain', 0):
                        data['max_gain'] = current_gain
                        data['highest_price'] = current_price
                    
                    # Send milestone alerts
                    milestones = [10, 25, 50, 100, 200, 500, 1000]
                    for milestone in milestones:
                        if current_gain >= milestone and not data.get('alerts_sent', {}).get(str(milestone)):
                            
                            whale_count = len(data.get('whales_bought', []))
                            multi_icon = "🔥🔥🔥" if whale_count >= 3 else "🔥" if whale_count >= 2 else ""
                            
                            time_since = (time.time() - data.get('first_alert_time', time.time())) / 3600
                            
                            message = f"""
🚀 <b>PRICE MILESTONE {multi_icon}</b>

💎 <b>{data['symbol']}</b> is UP <b>{current_gain:.1f}%</b>!

━━━━━━━━━━━━━━━━━━━━
📊 Initial MC: <b>${data['initial_mc']:,.0f}</b>
📊 Current MC: <b>${token_info['market_cap']:,.0f}</b>

💰 Entry: ${initial_price:.8f}
💰 Current: ${current_price:.8f}
📈 Gain: <b>+{current_gain:.1f}%</b>

🐋 Whales: <b>{whale_count}</b>
⏰ Time: {time_since:.1f}h ago

━━━━━━━━━━━━━━━━━━━━
🔗 <a href="{token_info['url']}">View Chart</a>
📝 <code>{token_addr}</code>
━━━━━━━━━━━━━━━━━━━━
"""
                            send_telegram_alert(message)
                            
                            if 'alerts_sent' not in data:
                                data['alerts_sent'] = {}
                            data['alerts_sent'][str(milestone)] = True
                            
                            # Update whale performance
                            from features import update_whale_performance
                            for whale_addr in data.get('whales_bought', []):
                                update_whale_performance(whale_addr, current_gain)
                    
                    save_bot_state()
        
        except Exception as e:
            time.sleep(60)

# ============================================================
# Sell Detector Thread (UPDATED!)
# ============================================================

def sell_detector():
    """Detect whale sells"""
    print("✅ Sell detector started")
    
    time.sleep(120)  # Wait 2 min before starting
    
    while True:
        try:
            time.sleep(120)  # Check every 2 minutes
            
            # Check for whale sells
            from features import check_whale_sells
            check_whale_sells()
            
        except Exception as e:
            print(f"Sell detector error: {e}")
            time.sleep(120)

# ============================================================
# Start all threads
# ============================================================

# Tier monitors
t1_thread = threading.Thread(target=tier1_monitor, daemon=True)
t2_thread = threading.Thread(target=tier2_monitor, daemon=True)
t3_thread = threading.Thread(target=tier3_monitor, daemon=True)
t4_thread = threading.Thread(target=tier4_monitor, daemon=True)

# Support threads
promotion_thread = threading.Thread(target=tier_promotion_monitor, daemon=True)
command_thread = threading.Thread(target=command_listener, daemon=True)
perf_thread = threading.Thread(target=performance_tracker, daemon=True)
sell_thread = threading.Thread(target=sell_detector, daemon=True)

# Start all threads
t1_thread.start()
t2_thread.start()
t3_thread.start()
t4_thread.start()
promotion_thread.start()
command_thread.start()
perf_thread.start()
sell_thread.start()

print("\n" + "="*60)
print("✅ ALL 8 SYSTEMS ONLINE!")
print("="*60)
print("\n🎯 Bot is now monitoring 1,963 whales across 4 tiers")
print("🚨 Sell detection active - tracking whale exits")
print("📈 Price milestones - alerts at +10%, +25%, +50%, +100%")
print("💬 Commands ready - type /help in Telegram\n")
print("="*60 + "\n")

# Keep main thread alive
while True:
    time.sleep(10)
