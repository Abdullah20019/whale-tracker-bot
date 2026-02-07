import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import threading

load_dotenv()

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

ADMIN_USER_ID = 1930784205

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

# ============================================================
# Bot State Management + Performance Tracking
# ============================================================

bot_state = {
    'paused': False,
    'filters': {
        'mc_min': 100000,
        'mc_max': 10000000,
        'liq_min': 10000,
        'vol_liq_max': 50,
        'buy_sell_max': 5,
        'min_age_hours': 1,
        'min_txns': 50
    },
    'alerts_sent': 0,
    'tokens_filtered': 0,
    'last_buys': [],
    'start_time': time.time(),
    'last_update_id': 0,
    'tracked_tokens': {},
    'multi_buys': {},
    'whale_performance': {},
    'whale_token_balances': {}
}

def save_bot_state():
    with open('bot_state.json', 'w') as f:
        json.dump(bot_state, f, indent=2)

def load_bot_state():
    global bot_state
    try:
        with open('bot_state.json', 'r') as f:
            loaded = json.load(f)
            bot_state.update(loaded)
            bot_state['start_time'] = time.time()
            
            if 'tracked_tokens' not in bot_state:
                bot_state['tracked_tokens'] = {}
            if 'multi_buys' not in bot_state:
                bot_state['multi_buys'] = {}
            if 'whale_performance' not in bot_state:
                bot_state['whale_performance'] = {}
            if 'whale_token_balances' not in bot_state:
                bot_state['whale_token_balances'] = {}
    except FileNotFoundError:
        save_bot_state()

load_bot_state()

print("="*60)
print("🐋 WHALE TRACKER BOT V4 - ADVANCED")
print("="*60)

# Load whales
with open('whales_tiered_final.json', 'r') as f:
    all_whales = json.load(f)

tier_1_whales = [w for w in all_whales if w.get('tier') == 1]

base_whales = [w for w in tier_1_whales if w['chain'] == 'base']
solana_whales = [w for w in tier_1_whales if w['chain'] == 'solana']

print(f"\n📊 Loaded Whales:")
print(f"  Base Tier 1: {len(base_whales)}")
print(f"  Solana Tier 1: {len(solana_whales)}")
print(f"  Total Tracking: {len(tier_1_whales)}")

# Track known tokens per whale
whale_tokens = {}
for whale in tier_1_whales:
    whale_tokens[whale['address']] = set()

