"""
All Telegram command handlers
"""

import json
from datetime import datetime
from config import TIER_CONFIG, DEFAULT_FILTERS, is_admin
from state import bot_state, save_bot_state

def handle_command(command_text, user_id):
    text = command_text.strip()
    if '@' in text:
        text = text.split('@')[0]
    
    if text == '/start':
        return cmd_start(None)
    elif text == '/help':
        return cmd_help(None)
    elif text == '/stats':
        return cmd_stats(None, bot_state)
    elif text == '/tracked':
        return cmd_tracked(None, bot_state)
    elif text == '/topwhales':
        return cmd_topwhales(None, bot_state)
    elif text == '/performance':
        return cmd_performance(None, bot_state)
    elif text == '/tiers':
        return cmd_tiers(None, bot_state)
    elif text == '/tier1':
        return cmd_tier_detail(None, bot_state, 1)
    elif text == '/tier2':
        return cmd_tier_detail(None, bot_state, 2)
    elif text == '/tier3':
        return cmd_tier_detail(None, bot_state, 3)
    elif text == '/tier4':
        return cmd_tier_detail(None, bot_state, 4)
    elif text == '/multibuys':
        return cmd_multibuys(None, bot_state)
    elif text == '/promotions':
        return cmd_promotions(None, bot_state)
    elif text == '/guide':
        return cmd_guide(None)
    elif text == '/lastbuys':
        return cmd_lastbuys(None, bot_state)
    elif text == '/filters':
        return cmd_filters(None)
    elif text == '/pause':
        return cmd_pause(None, user_id)
    elif text == '/resume':
        return cmd_resume(None, user_id)
    elif text.startswith('/setfilter'):
        return cmd_setfilter(None, user_id, text)
    elif text.startswith('/addwhale'):
        return cmd_addwhale(None, user_id, text)
    elif text.startswith('/removewhale'):
        return cmd_removewhale(None, user_id, text)
    else:
        return "Unknown command. Use /help"

def cmd_start(chat_id):
    msg = "WHALE TRACKER BOT V4\n\n"
    msg += "Welcome! I monitor elite crypto whales.\n\n"
    msg += "Commands:\n"
    msg += "/help - All commands\n"
    msg += "/stats - Statistics\n"
    msg += "/tiers - View tiers"
    return msg

def cmd_help(chat_id):
    msg = "COMMANDS\n\n"
    msg += "STATISTICS\n"
    msg += "/stats - Bot stats\n"
    msg += "/tiers - Tier info\n\n"
    msg += "TRACKING\n"
    msg += "/tracked - Active tokens\n"
    msg += "/topwhales - Top performers\n"
    msg += "/lastbuys - Recent buys\n\n"
    msg += "ADMIN\n"
    msg += "/pause - Pause bot\n"
    msg += "/resume - Resume bot\n"
    msg += "/addwhale - Add whale"
    return msg

def cmd_stats(chat_id, bot_state):
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        total = len(whales)
        sol = len([w for w in whales if w.get('chain') == 'solana'])
        base = len([w for w in whales if w.get('chain') == 'base'])
        
        t1 = len([w for w in whales if w.get('tier') == 1])
        t2 = len([w for w in whales if w.get('tier') == 2])
        t3 = len([w for w in whales if w.get('tier') == 3])
        t4 = len([w for w in whales if w.get('tier') == 4])
        
        tracked = bot_state.get('tracked_tokens', {})
        active = len([t for t in tracked.values() if t.get('status') == 'active'])
        alerts = bot_state.get('alerts_sent', 0)
        
        msg = "BOT STATISTICS\n\n"
        msg += f"Total Whales: {total}\n"
        msg += f"Solana: {sol}\n"
        msg += f"Base: {base}\n\n"
        msg += f"Tier 1: {t1}\n"
        msg += f"Tier 2: {t2}\n"
        msg += f"Tier 3: {t3}\n"
        msg += f"Tier 4: {t4}\n\n"
        msg += f"Alerts: {alerts}\n"
        msg += f"Tracking: {active} tokens"
        return msg
    except:
        return "Error loading stats"

def cmd_tiers(chat_id, bot_state):
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        t1 = len([w for w in whales if w.get('tier') == 1])
        t2 = len([w for w in whales if w.get('tier') == 2])
        t3 = len([w for w in whales if w.get('tier') == 3])
        t4 = len([w for w in whales if w.get('tier') == 4])
        
        msg = "TIER SYSTEM\n\n"
        msg += f"Tier 1 (30s): {t1} whales\n"
        msg += f"Tier 2 (3m): {t2} whales\n"
        msg += f"Tier 3 (10m): {t3} whales\n"
        msg += f"Tier 4 (24h): {t4} whales"
        return msg
    except:
        return "Error loading tiers"

def cmd_tier_detail(chat_id, bot_state, tier_num):
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        tier_whales = [w for w in whales if w.get('tier') == tier_num]
        
        if not tier_whales:
            return f"No whales in Tier {tier_num}"
        
        sol = len([w for w in tier_whales if w.get('chain') == 'solana'])
        base = len([w for w in tier_whales if w.get('chain') == 'base'])
        
        msg = f"TIER {tier_num}\n\n"
        msg += f"Total: {len(tier_whales)}\n"
        msg += f"Solana: {sol}\n"
        msg += f"Base: {base}"
        return msg
    except:
        return "Error"

