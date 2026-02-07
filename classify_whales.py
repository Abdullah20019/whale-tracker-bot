"""
Whale Tracker Bot V4 - Tiered Monitoring System
Elite whales = 30s checks | Active = 3m | Semi = 10m | Dormant = 24h
"""

import json
import time
import threading
import requests
from datetime import datetime

# Import all modules
from config import *
from state import load_bot_state, save_bot_state, bot_state
from utils import (
    send_telegram_message, 
    get_solana_tokens, 
    get_base_tokens, 
    get_token_info, 
    passes_filters,
    send_telegram_alert
)
from commands import handle_command
from features import (
    track_token_buy,
    check_multi_buy,
    check_whale_sells_solana,
    check_whale_sells_base,
    track_token_performance
)

# ============================================================
# STARTUP
# ============================================================

print("="*60)
print("🐋 WHALE TRACKER BOT V4 - TIERED SYSTEM")
print("="*60)

# Load bot state
load_bot_state()

# Load whales
with open(WHALE_LIST_FILE, 'r') as f:
    all_whales = json.load(f)

# Separate by tier
tier_1_whales = [w for w in all_whales if w.get('tier') == 1]
tier_2_whales = [w for w in all_whales if w.get('tier') == 2]
tier_3_whales = [w for w in all_whales if w.get('tier') == 3]
tier_4_whales = [w for w in all_whales if w.get('tier') == 4]

print(f"\n📊 Tiered Whale System:")
print(f"  🔥 Tier 1 (Elite - 30s): {len(tier_1_whales)}")
print(f"  ⭐ Tier 2 (Active - 3m): {len(tier_2_whales)}")
print(f"  📊 Tier 3 (Semi - 10m): {len(tier_3_whales)}")
print(f"  💤 Tier 4 (Dormant - 24h): {len(tier_4_whales)}")
print(f"  🎯 Total Tracking: {len(all_whales)}")

# Track known tokens per whale
whale_tokens = {}
whale_last_check = {}  # Track when each whale was last checked

for whale in all_whales:
    whale_tokens[whale['address']] = set()
    whale_last_check[whale['address']] = 0  # Never checked