print(f"\n📱 Telegram Configuration:")
print(f"  Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
print(f"  Private Chat: ✅ 1930784205")
print(f"  Group Chat: ✅ -1003704810993")
print(f"  🔒 Admin: {ADMIN_USER_ID}")

if TELEGRAM_BOT_TOKEN:
    print(f"  Commands: ✅ Enabled - Instant response!")
    print(f"  Alerts: ✅ Sent to BOTH private + group")
    print(f"  🆕 Multi-Buy Detection: ON")
    print(f"  🆕 TRUE Whale Exit Detection: ON")
    print(f"  🆕 Performance Tracking: ON")
    print(f"  🆕 Price Follow-Up: ON")

print(f"\n🎯 Filters:")
print(f"  Market Cap: ${bot_state['filters']['mc_min']:,} - ${bot_state['filters']['mc_max']:,}")
print(f"  Min Liquidity: ${bot_state['filters']['liq_min']:,}")

print(f"\n🚀 Starting monitoring loop...")
print(f"⏱️  Check interval: 3 minutes")
print(f"💬 Command listener: Running in background")
print(f"📊 Performance tracker: Running")
print(f"🚨 Sell detector: Running")
print("="*60 + "\n")

# ============================================================
# Blacklist
# ============================================================

BLACKLIST_TOKENS = {
    'So11111111111111111111111111111111111111112',
    'EPjFWdd5AufqSSqewy3WZaNW1pF3Q8dTMm24FYzJR8o',
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
    'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    '0x4200000000000000000000000000000000000006',
    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
}

# ============================================================
# Telegram Functions
# ============================================================

def send_telegram_message(message, chat_id=None):
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    success = False
    
    if chat_id:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                success = True
        except:
            pass
    else:
        private_chat = "1930784205"
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": private_chat,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                success = True
        except:
            pass
        
        group_chat = "-1003704810993"
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": group_chat,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                success = True
        except:
            pass
    
    return success

def send_telegram_alert(message):
    success = send_telegram_message(message)
    if success:
        print("  ✅ Alert sent!")
    return success

# ============================================================
# Performance Tracking Functions
# ============================================================

def track_token_buy(token_address, whale_address, initial_price, mc, symbol, chain, balance):
    """Start tracking a token after whale buy"""
    
    if token_address not in bot_state['tracked_tokens']:
        bot_state['tracked_tokens'][token_address] = {
            'symbol': symbol,
            'chain': chain,
            'initial_price': initial_price,
            'initial_mc': mc,
            'current_price': initial_price,
            'highest_price': initial_price,
            'max_gain': 0,
            'current_gain': 0,
            'whales_bought': [whale_address],
            'whale_balances': {whale_address: balance},
            'first_alert_time': time.time(),
            'last_check_time': time.time(),
            'alerts_sent': {
                '10': False,
                '25': False,
                '50': False,
                '100': False,
                '200': False
            },
            'status': 'active',
            'sells_detected': []
        }
    else:
        if whale_address not in bot_state['tracked_tokens'][token_address]['whales_bought']:
            bot_state['tracked_tokens'][token_address]['whales_bought'].append(whale_address)
            bot_state['tracked_tokens'][token_address]['whale_balances'][whale_address] = balance
    
    # Also track in whale_token_balances for sell detection
    whale_key = f"{whale_address}_{token_address}"
    bot_state['whale_token_balances'][whale_key] = {
        'whale': whale_address,
        'token': token_address,
        'symbol': symbol,
        'chain': chain,
        'initial_balance': balance,
        'current_balance': balance,
        'last_check': time.time()
    }
    
    save_bot_state()

def update_whale_performance(whale_address, token_gained):
    """Update whale's performance stats"""
    
    if whale_address not in bot_state['whale_performance']:
        bot_state['whale_performance'][whale_address] = {
            'tokens_tracked': 0,
            'successful_calls': 0,
            'total_gain': 0,
            'best_call': 0,
            'worst_call': 0
        }
    
    stats = bot_state['whale_performance'][whale_address]
    stats['tokens_tracked'] += 1
    stats['total_gain'] += token_gained
    
    if token_gained >= 100:
        stats['successful_calls'] += 1
    
    if token_gained > stats['best_call']:
        stats['best_call'] = token_gained
    
    if token_gained < stats['worst_call']:
        stats['worst_call'] = token_gained
    
    save_bot_state()

def check_multi_buy(token_address):
    """Check if multiple whales bought same token"""
    
    if token_address in bot_state['tracked_tokens']:
        whale_count = len(bot_state['tracked_tokens'][token_address]['whales_bought'])
        
        if whale_count >= 2 and token_address not in bot_state['multi_buys']:
            bot_state['multi_buys'][token_address] = {
                'whale_count': whale_count,
                'detected_time': time.time()
            }
            return whale_count
    
    return 0

# ============================================================
# NEW: Whale Sell Detection Functions
# ============================================================

def check_whale_sells_solana():
    """Check if tracked whales sold any tokens (Solana)"""
    
    for whale_key, balance_data in list(bot_state['whale_token_balances'].items()):
        if balance_data['chain'] != 'solana':
            continue
        
        if time.time() - balance_data.get('last_check', 0) < 120:
            continue
        
        whale_address = balance_data['whale']
        token_address = balance_data['token']
        initial_balance = balance_data['initial_balance']
        
        current_tokens = get_solana_tokens(whale_address)
        current_balance = 0
        
        for token in current_tokens:
            if token['address'] == token_address:
                current_balance = token['balance']
                break
        
        balance_data['current_balance'] = current_balance
        balance_data['last_check'] = time.time()
        
        if initial_balance > 0:
            balance_change_pct = ((current_balance - initial_balance) / initial_balance) * 100
            
            if balance_change_pct < -30:
                token_info = get_token_info(token_address, 'solana')
                
                if token_info:
                    sold_amount = initial_balance - current_balance
                    sold_pct = abs(balance_change_pct)
                    
                    tracked_token = bot_state['tracked_tokens'].get(token_address, {})
                    initial_price = tracked_token.get('initial_price', 0)
                    current_price = token_info['price']
                    
                    if initial_price > 0:
                        price_gain = ((current_price - initial_price) / initial_price) * 100
                    else:
                        price_gain = 0
                    
                    message = f"""
🚨 <b>WHALE EXIT DETECTED!</b> 🚨

💎 <b>{balance_data['symbol']}</b> ({token_address[:16]}...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE SOLD</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Whale: <code>{whale_address[:16]}...</code>

💰 Sold: <b>{sold_pct:.1f}%</b> of position
🪙 Amount: <b>{sold_amount:,.0f}</b> tokens
📊 Remaining: <b>{current_balance:,.0f}</b> tokens

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 <b>PERFORMANCE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Entry Price: ${initial_price:.8f}
Exit Price: ${current_price:.8f}
Gain: <b>{price_gain:+.1f}%</b>

Current MC: ${token_info['market_cap']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <b>Consider taking profits if holding!</b>

🔗 <a href="{token_info['url']}">View on DexScreener</a>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    
                    send_telegram_alert(message)
                    
                    if token_address in bot_state['tracked_tokens']:
                        if whale_address not in bot_state['tracked_tokens'][token_address].get('sells_detected', []):
                            bot_state['tracked_tokens'][token_address]['sells_detected'].append(whale_address)
                    
                    update_whale_performance(whale_address, price_gain)
                    
                    if current_balance == 0:
                        del bot_state['whale_token_balances'][whale_key]
                    
                    save_bot_state()
                    
                    print(f"  🚨 SELL DETECTED: {balance_data['symbol']} by whale {whale_address[:8]}...")

def check_whale_sells_base():
    """Check if tracked whales sold any tokens (Base)"""
    
    for whale_key, balance_data in list(bot_state['whale_token_balances'].items()):
        if balance_data['chain'] != 'base':
            continue
        
        if time.time() - balance_data.get('last_check', 0) < 120:
            continue
        
        whale_address = balance_data['whale']
        token_address = balance_data['token']
        initial_balance = balance_data['initial_balance']
        
        current_tokens = get_base_tokens(whale_address)
        current_balance = 0
        
        for token in current_tokens:
            if token['address'].lower() == token_address.lower():
                current_balance = token['balance']
                break
        
        balance_data['current_balance'] = current_balance
        balance_data['last_check'] = time.time()
        
        if initial_balance > 0:
            balance_change_pct = ((current_balance - initial_balance) / initial_balance) * 100
            
            if balance_change_pct < -30:
                token_info = get_token_info(token_address, 'base')
                
                if token_info:
                    sold_pct = abs(balance_change_pct)
                    
                    tracked_token = bot_state['tracked_tokens'].get(token_address, {})
                    initial_price = tracked_token.get('initial_price', 0)
                    current_price = token_info['price']
                    
                    if initial_price > 0:
                        price_gain = ((current_price - initial_price) / initial_price) * 100
                    else:
                        price_gain = 0
                    
                    message = f"""
🚨 <b>WHALE EXIT DETECTED!</b> 🚨

💎 <b>{balance_data['symbol']}</b> ({token_address[:16]}...)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE SOLD</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Whale: <code>{whale_address[:16]}...</code>

💰 Sold: <b>{sold_pct:.1f}%</b> of position
⛓️ Chain: <b>BASE</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 <b>PERFORMANCE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Entry Price: ${initial_price:.8f}
Exit Price: ${current_price:.8f}
Gain: <b>{price_gain:+.1f}%</b>

Current MC: ${token_info['market_cap']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ <b>Consider taking profits if holding!</b>

🔗 <a href="{token_info['url']}">View on DexScreener</a>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    
                    send_telegram_alert(message)
                    
                    if token_address in bot_state['tracked_tokens']:
                        if whale_address not in bot_state['tracked_tokens'][token_address].get('sells_detected', []):
                            bot_state['tracked_tokens'][token_address]['sells_detected'].append(whale_address)
                    
                    update_whale_performance(whale_address, price_gain)
                    
                    if current_balance == 0:
                        del bot_state['whale_token_balances'][whale_key]
                    
                    save_bot_state()
                    
                    print(f"  🚨 SELL DETECTED: {balance_data['symbol']} by whale {whale_address[:8]}...")

# ============================================================
# Command Handlers
# ============================================================

def get_bot_stats():
    with open('whales_tiered_final.json', 'r') as f:
        whales = json.load(f)
    
    tier_1 = [w for w in whales if w.get('tier') == 1]
    base = [w for w in tier_1 if w['chain'] == 'base']
    solana = [w for w in tier_1 if w['chain'] == 'solana']
    
    uptime_hours = (time.time() - bot_state.get('start_time', time.time())) / 3600
    
    tracked_count = len(bot_state.get('tracked_tokens', {}))
    multi_buy_count = len(bot_state.get('multi_buys', {}))
    monitored_positions = len(bot_state.get('whale_token_balances', {}))
    
    return f"""
📊 <b>BOT STATISTICS</b>

━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALES TRACKED</b>
━━━━━━━━━━━━━━━━━━━━
Tier 1: <b>{len(tier_1)}</b>
  • Solana: <b>{len(solana)}</b>
  • Base: <b>{len(base)}</b>

━━━━━━━━━━━━━━━━━━━━
📈 <b>ACTIVITY</b>
━━━━━━━━━━━━━━━━━━━━
Alerts Sent: <b>{bot_state.get('alerts_sent', 0)}</b>
Tokens Tracked: <b>{tracked_count}</b>
Multi-Buys: <b>{multi_buy_count}</b>
Positions Monitored: <b>{monitored_positions}</b>
Filtered: <b>{bot_state.get('tokens_filtered', 0)}</b>
Uptime: <b>{uptime_hours:.1f}h</b>

━━━━━━━━━━━━━━━━━━━━
⚙️ <b>FILTERS</b>
━━━━━━━━━━━━━━━━━━━━
MC: <b>${bot_state['filters']['mc_min']:,} - ${bot_state['filters']['mc_max']:,}</b>
Liq: <b>${bot_state['filters']['liq_min']:,}+</b>

🔔 Status: <b>{'⏸️ PAUSED' if bot_state.get('paused') else '✅ ACTIVE'}</b>
"""

def get_tracked_tokens():
    tracked = bot_state.get('tracked_tokens', {})
    
    if not tracked:
        return "📭 No tokens being tracked yet."
    
    sorted_tokens = sorted(
        tracked.items(),
        key=lambda x: x[1].get('current_gain', 0),
        reverse=True
    )
    
    message = "📊 <b>TRACKED TOKENS (Top 20)</b>\n\n"
    
    for i, (token_addr, data) in enumerate(sorted_tokens[:20], 1):
        gain = data.get('current_gain', 0)
        max_gain = data.get('max_gain', 0)
        whale_count = len(data.get('whales_bought', []))
        sells_count = len(data.get('sells_detected', []))
        
        gain_icon = "🟢" if gain > 0 else "🔴" if gain < -10 else "⚪"
        multi_icon = "🔥" if whale_count >= 3 else "⭐" if whale_count >= 2 else ""
        sell_icon = "🚨" if sells_count > 0 else ""
        
        message += f"{i}. {gain_icon} <b>{data['symbol']}</b> {multi_icon}{sell_icon}\n"
        message += f"   Gain: <b>{gain:+.1f}%</b> | ATH: <b>{max_gain:.1f}%</b>\n"
        message += f"   Whales: <b>{whale_count}</b> | Exits: <b>{sells_count}</b>\n\n"
    
    return message

def get_multi_buys():
    multi_buys = bot_state.get('multi_buys', {})
    tracked = bot_state.get('tracked_tokens', {})
    
    if not multi_buys:
        return "📭 No multi-buy events detected yet."
    
    message = "🔥 <b>MULTI-BUY ALERTS</b>\n\n"
    
    for token_addr, multi_data in list(multi_buys.items())[:15]:
        if token_addr in tracked:
            data = tracked[token_addr]
            whale_count = len(data.get('whales_bought', []))
            gain = data.get('current_gain', 0)
            sells = len(data.get('sells_detected', []))
            
            message += f"🔥 <b>{data['symbol']}</b>\n"
            message += f"   Whales: <b>{whale_count}</b> | Gain: <b>{gain:+.1f}%</b> | Exits: {sells}\n"
            message += f"   <code>{token_addr[:16]}...</code>\n\n"
    
    return message

def get_whale_performance_report():
    perf = bot_state.get('whale_performance', {})
    
    if not perf:
        return "📭 No performance data yet."
    
    whale_stats = []
    for whale_addr, stats in perf.items():
        if stats['tokens_tracked'] >= 3:
            success_rate = (stats['successful_calls'] / stats['tokens_tracked']) * 100
            avg_gain = stats['total_gain'] / stats['tokens_tracked']
            
            whale_stats.append({
                'address': whale_addr,
                'success_rate': success_rate,
                'avg_gain': avg_gain,
                'best_call': stats['best_call'],
                'tokens_tracked': stats['tokens_tracked']
            })
    
    if not whale_stats:
        return "📊 Need more data (min 3 calls per whale)"
    
    whale_stats.sort(key=lambda x: x['success_rate'], reverse=True)
    
    message = "🏆 <b>TOP PERFORMING WHALES</b>\n\n"
    
    for i, stats in enumerate(whale_stats[:10], 1):
        message += f"{i}. <code>{stats['address'][:16]}...</code>\n"
        message += f"   Success: <b>{stats['success_rate']:.0f}%</b> | Avg: <b>{stats['avg_gain']:+.1f}%</b>\n"
        message += f"   Best: <b>{stats['best_call']:.0f}%</b> | Calls: {stats['tokens_tracked']}\n\n"
    
    return message

def get_top_whales():
    with open('whales_tiered_final.json', 'r') as f:
        whales = json.load(f)
    
    tier_1 = [w for w in whales if w.get('tier') == 1]
    sorted_whales = sorted(tier_1, key=lambda x: x.get('win_count', 0), reverse=True)[:15]
    
    message = "🏆 <b>TOP 15 ELITE WHALES</b>\n\n"
    
    for i, whale in enumerate(sorted_whales, 1):
        chain_icon = "🟣" if whale['chain'] == 'solana' else "🔵"
        message += f"{i}. {chain_icon} <code>{whale['address'][:16]}...</code>\n   Wins: <b>{whale.get('win_count', 0)}</b> | WR: <b>{whale.get('win_rate', 0):.1f}%</b>\n"
        if i % 5 == 0:
            message += "\n"
    
    return message

def get_last_buys():
    last_buys = bot_state.get('last_buys', [])
    
    if not last_buys:
        return "📭 No recent buys detected yet."
    
    message = "🔥 <b>LAST 15 QUALITY BUYS</b>\n\n"
    
    for i, buy in enumerate(reversed(last_buys[-15:]), 1):
        message += f"{i}. 💎 <b>{buy['symbol']}</b> | MC: ${buy['mc']:,.0f}\n   {buy['timestamp']} | <code>{buy['token'][:16]}...</code>\n\n"
    
    return message

def get_filters_info():
    filters = bot_state['filters']
    
    return f"""
⚙️ <b>CURRENT FILTER SETTINGS</b>

━━━━━━━━━━━━━━━━━━━━
💰 Market Cap:
   Min: <b>${filters['mc_min']:,}</b>
   Max: <b>${filters['mc_max']:,}</b>

💧 Liquidity:
   Min: <b>${filters['liq_min']:,}</b>

📊 Ratios:
   Max Vol/Liq: <b>{filters['vol_liq_max']}x</b>
   Max Buy/Sell: <b>{filters['buy_sell_max']}:1</b>

⏰ Token Age:
   Min: <b>{filters['min_age_hours']}h</b>

━━━━━━━━━━━━━━━━━━━━
<b>🔒 Admin Only:</b> Use /setfilter to change
"""

def add_wallet(address, chain, user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    with open('whales_tiered_final.json', 'r') as f:
        whales = json.load(f)
    
    if any(w['address'] == address for w in whales):
        return f"❌ Wallet already tracked"
    
    new_whale = {
        'address': address,
        'chain': chain.lower(),
        'tier': 1,
        'win_count': 0,
        'win_rate': 0,
        'is_active': True,
        'source': 'manual_add',
        'added_date': datetime.now().strftime("%Y-%m-%d")
    }
    
    whales.append(new_whale)
    
    with open('whales_tiered_final.json', 'w') as f:
        json.dump(whales, f, indent=2)
    
    return f"✅ Wallet added! Now tracking {len(whales)} whales."

def remove_wallet(address, user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    with open('whales_tiered_final.json', 'r') as f:
        whales = json.load(f)
    
    original_count = len(whales)
    whales = [w for w in whales if w['address'] != address]
    
    if len(whales) == original_count:
        return f"❌ Wallet not found"
    
    with open('whales_tiered_final.json', 'w') as f:
        json.dump(whales, f, indent=2)
    
    return f"✅ Wallet removed! Now tracking {len(whales)} whales."

def set_filter(setting, value, user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    valid_settings = {
        'mc_min': 'Min Market Cap',
        'mc_max': 'Max Market Cap',
        'liq_min': 'Min Liquidity',
        'vol_liq_max': 'Max Vol/Liq',
        'buy_sell_max': 'Max Buy/Sell',
        'min_age_hours': 'Min Age',
        'min_txns': 'Min Txns'
    }
    
    if setting not in valid_settings:
        return f"❌ Invalid setting"
    
    try:
        value = float(value)
        bot_state['filters'][setting] = value
        save_bot_state()
        return f"✅ Updated {valid_settings[setting]} to {value:,.0f}"
    except:
        return "❌ Invalid value"

def pause_bot(user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    bot_state['paused'] = True
    save_bot_state()
    return "⏸️ <b>BOT PAUSED</b>"

def resume_bot(user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    bot_state['paused'] = False
    save_bot_state()
    return "▶️ <b>BOT RESUMED</b>"

def get_help():
    return """
🤖 <b>WHALE TRACKER BOT V4</b>

━━━━━━━━━━━━━━━━━━━━
📊 <b>MONITORING</b>
━━━━━━━━━━━━━━━━━━━━
/stats - Bot statistics
/topwhales - Top 15 whales
/lastbuys - Last 15 buys
/tracked - Tracked tokens
/multibuys - Multi-whale buys
/performance - Whale leaderboard

━━━━━━━━━━━━━━━━━━━━
📖 <b>DOCUMENTATION</b>
━━━━━━━━━━━━━━━━━━━━
/guide - Full user guide ⭐
/help - This help message

━━━━━━━━━━━━━━━━━━━━
🔒 <b>ADMIN ONLY</b>
━━━━━━━━━━━━━━━━━━━━
/addwallet address chain
/removewallet address
/setfilter setting value
/pause | /resume
/filters

━━━━━━━━━━━━━━━━━━━━
<b>Features:</b>
✅ Multi-buy detection
✅ TRUE whale exit alerts
✅ Performance tracking
✅ Price follow-ups
"""

def get_guide():
    return """
🐋 <b>WHALE TRACKER BOT V4 - USER GUIDE</b>

━━━━━━━━━━━━━━━━━━━━
📋 <b>AVAILABLE COMMANDS</b>
━━━━━━━━━━━━━━━━━━━━

<b>📊 MONITORING COMMANDS</b>

/stats - View current monitoring statistics
• Total whales tracked
• Active detectors status  
• System uptime

/topwhales - Top 15 elite whales
• Sorted by win count
• Win rate percentages

/lastbuys - Last 15 quality buys
• Recent whale purchases
• Market cap info

/tracked - Tracked tokens (Top 20)
• Current gains
• All-time highs
• Multi-buy indicators

/multibuys - Multi-whale buy events
• Tokens bought by 2+ whales
• Highest conviction plays

/performance - Whale leaderboard
• Success rates
• Average gains
• Best calls

━━━━━━━━━━━━━━━━━━━━
🔔 <b>ALERT TYPES</b>
━━━━━━━━━━━━━━━━━━━━

<b>🚨 NEW POSITION ALERTS</b>
When a whale buys a new token:
• Token name & symbol
• Market cap & liquidity
• Buy amount in USD
• Whale win rate
• Multi-buy detection (2+ whales)

<b>💰 WHALE EXIT ALERTS</b>
When whales sell 30%+ of position:
• Sold percentage
• Entry vs exit price
• Profit/Loss calculation
• Time held

<b>📈 PRICE MILESTONE ALERTS</b>
Automatic updates at:
• +10% | +25% | +50%
• +100% | +200%

━━━━━━━━━━━━━━━━━━━━
⚙️ <b>CURRENT SETTINGS</b>
━━━━━━━━━━━━━━━━━━━━

<b>🔍 Monitoring:</b>
• 204 Solana whales
• 29 Base/EVM whales
• Check every 3 minutes

<b>💵 Filters:</b>
• MC: $100K - $10M
• Min Liquidity: $10K
• Min Age: 1 hour
• Min Txns: 50

<b>🛡️ Safety Filters:</b>
• Vol/Liq ratio check
• Buy/Sell ratio analysis
• Liquidity verification
• Known scam blacklist

━━━━━━━━━━━━━━━━━━━━
🎯 <b>HOW IT WORKS</b>
━━━━━━━━━━━━━━━━━━━━

<b>1. BASELINE SCAN</b>
Bot snapshots all whale positions

<b>2. CONTINUOUS MONITORING</b>
Every 3 minutes checks for:
• New token purchases
• Position changes
• Sell transactions

<b>3. INSTANT ALERTS</b>
Filtered quality plays sent with:
• Full token metrics
• Whale information
• DexScreener link

<b>4. PERFORMANCE TRACKING</b>
Bot monitors and reports:
• Price milestones
• Whale exits
• Success rates

━━━━━━━━━━━━━━━━━━━━
💡 <b>PRO TIPS</b>
━━━━━━━━━━━━━━━━━━━━

<b>✅ Do This:</b>
• Check /stats daily
• Review /performance weekly
• Act fast on multi-buy alerts
• Research before buying
• Set your own stop losses
• Watch for whale exit alerts

<b>⚠️ Avoid This:</b>
• Blindly copying trades
• Ignoring market cap limits
• FOMO buying
• Over-leveraging
• Missing exit signals

━━━━━━━━━━━━━━━━━━━━
🔐 <b>ADMIN COMMANDS</b>
━━━━━━━━━━━━━━━━━━━━

/addwallet address chain
• Add new whale to track

/removewallet address
• Remove whale from tracking

/setfilter setting value
• Adjust filter parameters

/pause | /resume
• Pause/resume monitoring

/filters
• View all filter settings

━━━━━━━━━━━━━━━━━━━━
📊 <b>KEY FEATURES</b>
━━━━━━━━━━━━━━━━━━━━

✅ Multi-buy detection
✅ TRUE whale exit alerts  
✅ Performance tracking
✅ Price follow-ups
✅ Quality filtering
✅ 24/7 monitoring

━━━━━━━━━━━━━━━━━━━━
🚀 <b>Happy Whale Hunting!</b>

Bot running on Railway ☁️
Updates every 3 minutes ⏱️
Monitoring 233 elite whales 🐋
"""

def handle_command(command_text, user_id):
    parts = command_text.strip().split()
    command = parts[0].lower()
    
    if '@' in command:
        command = command.split('@')[0]
    
    if command == '/stats':
        return get_bot_stats()
    elif command == '/topwhales':
        return get_top_whales()
    elif command == '/lastbuys':
        return get_last_buys()
    elif command == '/help':
        return get_help()
    elif command == '/guide':
        return get_guide()
    elif command == '/tracked':
        return get_tracked_tokens()
    elif command == '/multibuys':
        return get_multi_buys()
    elif command == '/performance':
        return get_whale_performance_report()
    elif command == '/filters':
        return get_filters_info()
    elif command == '/addwallet':
        if len(parts) < 3:
            return "❌ Usage: /addwallet address chain"
        return add_wallet(parts[1], parts[2], user_id)
    elif command == '/removewallet':
        if len(parts) < 2:
            return "❌ Usage: /removewallet address"
        return remove_wallet(parts[1], user_id)
    elif command == '/setfilter':
        if len(parts) < 3:
            return "❌ Usage: /setfilter setting value"
        return set_filter(parts[1], parts[2], user_id)
    elif command == '/pause':
        return pause_bot(user_id)
    elif command == '/resume':
        return resume_bot(user_id)
    else:
        return "❌ Unknown command. Use /help"

# ============================================================
# Command Listener Thread
# ============================================================

def command_listener_thread():
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

listener_thread = threading.Thread(target=command_listener_thread, daemon=True)
listener_thread.start()

# ============================================================
# NEW: Sell Detector Thread
# ============================================================

def sell_detector_thread():
    """Monitor whale wallets for sells"""
    print("✅ Sell detector started")
    
    while True:
        try:
            time.sleep(120)
            
            print("  🔍 Checking for whale sells...")
            
            check_whale_sells_solana()
            check_whale_sells_base()
            
            save_bot_state()
            
        except Exception as e:
            print(f"Sell detector error: {e}")
            time.sleep(120)

sell_thread = threading.Thread(target=sell_detector_thread, daemon=True)
sell_thread.start()

# ============================================================
# Performance Tracker Thread
# ============================================================

def performance_tracker_thread():
    """Track token performance and send price updates"""
    print("✅ Performance tracker started")
    
    while True:
        try:
            time.sleep(60)
            
            tracked = bot_state.get('tracked_tokens', {})
            
            for token_addr, data in list(tracked.items()):
                if data['status'] != 'active':
                    continue
                
                if time.time() - data.get('last_check_time', 0) < 60:
                    continue
                
                token_info = get_token_info(token_addr, data['chain'])
                
                if token_info:
                    current_price = token_info['price']
                    initial_price = data['initial_price']
                    
                    current_gain = ((current_price - initial_price) / initial_price) * 100
                    
                    data['current_price'] = current_price
                    data['current_gain'] = current_gain
                    data['last_check_time'] = time.time()
                    
                    if current_gain > data['max_gain']:
                        data['max_gain'] = current_gain
                        data['highest_price'] = current_price
                    
                    milestones = [10, 25, 50, 100, 200]
                    for milestone in milestones:
                        if current_gain >= milestone and not data['alerts_sent'].get(str(milestone)):
                            whale_count = len(data['whales_bought'])
                            multi_icon = "🔥🔥🔥" if whale_count >= 3 else "🔥" if whale_count >= 2 else ""
                            
                            message = f"""
🚀 <b>PRICE UPDATE {multi_icon}</b>

💎 <b>{data['symbol']}</b> is UP <b>{current_gain:.1f}%</b>!

━━━━━━━━━━━━━━━━━━━━
📊 Initial MC: <b>${data['initial_mc']:,.0f}</b>
📊 Current MC: <b>${token_info['market_cap']:,.0f}</b>

💰 Entry: ${initial_price:.8f}
💰 Current: ${current_price:.8f}

🐋 Whales: <b>{whale_count}</b>
⏰ Time: {((time.time() - data['first_alert_time'])/3600):.1f}h ago

━━━━━━━━━━━━━━━━━━━━
🔗 <a href="{token_info['url']}">View Chart</a>
📝 <code>{token_addr}</code>
━━━━━━━━━━━━━━━━━━━━
"""
                            send_telegram_alert(message)
                            data['alerts_sent'][str(milestone)] = True
                            
                            for whale_addr in data['whales_bought']:
                                update_whale_performance(whale_addr, current_gain)
                    
                    save_bot_state()
        
        except Exception as e:
            print(f"Performance tracker error: {e}")
            time.sleep(60)

perf_thread = threading.Thread(target=performance_tracker_thread, daemon=True)
perf_thread.start()

# ============================================================
# Token Checkers
# ============================================================

def get_solana_tokens(wallet_address):
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        tokens = []
        if 'result' in data and 'value' in data['result']:
            for account in data['result']['value']:
                token_data = account['account']['data']['parsed']['info']
                mint = token_data['mint']
                balance = float(token_data['tokenAmount']['uiAmount'] or 0)
                
                if balance > 0 and mint not in BLACKLIST_TOKENS:
                    tokens.append({'address': mint, 'balance': balance})
        
        return tokens
    except:
        return []

def get_base_tokens(wallet_address):
    url = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address, "erc20"]
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        tokens = []
        if 'result' in data and 'tokenBalances' in data['result']:
            for token in data['result']['tokenBalances']:
                token_address = token['contractAddress']
                balance_hex = token.get('tokenBalance', '0x0')
                
                try:
                    balance = int(balance_hex, 16)
                except:
                    balance = 0
                
                if balance > 0 and token_address not in BLACKLIST_TOKENS:
                    tokens.append({'address': token_address, 'balance': balance})
        
        return tokens
    except:
        return []

def get_token_info(token_address, chain):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('pairs'):
            pairs = sorted(data['pairs'], key=lambda x: x.get('liquidity', {}).get('usd', 0), reverse=True)
            pair = pairs[0]
            
            fdv = pair.get('fdv', 0)
            market_cap = pair.get('marketCap', fdv)
            price = float(pair.get('priceUsd', 0))
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            volume_24h = pair.get('volume', {}).get('h24', 0)
            price_change_5m = pair.get('priceChange', {}).get('m5', 0)
            price_change_1h = pair.get('priceChange', {}).get('h1', 0)
            
            txns = pair.get('txns', {}).get('h24', {})
            buys = txns.get('buys', 0)
            sells = txns.get('sells', 0)
            
            pair_created_at = pair.get('pairCreatedAt', 0)
            
            return {
                'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                'symbol': pair.get('baseToken', {}).get('symbol', 'UNK'),
                'price': price,
                'market_cap': market_cap,
                'liquidity': liquidity,
                'volume_24h': volume_24h,
                'dex': pair.get('dexId', 'Unknown'),
                'url': pair.get('url', ''),
                'price_change_5m': price_change_5m,
                'price_change_1h': price_change_1h,
                'chain_id': pair.get('chainId', chain),
                'txns_24h': {'buys': buys, 'sells': sells},
                'pair_created_at': pair_created_at
            }
    except:
        pass
    
    return None

def passes_filters(token_info):
    if not token_info:
        return False, "No data"
    
    mc = token_info['market_cap']
    liq = token_info['liquidity']
    filters = bot_state['filters']
    
    if mc < filters['mc_min']:
        return False, f"MC too low (${mc:,.0f})"
    if mc > filters['mc_max']:
        return False, f"MC too high (${mc:,.0f})"
    if liq < filters['liq_min']:
        return False, f"Low liquidity (${liq:,.0f})"
    
    liq_ratio = (liq / mc) * 100 if mc > 0 else 0
    if liq_ratio < 5:
        return False, f"Suspicious liq ratio ({liq_ratio:.1f}%)"
    
    volume_24h = token_info.get('volume_24h', 0)
    if volume_24h > 0 and liq > 0:
        vol_liq_ratio = volume_24h / liq
        if vol_liq_ratio > filters['vol_liq_max']:
            return False, f"Fake volume ({vol_liq_ratio:.1f}x)"
    
    txns = token_info.get('txns_24h', {})
    buyers = txns.get('buys', 0)
    sellers = txns.get('sells', 0)
    
    if buyers > 0 and sellers > 0:
        buy_sell_ratio = buyers / sellers
        if buy_sell_ratio > filters['buy_sell_max']:
            return False, f"Pump pattern ({buy_sell_ratio:.1f}:1)"
        if buy_sell_ratio < 0.3:
            return False, f"Dump pattern ({buy_sell_ratio:.1f}:1)"
    
    total_txns = buyers + sellers
    if total_txns < filters['min_txns']:
        return False, f"Low activity ({total_txns} txns)"
    
    pair_created = token_info.get('pair_created_at', 0)
    if pair_created > 0:
        age_hours = (time.time() - pair_created / 1000) / 3600
        if age_hours < filters['min_age_hours']:
            return False, f"Too new ({age_hours:.1f}h)"
    
    return True, "Passed"

# ============================================================
# Main Monitoring Loop
# ============================================================

def check_whale_wallet(whale):
    """Check single whale for new positions"""
    address = whale['address']
    chain = whale['chain']
    tier = whale.get('tier', 1)
    win_rate = whale.get('win_rate', 0)
    
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
            
            passed, reason = passes_filters(token_info)
            
            if not passed:
                bot_state['tokens_filtered'] += 1
                print(f"    ❌ Filtered: {reason}")
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
            
            message = f"""
🚨 <b>WHALE ALERT! {multi_icon}</b>

💎 <b>{token_info['name']}</b> (${token_info['symbol']})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE BOUGHT</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tier: <b>{tier}</b>
Win Rate: <b>{win_rate:.1f}%</b>
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

{f"🔥 <b>{multi_count} WHALES BOUGHT THIS!</b>" if multi_count >= 2 else ""}
"""
            
            if send_telegram_alert(message):
                bot_state['alerts_sent'] += 1
                bot_state['last_buys'].append({
                    'symbol': token_info['symbol'],
                    'token': token_address,
                    'mc': token_info['market_cap'],
                    'timestamp': datetime.now().strftime("%m/%d %H:%M")
                })
                if len(bot_state['last_buys']) > 50:
                    bot_state['last_buys'] = bot_state['last_buys'][-50:]
            
            save_bot_state()
    
    whale_tokens[address] = current_token_set

def main_loop():
    """Main monitoring loop"""
    cycle = 0
    
    while True:
        try:
            if bot_state.get('paused'):
                print("⏸️  Bot is paused. Waiting...")
                time.sleep(60)
                continue
            
            cycle += 1
            print(f"\n{'='*60}")
            print(f"🔍 Cycle #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if cycle == 1:
                print("📋 BASELINE SCAN")
            
            print("="*60)
            
            print(f"\n📊 Checking {len(solana_whales)} Solana whales...")
            for i, whale in enumerate(solana_whales, 1):
                check_whale_wallet(whale)
                if i % 20 == 0:
                    print(f"  Progress: {i}/{len(solana_whales)}")
                time.sleep(0.5)
            
            print(f"\n📊 Checking {len(base_whales)} Base whales...")
            for i, whale in enumerate(base_whales, 1):
                check_whale_wallet(whale)
                if i % 10 == 0:
                    print(f"  Progress: {i}/{len(base_whales)}")
                time.sleep(0.5)
            
            print("\n" + "="*60)
            if cycle == 1:
                print("✅ Baseline complete!")
            else:
                print(f"✅ Cycle #{cycle} complete!")
            print("⏳ Next check in 3 minutes...")
            print("="*60)
            
            save_bot_state()
            time.sleep(180)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down gracefully...")
            save_bot_state()
            break
        except Exception as e:
            print(f"\n❌ Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
