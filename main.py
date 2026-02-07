"""
Whale Tracker Bot V4 - Advanced Edition
Multi-chain whale monitoring with intelligent tier system
"""

import json
import time
import requests
import threading
from datetime import datetime, timedelta
from collections import defaultdict

# Import configuration
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_GROUP_ID,
    ADMIN_USER_ID,
    TIER_CONFIG,
    DEFAULT_FILTERS
)

# Import utilities
from utils import (
    send_telegram_message,
    send_telegram_alert,
    get_token_info,
    get_solana_tokens,
    get_base_tokens,
    passes_filters,
    format_number,
    check_whale_balance
)

# Import commands
from commands import handle_command

# Bot state
bot_state = {
    'tracked_tokens': {},
    'whale_baselines': {},
    'tier_changes': [],
    'cycle_count': 0
}

def load_whales():
    """Load whale data from JSON file"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        # Separate by chain and tier
        base_tier1 = [w for w in whales if w.get('chain') == 'base' and w.get('tier') == 1]
        sol_tier1 = [w for w in whales if w.get('chain') == 'sol' and w.get('tier') == 1]

        print(f"  Base Tier 1: {len(base_tier1)}")
        print(f"  Solana Tier 1: {len(sol_tier1)}")
        print(f"  Total Tracking: {len(base_tier1) + len(sol_tier1)}")

        return whales

    except FileNotFoundError:
        print("❌ whales_tiered_final.json not found!")
        return []

def check_whale_tokens(whale):
    """Check current tokens held by whale"""
    address = whale.get('address')
    chain = whale.get('chain', 'sol')

    try:
        if chain == 'sol':
            tokens = get_solana_tokens(address)
        elif chain == 'base':
            tokens = get_base_tokens(address)
        else:
            return []

        # Extract token addresses
        if chain == 'sol':
            return [t.get('mint') for t in tokens if t.get('amount', 0) > 0]
        else:
            return [t.get('address') for t in tokens if t.get('balance', 0) > 0]

    except Exception as e:
        print(f"  ⚠️ Error checking {address[:8]}: {str(e)}")
        return []

def send_buy_alert(whale, token_address, chain):
    """Send whale buy alert"""
    try:
        # Get token info
        token_info = get_token_info(token_address, chain)

        if not token_info:
            print(f"  ⚠️ Could not fetch token info")
            return

        # Check if passes filters
        if not passes_filters(token_info, DEFAULT_FILTERS):
            print(f"  ⚠️ Token failed quality filters")
            return

        # Prepare alert message
        whale_addr = whale.get('address', 'Unknown')
        whale_name = whale.get('name', f"{whale_addr[:6]}...{whale_addr[-4:]}")
        tier = whale.get('tier', 3)
        is_kol = whale.get('type') == 'kol'
        twitter = whale.get('twitter', '')

        symbol = token_info.get('symbol', 'UNKNOWN')
        name = token_info.get('name', 'Unknown Token')
        mc = token_info.get('mc', 0)
        liq = token_info.get('liquidity', 0)
        vol_24h = token_info.get('volume_24h', 0)
        dex_url = token_info.get('dex_url', '')

        # Build alert
        if is_kol:
            alert = f"🌟 KOL ALERT! 🔥\n\n"
            alert += f"💎 {name} (${symbol})\n"
            alert += f"🐦 {twitter} | Tier {tier} KOL\n\n"
        else:
            tier_emoji = {1: "🔥", 2: "⭐", 3: "📊", 4: "💤"}
            alert = f"{tier_emoji.get(tier, '🐋')} WHALE ALERT - Tier {tier}\n\n"
            alert += f"💎 {name} (${symbol})\n"
            alert += f"🐋 {whale_name}\n\n"

        alert += f"📊 Token Metrics:\n"
        alert += f"  MC: {format_number(mc)}\n"
        alert += f"  Liquidity: {format_number(liq)}\n"
        alert += f"  24h Volume: {format_number(vol_24h)}\n\n"

        alert += f"🔗 {dex_url}\n\n"
        alert += f"⚡ Chain: {chain.upper()}"

        # Send alert
        send_telegram_alert(alert)

        # Track token
        bot_state['tracked_tokens'][token_address] = {
            'symbol': symbol,
            'name': name,
            'chain': chain,
            'entry_price': token_info.get('price', 0),
            'current_price': token_info.get('price', 0),
            'entry_mc': mc,
            'whale_buyers': [{'address': whale_addr, 'is_kol': is_kol, 'name': whale_name}],
            'first_seen': datetime.now().isoformat(),
            'active': True
        }

        print(f"  ✅ Alert sent for {symbol}")

    except Exception as e:
        print(f"  ❌ Error sending alert: {str(e)}")

def command_listener_thread():
    """
    Listen for Telegram commands in background
    Uses long polling to get updates
    """
    print("✅ Command listener started")

    last_update_id = 0

    while True:
        try:
            # Get updates from Telegram
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {
                'offset': last_update_id + 1,
                'timeout': 30,
                'allowed_updates': ['message']
            }

            response = requests.get(url, params=params, timeout=35)

            if response.status_code == 200:
                data = response.json()

                if data.get('ok') and data.get('result'):
                    for update in data['result']:
                        last_update_id = update['update_id']

                        # Check if it's a message with text (command)
                        if 'message' in update and 'text' in update['message']:
                            message = update['message']
                            text = message['text'].strip()
                            chat_id = message['chat']['id']

                            # Only respond to admin
                            if chat_id != ADMIN_USER_ID:
                                continue

                            # Check if it's a command
                            if text.startswith('/'):
                                print(f"💬 Command: {text}")

                                # Handle the command
                                try:
                                    # Get response
                                    response_text = handle_command(update, None, bot_state)

                                    # Send response back to Telegram
                                    if response_text:
                                        # Use send_telegram_message with specific chat_id
                                        success = send_telegram_message(response_text, chat_id=chat_id)

                                        if success:
                                            print(f"   ✅ Response sent to {chat_id}!")
                                        else:
                                            print(f"   ❌ Failed to send response")
                                    else:
                                        print(f"   ⚠️ Command returned empty response")

                                except Exception as e:
                                    error_msg = f"Error processing command: {str(e)}"
                                    print(f"   ❌ {error_msg}")
                                    send_telegram_message(error_msg, chat_id=chat_id)

            else:
                print(f"⚠️ Telegram API error: {response.status_code}")
                time.sleep(5)

        except requests.exceptions.Timeout:
            # Timeout is normal with long polling
            continue

        except Exception as e:
            print(f"❌ Command listener error: {str(e)}")
            time.sleep(10)

def sell_detector_thread():
    """Monitor tracked tokens for whale exits"""
    print("✅ Sell detector started")

    while True:
        try:
            time.sleep(120)  # Check every 2 minutes

            if not bot_state['tracked_tokens']:
                continue

            print("  🔍 Checking for whale sells...")

            for token_addr, data in bot_state['tracked_tokens'].items():
                if not data.get('active'):
                    continue

                chain = data.get('chain', 'sol')
                whale_buyers = data.get('whale_buyers', [])

                # Check each whale's balance
                for whale in whale_buyers:
                    whale_addr = whale.get('address')
                    balance = check_whale_balance(whale_addr, token_addr, chain)

                    # If balance is 0 or very low, whale sold
                    if balance < 0.1:
                        # Send sell alert
                        alert = f"⚠️ WHALE SELL ALERT!\n\n"
                        alert += f"💎 {data.get('symbol', 'Token')}\n"
                        alert += f"🐋 {whale.get('name', whale_addr[:8])} exited position\n\n"
                        alert += f"Consider taking profits! 💰"

                        send_telegram_alert(alert)
                        print(f"  📉 Whale sold: {data.get('symbol')}")

        except Exception as e:
            print(f"❌ Sell detector error: {str(e)}")
            time.sleep(60)

def performance_tracker_thread():
    """Track token prices and send milestone alerts"""
    print("✅ Performance tracker started")

    while True:
        try:
            time.sleep(60)  # Check every minute

            if not bot_state['tracked_tokens']:
                continue

            for token_addr, data in bot_state['tracked_tokens'].items():
                if not data.get('active'):
                    continue

                chain = data.get('chain', 'sol')
                entry_price = data.get('entry_price', 0)

                if entry_price == 0:
                    continue

                # Get current price
                token_info = get_token_info(token_addr, chain)
                if not token_info:
                    continue

                current_price = token_info.get('price', 0)
                data['current_price'] = current_price

                # Calculate gain
                gain_pct = ((current_price - entry_price) / entry_price) * 100
                data['current_gain'] = gain_pct

                # Check for milestones
                milestones = [10, 25, 50, 100, 200]
                last_milestone = data.get('last_milestone', 0)

                for milestone in milestones:
                    if gain_pct >= milestone and last_milestone < milestone:
                        # Send milestone alert
                        alert = f"📊 PRICE UPDATE!\n\n"
                        alert += f"💎 {data.get('symbol', 'Token')}\n"
                        alert += f"📈 +{gain_pct:.1f}% since whale entry!\n\n"
                        alert += f"Entry: ${entry_price:.8f}\n"
                        alert += f"Current: ${current_price:.8f}\n\n"
                        alert += f"Consider taking profits! 💰"

                        send_telegram_alert(alert)
                        data['last_milestone'] = milestone
                        print(f"  📈 Milestone {milestone}% hit: {data.get('symbol')}")
                        break

        except Exception as e:
            print(f"❌ Performance tracker error: {str(e)}")
            time.sleep(60)

def monitor_whales():
    """Main monitoring loop"""
    whales = load_whales()

    if not whales:
        print("❌ No whales to monitor!")
        return

    # Start background threads
    print("🚀 Starting monitoring loop...")
    print(f"⏱️  Check interval: 3 minutes")
    print(f"💬 Command listener: Running in background")
    print(f"📊 Performance tracker: Running")
    print(f"🚨 Sell detector: Running")
    print("=" * 60)

    # Start threads
    threading.Thread(target=command_listener_thread, daemon=True).start()
    threading.Thread(target=sell_detector_thread, daemon=True).start()
    threading.Thread(target=performance_tracker_thread, daemon=True).start()

    print("=" * 60)

    # Get Tier 1 whales only
    tier1_whales = [w for w in whales if w.get('tier') == 1]
    sol_whales = [w for w in tier1_whales if w.get('chain') == 'sol']
    base_whales = [w for w in tier1_whales if w.get('chain') == 'base']

    first_run = True

    while True:
        try:
            bot_state['cycle_count'] += 1
            cycle_num = bot_state['cycle_count']

            print(f"🔍 Cycle #{cycle_num} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            if first_run:
                print("📋 BASELINE SCAN")
                print("=" * 60)

            # Check Solana whales
            print(f"📊 Checking {len(sol_whales)} Solana whales...")
            for i, whale in enumerate(sol_whales, 1):
                if i % 20 == 0:
                    print(f"  Progress: {i}/{len(sol_whales)}")

                address = whale.get('address')
                current_tokens = check_whale_tokens(whale)

                if first_run:
                    # Store baseline
                    bot_state['whale_baselines'][address] = current_tokens
                else:
                    # Compare with baseline
                    baseline = bot_state['whale_baselines'].get(address, [])
                    new_tokens = set(current_tokens) - set(baseline)

                    # New tokens = whale bought!
                    for token in new_tokens:
                        print(f"  🚨 NEW BUY: {whale.get('name', address[:8])} → {token[:8]}...")
                        send_buy_alert(whale, token, 'sol')
                        time.sleep(2)  # Rate limit

                    # Update baseline
                    bot_state['whale_baselines'][address] = current_tokens

                time.sleep(0.5)  # Rate limit

            # Check Base whales
            print(f"📊 Checking {len(base_whales)} Base whales...")
            for i, whale in enumerate(base_whales, 1):
                if i % 10 == 0:
                    print(f"  Progress: {i}/{len(base_whales)}")

                address = whale.get('address')
                current_tokens = check_whale_tokens(whale)

                if first_run:
                    bot_state['whale_baselines'][address] = current_tokens
                else:
                    baseline = bot_state['whale_baselines'].get(address, [])
                    new_tokens = set(current_tokens) - set(baseline)

                    for token in new_tokens:
                        print(f"  🚨 NEW BUY: {whale.get('name', address[:8])} → {token[:8]}...")
                        send_buy_alert(whale, token, 'base')
                        time.sleep(2)

                    bot_state['whale_baselines'][address] = current_tokens

                time.sleep(0.5)

            if first_run:
                print("✅ Baseline scan complete!")
                print("🚀 Starting LIVE monitoring...")
                first_run = False
            else:
                print(f"✅ Cycle #{cycle_num} complete")

            print("⏳ Next check in 3 minutes...")
            print("=" * 60)
            time.sleep(180)  # Wait 3 minutes

        except Exception as e:
            print(f"❌ Error in monitoring loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    print("=" * 60)
    print("🐋 WHALE TRACKER BOT V4 - ADVANCED")
    print("=" * 60)
    print("📊 Loaded Whales:")

    # Validate configuration
    print("📱 Telegram Configuration:")
    print(f"  Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
    print(f"  Private Chat: {'✅ ' + str(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else '❌ Missing'}")
    print(f"  Group Chat: {'✅ ' + str(TELEGRAM_GROUP_ID) if TELEGRAM_GROUP_ID else '⚠️ Not set'}")
    print(f"  🔒 Admin: {ADMIN_USER_ID}")
    print(f"  Commands: ✅ Enabled - Instant response!")
    print(f"  Alerts: ✅ Sent to BOTH private + group")
    print(f"  🆕 Multi-Buy Detection: ON")
    print(f"  🆕 TRUE Whale Exit Detection: ON")
    print(f"  🆕 Performance Tracking: ON")
    print(f"  🆕 Price Follow-Up: ON")

    print("🎯 Filters:")
    print(f"  Market Cap: ${DEFAULT_FILTERS['mc_min']:,} - ${DEFAULT_FILTERS['mc_max']:,}")
    print(f"  Min Liquidity: ${DEFAULT_FILTERS['liq_min']:,}")
    print("=" * 60)

    # Start monitoring
    monitor_whales()
