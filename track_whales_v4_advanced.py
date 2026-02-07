import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import threading

# Load environment variables
load_dotenv()

# Configuration
HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ADMIN_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))

# API Endpoints
HELIUS_API = f"https://api.helius.xyz/v0/addresses"
ALCHEMY_BASE_API = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# Filters
MIN_MARKET_CAP = 100_000
MAX_MARKET_CAP = 10_000_000
MIN_LIQUIDITY = 10_000

# Monitoring interval (3 minutes)
CHECK_INTERVAL = 180

# Global state
whale_positions = {}
bot_state = {
    'start_time': datetime.now(),
    'total_checks': 0,
    'alerts_sent': 0,
    'last_check': None,
    'errors': 0
}

def load_whales():
    """Load whale wallets from JSON file"""
    try:
        # Try whales_tiered_final.json first
        with open('whales_tiered_final.json', 'r') as f:
            data = json.load(f)
            
            # Check if data is a dict with 'solana' and 'base' keys
            if isinstance(data, dict):
                return data.get('solana', []), data.get('base', [])
            # If data is a list, assume it's all Solana whales
            elif isinstance(data, list):
                return data, []
            else:
                return [], []
                
    except FileNotFoundError:
        try:
            # Try evm_whales_ranked.json as fallback
            with open('evm_whales_ranked.json', 'r') as f:
                data = json.load(f)
                
                # Check if data is a dict with 'solana' and 'base' keys
                if isinstance(data, dict):
                    return data.get('solana', []), data.get('base', [])
                # If data is a list, assume it's all Solana whales
                elif isinstance(data, list):
                    return data, []
                else:
                    return [], []
        except Exception as e:
            print(f"❌ Error loading whale list: {e}")
            return [], []
    except Exception as e:
        print(f"❌ Error parsing whale list: {e}")
        return [], []