def cmd_tracked(chat_id, bot_state):
    tracked = bot_state.get('tracked_tokens', {})
    active = {k: v for k, v in tracked.items() if v.get('status') == 'active'}
    
    if not active:
        return "No tracked tokens"
    
    msg = f"TRACKED ({len(active)})\n\n"
    sorted_tokens = sorted(active.items(), key=lambda x: x[1].get('current_gain', 0), reverse=True)[:10]
    
    for i, (addr, data) in enumerate(sorted_tokens, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        gain = data.get('current_gain', 0)
        msg += f"{i}. {symbol}: {gain:+.1f}%\n"
    
    return msg

def cmd_topwhales(chat_id, bot_state):
    perf = bot_state.get('whale_performance', {})
    
    if not perf:
        return "No performance data yet"
    
    stats = []
    for addr, data in perf.items():
        if data['tokens_tracked'] >= 3:
            rate = (data['successful_calls'] / data['tokens_tracked']) * 100
            stats.append({'addr': addr, 'rate': rate, 'calls': data['tokens_tracked']})
    
    if not stats:
        return "Need more data"
    
    stats.sort(key=lambda x: x['rate'], reverse=True)
    
    msg = "TOP WHALES\n\n"
    for i, s in enumerate(stats[:10], 1):
        short = f"{s['addr'][:6]}...{s['addr'][-4:]}"
        msg += f"{i}. {short}: {s['rate']:.0f}%\n"
    
    return msg

def cmd_performance(chat_id, bot_state):
    return cmd_topwhales(chat_id, bot_state)

def cmd_multibuys(chat_id, bot_state):
    multi = bot_state.get('multi_buys', {})
    
    if not multi:
        return "No multi-buys yet"
    
    msg = "MULTI-BUYS\n\n"
    for addr in list(multi.keys())[:5]:
        msg += f"{addr[:8]}...\n"
    
    return msg

def cmd_lastbuys(chat_id, bot_state):
    buys = bot_state.get('last_buys', [])
    
    if not buys:
        return "No recent buys"
    
    msg = "LAST BUYS\n\n"
    for i, buy in enumerate(reversed(buys[-10:]), 1):
        symbol = buy.get('symbol', 'UNK')
        mc = buy.get('mc', 0)
        msg += f"{i}. {symbol}: ${mc:,.0f}\n"
    
    return msg

def cmd_promotions(chat_id, bot_state):
    promos = bot_state.get('tier_changes', [])
    
    if not promos:
        return "No tier changes yet"
    
    msg = "TIER CHANGES\n\n"
    for change in reversed(promos[-5:]):
        addr = change.get('whale', 'Unknown')
        short = f"{addr[:6]}...{addr[-4:]}"
        old = change.get('old_tier', 0)
        new = change.get('new_tier', 0)
        msg += f"{short}: T{old} -> T{new}\n"
    
    return msg

def cmd_guide(chat_id):
    msg = "WHALE TRACKER GUIDE\n\n"
    msg += "Monitors 1,963 whales\n"
    msg += "4-tier system\n"
    msg += "Auto alerts\n\n"
    msg += "Use /help for commands"
    return msg

def cmd_filters(chat_id):
    filters = bot_state.get('filters', DEFAULT_FILTERS)
    
    msg = "FILTERS\n\n"
    msg += f"MC Min: ${filters['mc_min']:,}\n"
    msg += f"MC Max: ${filters['mc_max']:,}\n"
    msg += f"Liq Min: ${filters['liq_min']:,}"
    return msg

def cmd_pause(chat_id, user_id):
    if not is_admin(user_id):
        return "Admin only"
    
    bot_state['paused'] = True
    save_bot_state()
    return "Bot paused"

def cmd_resume(chat_id, user_id):
    if not is_admin(user_id):
        return "Admin only"
    
    bot_state['paused'] = False
    save_bot_state()
    return "Bot resumed"

def cmd_setfilter(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "Admin only"
    
    parts = command_text.strip().split()
    
    if len(parts) < 3:
        return "Usage: /setfilter [setting] [value]"
    
    setting = parts[1]
    try:
        value = float(parts[2])
    except:
        return "Invalid value"
    
    if 'filters' not in bot_state:
        bot_state['filters'] = DEFAULT_FILTERS.copy()
    
    bot_state['filters'][setting] = value
    save_bot_state()
    
    return f"Updated: {setting} = {value}"

def cmd_addwhale(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "Admin only"
    
    parts = command_text.strip().split()
    
    if len(parts) < 3:
        return "Usage: /addwhale [address] [chain]"
    
    address = parts[1]
    chain = parts[2].lower()
    
    if chain not in ['solana', 'base']:
        return "Chain must be solana or base"
    
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        if any(w['address'] == address for w in whales):
            return "Already tracked"
        
        whale = {
            'address': address,
            'chain': chain,
            'tier': 1,
            'win_count': 0,
            'win_rate': 0,
            'total_calls': 0,
            'source': 'manual',
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        whales.append(whale)
        
        with open('whales_tiered_final.json', 'w') as f:
            json.dump(whales, f, indent=2)
        
        return f"Added to Tier 1!\nTotal: {len(whales)} whales"
    except Exception as e:
        return f"Error: {str(e)}"

def cmd_removewhale(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "Admin only"
    
    parts = command_text.strip().split()
    
    if len(parts) < 2:
        return "Usage: /removewhale [address]"
    
    address = parts[1]
    
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        original = len(whales)
        whales = [w for w in whales if w['address'] != address]
        
        if len(whales) == original:
            return "Not found"
        
        with open('whales_tiered_final.json', 'w') as f:
            json.dump(whales, f, indent=2)
        
        return f"Removed! Now tracking {len(whales)} whales"
    except Exception as e:
        return f"Error: {str(e)}"