print(f"\n📱 Telegram Configuration:")
print(f"  Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
print(f"  Private Chat: ✅ {PRIVATE_CHAT_ID}")
print(f"  Group Chat: ✅ {GROUP_CHAT_ID}")
print(f"  🔒 Admin: {ADMIN_USER_ID}")

if TELEGRAM_BOT_TOKEN:
    print(f"  Commands: ✅ Enabled")
    print(f"  🆕 Tiered Monitoring: ON")
    print(f"  🆕 Multi-Buy Detection: ON")
    print(f"  🆕 Whale Exit Detection: ON")
    print(f"  🆕 Performance Tracking: ON")

print(f"\n🎯 Filters:")
print(f"  Market Cap: ${bot_state['filters']['mc_min']:,} - ${bot_state['filters']['mc_max']:,}")
print(f"  Min Liquidity: ${bot_state['filters']['liq_min']:,}")

print(f"\n🚀 Starting tiered monitoring...")
print("="*60 + "\n")

# ============================================================
# COMMAND LISTENER THREAD
# ============================================================

def command_listener_thread():
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
            data = response.json()
            
            if data.get('result'):
                for update in data['result']:
                    bot_state['last_update_id'] = update['update_id']
                    
                    if 'message' in update and 'text' in update['message']:
                        text = update['message']['text']
                        user_id = update['message']['from']['id']
                        chat_id = update['message']['chat']['id']
                        
                        if text.startswith('/'):
                            print(f"💬 Command: {text}")
                            reply = handle_command(text, user_id)
                            
                            if send_telegram_message(reply, chat_id):
                                print(f"   ✅ Response sent!")
                
                save_bot_state()
        
        except Exception as e:
            time.sleep(5)

# ============================================================
# SELL DETECTOR THREAD
# ============================================================

def sell_detector_thread():
    """Monitor whale wallets for sells"""
    print("✅ Sell detector started")
    
    while True:
        try:
            time.sleep(SELL_CHECK_INTERVAL)
            
            check_whale_sells_solana()
            check_whale_sells_base()
            
            save_bot_state()
            
        except Exception as e:
            print(f"Sell detector error: {e}")
            time.sleep(SELL_CHECK_INTERVAL)

# ============================================================
# PERFORMANCE TRACKER THREAD
# ============================================================

def performance_tracker_thread():
    """Track token performance and send price updates"""
    print("✅ Performance tracker started")
    
    while True:
        try:
            time.sleep(PERFORMANCE_CHECK_INTERVAL)
            
            track_token_performance()
        
        except Exception as e:
            print(f"Performance tracker error: {e}")
            time.sleep(PERFORMANCE_CHECK_INTERVAL)

# ============================================================
# WHALE MONITORING
# ============================================================

def check_whale_wallet(whale, is_wakeup=False):
    """Check single whale for new positions"""
    address = whale['address']
    chain = whale['chain']
    tier = whale.get('tier', 1)
    win_rate = whale.get('win_rate', 0)
    
    tier_emoji = TIER_CONFIG[tier]['emoji']
    priority = TIER_CONFIG[tier]['alert_priority']
    
    if chain == 'solana':
        current_tokens = get_solana_tokens(address)
    else:
        current_tokens = get_base_tokens(address)
    
    current_token_set = {t['address'] for t in current_tokens}
    previous_token_set = whale_tokens.get(address, set())
    
    new_tokens = current_token_set - previous_token_set
    
    if new_tokens and len(previous_token_set) > 0:
        for token_address in new_tokens:
            if token_address in BLACKLIST_TOKENS:
                continue
            
            token_info = get_token_info(token_address, chain)
            
            if not token_info:
                continue
            
            passed, reason = passes_filters(token_info, bot_state['filters'])
            
            if not passed:
                bot_state['tokens_filtered'] += 1
                continue
            
            token_balance = next((t['balance'] for t in current_tokens if t['address'] == token_address), 0)
            
            track_token_buy(
                token_address,
                address,
                token_info['price'],
                token_info['market_cap'],
                token_info['symbol'],
                chain,
                token_balance
            )
            
            multi_count = check_multi_buy(token_address)
            multi_icon = "🔥🔥🔥" if multi_count >= 3 else "🔥" if multi_count >= 2 else ""
            
            wakeup_alert = ""
            if is_wakeup:
                wakeup_alert = "\n\n🚨 <b>DORMANT WHALE WAKE-UP!</b> 🚨\nFirst trade in 90+ days!"
            
            message = f"""
🚨 <b>WHALE ALERT!</b> {tier_emoji}{multi_icon}

💎 <b>{token_info['name']}</b> (${token_info['symbol']})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE BOUGHT</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tier: <b>{tier}</b> {tier_emoji} ({TIER_CONFIG[tier]['name']})
Win Rate: <b>{win_rate:.1f}%</b>
Priority: <b>{priority}</b>
Chain: <b>{chain.upper()}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>TOKEN METRICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Market Cap: <b>${token_info['market_cap']:,.0f}</b>
Liquidity: <b>${token_info['liquidity']:,.0f}</b>
Price: <b>${token_info['price']:.8f}</b>

24h Volume: ${token_info['volume_24h']:,.0f}
DEX: {token_info['dex']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 <b>PRICE ACTION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5m: <b>{token_info['price_change_5m']:+.1f}%</b>
1h: <b>{token_info['price_change_1h']:+.1f}%</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 <a href="{token_info['url']}">View on DexScreener</a>
📝 <code>{token_address}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{f"🔥 <b>{multi_count} WHALES BOUGHT THIS!</b>" if multi_count >= 2 else ""}{wakeup_alert}
"""
            
            if send_telegram_alert(message):
                bot_state['alerts_sent'] += 1
                bot_state['last_buys'].append({
                    'symbol': token_info['symbol'],
                    'token': token_address,
                    'mc': token_info['market_cap'],
                    'tier': tier,
                    'timestamp': datetime.now().strftime("%m/%d %H:%M")
                })
                if len(bot_state['last_buys']) > 50:
                    bot_state['last_buys'] = bot_state['last_buys'][-50:]
            
            save_bot_state()
    
    whale_tokens[address] = current_token_set
    whale_last_check[address] = time.time()

# ============================================================
# TIERED MONITORING LOOP
# ============================================================

def tiered_monitoring_loop():
    """Main tiered monitoring loop - checks whales based on their tier"""
    
    print("🚀 Tiered monitoring started!")
    
    # First pass - baseline scan for all whales
    print("\n📋 BASELINE SCAN - All whales...")
    for whale in all_whales:
        check_whale_wallet(whale)
        time.sleep(0.3)
    
    print("✅ Baseline complete! Starting tiered monitoring...\n")
    
    cycle = 0
    
    while True:
        try:
            if bot_state.get('paused'):
                print("⏸️  Bot is paused. Waiting...")
                time.sleep(60)
                continue
            
            cycle += 1
            current_time = time.time()
            
            # Check Tier 1 (Elite) - Every 30 seconds
            for whale in tier_1_whales:
                last_check = whale_last_check.get(whale['address'], 0)
                if current_time - last_check >= 30:
                    check_whale_wallet(whale)
                    time.sleep(0.2)
            
            # Check Tier 2 (Active) - Every 3 minutes
            for whale in tier_2_whales:
                last_check = whale_last_check.get(whale['address'], 0)
                if current_time - last_check >= 180:
                    check_whale_wallet(whale)
                    time.sleep(0.3)
            
            # Check Tier 3 (Semi-Active) - Every 10 minutes
            for whale in tier_3_whales:
                last_check = whale_last_check.get(whale['address'], 0)
                if current_time - last_check >= 600:
                    check_whale_wallet(whale)
                    time.sleep(0.5)
            
            # Check Tier 4 (Dormant) - Every 24 hours
            for whale in tier_4_whales:
                last_check = whale_last_check.get(whale['address'], 0)
                if current_time - last_check >= 86400:
                    check_whale_wallet(whale, is_wakeup=True)
                    time.sleep(1)
            
            if cycle % 10 == 0:
                print(f"🔄 Cycle #{cycle} - Monitoring all tiers...")
            
            save_bot_state()
            time.sleep(5)  # Small sleep between cycles
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down gracefully...")
            save_bot_state()
            break
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            time.sleep(60)

# ============================================================
# START THREADS & MAIN LOOP
# ============================================================

if __name__ == "__main__":
    # Start background threads
    listener_thread = threading.Thread(target=command_listener_thread, daemon=True)
    sell_thread = threading.Thread(target=sell_detector_thread, daemon=True)
    perf_thread = threading.Thread(target=performance_tracker_thread, daemon=True)
    
    listener_thread.start()
    sell_thread.start()
    perf_thread.start()
    
    # Start tiered monitoring loop
    tiered_monitoring_loop()