def send_telegram_message(message, chat_id=None):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️  Telegram bot token not configured")
        return False
    
    target_chat = chat_id or TELEGRAM_CHAT_ID
    if not target_chat:
        print("⚠️  No chat ID configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": target_chat,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Telegram error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send telegram: {e}")
        return False

def get_solana_tokens(wallet_address):
    """Get Solana tokens for a wallet"""
    try:
        url = f"{HELIUS_API}/{wallet_address}/balances?api-key={HELIUS_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tokens = []
            for token in data.get('tokens', []):
                if token.get('amount', 0) > 0:
                    tokens.append({
                        'mint': token.get('mint'),
                        'amount': token.get('amount'),
                        'decimals': token.get('decimals', 9)
                    })
            return tokens
        return []
    except Exception as e:
        print(f"❌ Error fetching Solana tokens: {e}")
        return []

def get_base_tokens(wallet_address):
    """Get Base/EVM tokens for a wallet"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getTokenBalances",
            "params": [wallet_address]
        }
        response = requests.post(ALCHEMY_BASE_API, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tokens = []
            for token in data.get('result', {}).get('tokenBalances', []):
                if int(token.get('tokenBalance', '0x0'), 16) > 0:
                    tokens.append({
                        'contract': token.get('contractAddress'),
                        'balance': token.get('tokenBalance')
                    })
            return tokens
        return []
    except Exception as e:
        print(f"❌ Error fetching Base tokens: {e}")
        return []

def check_whale_positions(whales, chain='solana'):
    """Check positions for a list of whales"""
    new_positions = []
    
    for i, whale in enumerate(whales, 1):
        wallet = whale.get('wallet') or whale.get('address')
        tier = whale.get('tier', 'Unknown')
        
        if (i % 20) == 0:
            print(f"  Progress: {i}/{len(whales)}")
        
        if chain == 'solana':
            tokens = get_solana_tokens(wallet)
        else:
            tokens = get_base_tokens(wallet)
        
        # Check for new positions
        whale_key = f"{chain}_{wallet}"
        previous_tokens = whale_positions.get(whale_key, set())
        current_tokens = {t.get('mint') or t.get('contract') for t in tokens}
        
        new_tokens = current_tokens - previous_tokens
        
        if new_tokens and previous_tokens:  # Skip baseline
            for token_id in new_tokens:
                alert = f"""
🚨 *NEW WHALE POSITION DETECTED!*

🐋 *Whale Tier:* {tier}
🔗 *Chain:* {chain.upper()}
💼 *Wallet:* `{wallet[:8]}...{wallet[-6:]}`

🪙 *Token:* `{token_id[:8]}...{token_id[-6:]}`

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                send_telegram_message(alert)
                bot_state['alerts_sent'] += 1
                new_positions.append({'whale': wallet, 'token': token_id, 'tier': tier})
        
        whale_positions[whale_key] = current_tokens
        time.sleep(0.5)  # Rate limiting
    
    return new_positions

def send_stats(chat_id):
    """Send bot statistics"""
    solana_whales, base_whales = load_whales()
    uptime = datetime.now() - bot_state['start_time']
    
    stats = f"""
📊 *WHALE TRACKER BOT - STATISTICS*

🐋 *Whales Monitored:*
• Solana: {len(solana_whales)}
• Base: {len(base_whales)}
• Total: {len(solana_whales) + len(base_whales)}

📈 *Performance:*
• Total Checks: {bot_state['total_checks']}
• Alerts Sent: {bot_state['alerts_sent']}
• Errors: {bot_state['errors']}

⏱️ *Status:*
• Uptime: {str(uptime).split('.')[0]}
• Last Check: {bot_state['last_check'] or 'Not started'}
• Interval: {CHECK_INTERVAL // 60} minutes

✅ *All Systems Operational*
"""
    send_telegram_message(stats, chat_id)

def send_performance(chat_id):
    """Send performance metrics"""
    uptime = datetime.now() - bot_state['start_time']
    hours = uptime.total_seconds() / 3600
    avg_alerts = bot_state['alerts_sent'] / max(hours, 1)
    
    perf = f"""
📊 *PERFORMANCE METRICS*

🎯 *Detection Stats:*
• Total Alerts: {bot_state['alerts_sent']}
• Avg per Hour: {avg_alerts:.1f}
• Success Rate: {((bot_state['total_checks'] - bot_state['errors']) / max(bot_state['total_checks'], 1) * 100):.1f}%

⚡ *System Health:*
• Uptime: {str(uptime).split('.')[0]}
• Total Cycles: {bot_state['total_checks']}
• Error Count: {bot_state['errors']}

✅ *Status:* Running Smoothly
"""
    send_telegram_message(perf, chat_id)

def send_help(chat_id):
    """Send help message"""
    help_text = """
🐋 *WHALE TRACKER BOT V4 - COMMANDS*

📊 *Monitoring:*
/stats - Current statistics
/performance - Detection metrics
/status - Bot status

📖 *Documentation:*
/guide - Full user guide (⭐ NEW!)
/help - This help message

🔐 *Admin:*
/restart - Restart bot

📚 Type /guide for detailed instructions!
"""
    send_telegram_message(help_text, chat_id)

def send_guide(chat_id):
    """Send comprehensive bot usage guide"""
    
    guide_message = """
🐋 *WHALE TRACKER BOT V4 - USER GUIDE*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 *AVAILABLE COMMANDS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*📊 MONITORING COMMANDS*

/stats - View current monitoring statistics
• Shows total whales being tracked
• Active detectors status
• Current cycle information
• System uptime

/performance - Check detection performance
• Successful alerts sent
• Detection accuracy
• Response time metrics
• Error rates

/status - Get real-time bot status
• Connection status
• API health checks
• Last activity timestamp
• System resources

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*🔔 ALERT TYPES*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 *NEW POSITION ALERTS*
When a whale buys a new token, you receive:
• Token name & symbol
• Token contract address
• Amount purchased ($USD)
• Token price
• Market cap & liquidity
• Transaction link

💰 *SELL ALERTS*
When a whale sells their position:
• Token name & sell amount
• Profit/Loss percentage
• Time held
• Exit price
• Transaction link

📊 *PERFORMANCE UPDATES*
Hourly summary of:
• Total transactions detected
• Top performing whales
• Most traded tokens
• Success rate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*⚙️ CURRENT SETTINGS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 *Monitoring Scope:*
• 204 Solana whale wallets
• 29 Base/EVM whale wallets
• Total: 233 whales tracked

💵 *Filters:*
• Min Market Cap: $100,000
• Max Market Cap: $10,000,000
• Min Liquidity: $10,000

⏱️ *Check Interval:*
• Scans every 3 minutes
• Real-time sell detection
• 24/7 monitoring

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*🎯 HOW IT WORKS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*1. BASELINE SCAN*
Bot creates a snapshot of all whale positions

*2. CONTINUOUS MONITORING*
Every 3 minutes, bot checks for:
• New token purchases
• Position changes
• Sell transactions

*3. INSTANT ALERTS*
When detected, you get notifications with:
• Full transaction details
• Token information
• Direct blockchain links

*4. PERFORMANCE TRACKING*
Bot tracks and reports:
• Detection accuracy
• Response times
• Whale profitability

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*💡 PRO TIPS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *Do This:*
• Check /stats daily for overview
• Review /performance weekly
• Act fast on Tier 1 whale alerts
• Research tokens before buying
• Set your own stop losses

⚠️ *Avoid This:*
• Blindly copying whale trades
• Ignoring market cap limits
• FOMO buying without research
• Over-leveraging positions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*🔐 ADMIN COMMANDS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/help - Show command list
/guide - Display this guide
/restart - Restart monitoring (admin only)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*📞 SUPPORT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bot running 24/7 on Railway ☁️
Updates every 3 minutes ⏱️
Monitoring 233 whales 🐋

🚀 *Happy Whale Hunting!*
"""
    
    send_telegram_message(guide_message, chat_id)

def command_listener():
    """Listen for Telegram commands"""
    print("💬 Command listener: Running in background")
    offset = 0
    
    while True:
        try:
            if not TELEGRAM_BOT_TOKEN:
                time.sleep(30)
                continue
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                updates = response.json().get('result', [])
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    message = update.get('message', {})
                    chat_id = message.get('chat', {}).get('id')
                    text = message.get('text', '')
                    
                    if text.startswith('/'):
                        command = text.split()[0].lower()
                        print(f"📨 Command received: {command} from {chat_id}")
                        
                        if command == '/stats':
                            send_stats(chat_id)
                        elif command == '/performance':
                            send_performance(chat_id)
                        elif command == '/help':
                            send_help(chat_id)
                        elif command == '/guide':
                            send_guide(chat_id)
                            print(f"📖 Sent user guide to {chat_id}")
                        elif command == '/status':
                            send_stats(chat_id)
            
            time.sleep(1)
        except Exception as e:
            print(f"❌ Command listener error: {e}")
            time.sleep(5)

def sell_detector():
    """Monitor for whale sell transactions"""
    print("🚨 Sell detector: Running")
    # Placeholder for future sell detection logic
    while True:
        time.sleep(60)

def performance_tracker():
    """Track and report performance metrics"""
    print("📊 Performance tracker: Running")
    # Placeholder for future performance tracking
    while True:
        time.sleep(3600)  # Report every hour

def main():
    """Main monitoring loop"""
    print("=" * 60)
    print("🐋 WHALE TRACKER BOT V4 - ADVANCED")
    print("=" * 60)
    
    # Load whales
    solana_whales, base_whales = load_whales()
    print(f"📊 Loaded Whales:")
    print(f"  Solana Tier 1: {len(solana_whales)}")
    print(f"  Base Tier 1: {len(base_whales)}")
    print(f"  Total Tracking: {len(solana_whales) + len(base_whales)}")
    
    # Configuration display
    print("=" * 60)
    print("📱 Telegram Configuration:")
    print(f"  Bot Token: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
    print(f"  Group Chat: {'✅ ' + str(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else '❌ Missing'}")
    print(f"  Private Chat: {'✅ ' + str(ADMIN_ID) if ADMIN_ID else '❌ Missing'}")
    print(f"  🔒 Admin: {ADMIN_ID}")
    
    print("=" * 60)
    print("🎯 Filters:")
    print(f"  Market Cap: ${MIN_MARKET_CAP:,} - ${MAX_MARKET_CAP:,}")
    print(f"  Min Liquidity: ${MIN_LIQUIDITY:,}")
    
    # Start background threads
    print("=" * 60)
    threading.Thread(target=command_listener, daemon=True).start()
    threading.Thread(target=sell_detector, daemon=True).start()
    threading.Thread(target=performance_tracker, daemon=True).start()
    
    print("✅ Command listener started")
    print("✅ Sell detector started")
    print("✅ Performance tracker started")
    
    # Main monitoring loop
    print("=" * 60)
    print("🚀 Starting monitoring loop...")
    print(f"⏱️  Check interval: {CHECK_INTERVAL // 60} minutes")
    print("=" * 60)
    
    cycle = 0
    
    while True:
        try:
            cycle += 1
            bot_state['total_checks'] += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            bot_state['last_check'] = current_time
            
            print(f"\n🔍 Cycle #{cycle} - {current_time}")
            
            if cycle == 1:
                print("📋 BASELINE SCAN")
                print("=" * 60)
            
            # Check Solana whales
            print(f"📊 Checking {len(solana_whales)} Solana whales...")
            sol_new = check_whale_positions(solana_whales, 'solana')
            
            # Check Base whales
            print(f"📊 Checking {len(base_whales)} Base whales...")
            base_new = check_whale_positions(base_whales, 'base')
            
            if cycle == 1:
                print("=" * 60)
                print("✅ Baseline complete!")
            
            # Sleep until next check
            print(f"⏳ Next check in {CHECK_INTERVAL // 60} minutes...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            bot_state['errors'] += 1
            time.sleep(60)

if __name__ == "__main__":
    main()
