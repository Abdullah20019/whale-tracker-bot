"""
All Telegram command handlers - UPGRADED WITH EMOJIS
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
        return "❌ Unknown command. Use /help"

def cmd_start(chat_id):
    msg = "🐋 <b>WHALE TRACKER BOT V4</b>\n\n"
    msg += "Welcome! I monitor elite crypto whales across Solana & Base chains.\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📊 <b>Quick Commands:</b>\n"
    msg += "/help ❓ - All commands\n"
    msg += "/stats 📈 - Live statistics\n"
    msg += "/tiers 🏆 - Tier information\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "🔔 Auto-alerts enabled for whale activity!"
    return msg

def cmd_help(chat_id):
    msg = "🐋 <b>WHALE TRACKER BOT V4</b>\n\n"
    msg += "╔══════════════════════════════════╗\n"
    msg += "      📊 <b>STATISTICS</b>\n"
    msg += "╚══════════════════════════════════╝\n"
    msg += "/stats 📈 - Bot statistics\n"
    msg += "/tiers 🏆 - Tier information\n\n"
    msg += "╔══════════════════════════════════╗\n"
    msg += "      🔍 <b>TRACKING</b>\n"
    msg += "╚══════════════════════════════════╝\n"
    msg += "/tracked 💎 - Active tokens\n"
    msg += "/topwhales 🐋 - Top performers\n"
    msg += "/lastbuys 🔥 - Recent buys\n"
    msg += "/multibuys 🎯 - Multi-whale buys\n"
    msg += "/performance 👑 - Whale leaderboard\n"
    msg += "/promotions ⬆️ - Tier changes\n\n"
    msg += "╔══════════════════════════════════╗\n"
    msg += "      ⚙️ <b>ADMIN CONTROLS</b>\n"
    msg += "╚══════════════════════════════════╝\n"
    msg += "/pause ⏸️ - Pause monitoring\n"
    msg += "/resume ▶️ - Resume monitoring\n"
    msg += "/addwhale ➕ - Add whale manually\n"
    msg += "/removewhale ❌ - Remove whale\n"
    msg += "/filters 🎛️ - View filter settings\n"
    msg += "/setfilter 🔧 - Change filters\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "<b>🚀 FEATURES:</b>\n"
    msg += "✅ Multi-buy detection\n"
    msg += "✅ Whale exit alerts\n"
    msg += "✅ Performance tracking\n"
    msg += "✅ Real-time price updates\n"
    msg += "✅ 4-tier monitoring system\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
        filtered = bot_state.get('tokens_filtered', 0)

        msg = "📊 <b>BOT STATISTICS</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🐋 <b>WHALES TRACKED</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Total: <b>{total}</b>\n"
        msg += f"  🟣 Solana: <b>{sol}</b>\n"
        msg += f"  🔵 Base: <b>{base}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🏆 <b>TIER BREAKDOWN</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Tier 1 (30s): <b>{t1}</b>\n"
        msg += f"Tier 2 (3m): <b>{t2}</b>\n"
        msg += f"Tier 3 (10m): <b>{t3}</b>\n"
        msg += f"Tier 4 (24h): <b>{t4}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "📈 <b>ACTIVITY</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🚨 Alerts Sent: <b>{alerts}</b>\n"
        msg += f"💎 Tracking: <b>{active}</b> tokens\n"
        msg += f"⏭️ Filtered: <b>{filtered}</b>\n\n"
        msg += f"🔔 Status: <b>{'⏸️ PAUSED' if bot_state.get('paused') else '✅ ACTIVE'}</b>"
        return msg
    except Exception as e:
        return f"❌ Error loading stats: {str(e)}"

def cmd_tiers(chat_id, bot_state):
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        t1 = len([w for w in whales if w.get('tier') == 1])
        t2 = len([w for w in whales if w.get('tier') == 2])
        t3 = len([w for w in whales if w.get('tier') == 3])
        t4 = len([w for w in whales if w.get('tier') == 4])

        msg = "🏆 <b>TIER SYSTEM</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🔥 <b>TIER 1 (ELITE)</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"⚡ Check Interval: <b>30 seconds</b>\n"
        msg += f"🎯 Priority: <b>HIGHEST</b>\n"
        msg += f"🐋 Whales: <b>{t1}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "⭐ <b>TIER 2 (HIGH)</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"⚡ Check Interval: <b>3 minutes</b>\n"
        msg += f"🎯 Priority: <b>HIGH</b>\n"
        msg += f"🐋 Whales: <b>{t2}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "💫 <b>TIER 3 (MEDIUM)</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"⚡ Check Interval: <b>10 minutes</b>\n"
        msg += f"🎯 Priority: <b>MEDIUM</b>\n"
        msg += f"🐋 Whales: <b>{t3}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "⚪ <b>TIER 4 (STANDARD)</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"⚡ Check Interval: <b>24 hours</b>\n"
        msg += f"🎯 Priority: <b>STANDARD</b>\n"
        msg += f"🐋 Whales: <b>{t4}</b>\n\n"
        msg += "💡 <b>TIP:</b> Use /tier1, /tier2, etc. for details"
        return msg
    except Exception as e:
        return f"❌ Error loading tiers: {str(e)}"

def cmd_tier_detail(chat_id, bot_state, tier_num):
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        tier_whales = [w for w in whales if w.get('tier') == tier_num]

        if not tier_whales:
            return f"📭 No whales in Tier {tier_num}"

        sol = len([w for w in tier_whales if w.get('chain') == 'solana'])
        base = len([w for w in tier_whales if w.get('chain') == 'base'])

        tier_icons = {1: "🔥", 2: "⭐", 3: "💫", 4: "⚪"}
        icon = tier_icons.get(tier_num, "🔹")

        msg = f"{icon} <b>TIER {tier_num} DETAILS</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Total Whales: <b>{len(tier_whales)}</b>\n"
        msg += f"🟣 Solana: <b>{sol}</b>\n"
        msg += f"🔵 Base: <b>{base}</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━"
        return msg
    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_tracked(chat_id, bot_state):
    tracked = bot_state.get('tracked_tokens', {})
    active = {k: v for k, v in tracked.items() if v.get('status') == 'active'}

    if not active:
        return "📭 No tokens being tracked yet"

    msg = f"💎 <b>TRACKED TOKENS ({len(active)})</b>\n\n"
    sorted_tokens = sorted(active.items(), key=lambda x: x[1].get('current_gain', 0), reverse=True)[:15]

    for i, (addr, data) in enumerate(sorted_tokens, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        gain = data.get('current_gain', 0)
        max_gain = data.get('max_gain', 0)
        whale_count = len(data.get('whales_bought', []))
        
        gain_icon = "🟢" if gain > 0 else "🔴" if gain < -10 else "⚪"
        multi_icon = "🔥" if whale_count >= 3 else "⭐" if whale_count >= 2 else ""
        
        msg += f"{i}. {gain_icon} <b>{symbol}</b> {multi_icon}\n"
        msg += f"   Gain: <b>{gain:+.1f}%</b> | ATH: <b>{max_gain:.1f}%</b>\n"
        msg += f"   Whales: <b>{whale_count}</b>\n\n"

    return msg

def cmd_topwhales(chat_id, bot_state):
    perf = bot_state.get('whale_performance', {})

    if not perf:
        return "📭 No performance data yet"

    stats = []
    for addr, data in perf.items():
        if data['tokens_tracked'] >= 3:
            rate = (data['successful_calls'] / data['tokens_tracked']) * 100
            avg_gain = data['total_gain'] / data['tokens_tracked']
            stats.append({
                'addr': addr,
                'rate': rate,
                'avg': avg_gain,
                'best': data['best_call'],
                'calls': data['tokens_tracked']
            })

    if not stats:
        return "📊 Need more data (min 3 calls per whale)"

    stats.sort(key=lambda x: x['rate'], reverse=True)

    msg = "🐋 <b>TOP PERFORMING WHALES</b>\n\n"
    for i, s in enumerate(stats[:10], 1):
        short = f"{s['addr'][:6]}...{s['addr'][-4:]}"
        msg += f"{i}. <code>{short}</code>\n"
        msg += f"   Success: <b>{s['rate']:.0f}%</b> | Avg: <b>{s['avg']:+.1f}%</b>\n"
        msg += f"   Best: <b>{s['best']:.0f}%</b> | Calls: {s['calls']}\n\n"

    return msg

def cmd_performance(chat_id, bot_state):
    return cmd_topwhales(chat_id, bot_state)

def cmd_multibuys(chat_id, bot_state):
    multi = bot_state.get('multi_buys', {})
    tracked = bot_state.get('tracked_tokens', {})

    if not multi:
        return "📭 No multi-buy events detected yet"

    msg = "🎯 <b>MULTI-BUY ALERTS</b>\n\n"
    
    for token_addr in list(multi.keys())[:10]:
        if token_addr in tracked:
            data = tracked[token_addr]
            symbol = data.get('symbol', 'UNKNOWN')
            whale_count = len(data.get('whales_bought', []))
            gain = data.get('current_gain', 0)
            
            msg += f"🔥 <b>{symbol}</b>\n"
            msg += f"   Whales: <b>{whale_count}</b> | Gain: <b>{gain:+.1f}%</b>\n"
            msg += f"   <code>{token_addr[:16]}...</code>\n\n"

    return msg

def cmd_lastbuys(chat_id, bot_state):
    buys = bot_state.get('last_buys', [])

    if not buys:
        return "📭 No recent buys detected yet"

    msg = "🔥 <b>LAST 15 QUALITY BUYS</b>\n\n"
    for i, buy in enumerate(reversed(buys[-15:]), 1):
        symbol = buy.get('symbol', 'UNK')
        mc = buy.get('mc', 0)
        timestamp = buy.get('timestamp', '')
        msg += f"{i}. 💎 <b>{symbol}</b> | MC: ${mc:,.0f}\n"
        msg += f"   {timestamp}\n\n"

    return msg

def cmd_promotions(chat_id, bot_state):
    promos = bot_state.get('tier_changes', [])

    if not promos:
        return "📭 No tier changes yet"

    msg = "⬆️ <b>RECENT TIER CHANGES</b>\n\n"
    for change in reversed(promos[-10:]):
        addr = change.get('whale', 'Unknown')
        short = f"{addr[:6]}...{addr[-4:]}"
        old = change.get('old_tier', 0)
        new = change.get('new_tier', 0)
        reason = change.get('reason', '')
        
        if new < old:
            arrow = "⬆️"
            color = "🟢"
        else:
            arrow = "⬇️"
            color = "🔴"
        
        msg += f"{color} <code>{short}</code>\n"
        msg += f"   {arrow} Tier {old} → Tier {new}\n"
        msg += f"   {reason}\n\n"

    return msg

def cmd_guide(chat_id):
    msg = "📖 <b>WHALE TRACKER GUIDE</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🎯 <b>WHAT IT DOES:</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "Monitors 1,963 elite whale wallets\n"
    msg += "Tracks buys across Solana & Base\n"
    msg += "Sends instant alerts when whales buy\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🏆 <b>4-TIER SYSTEM:</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "Tier 1: 30s checks (Elite)\n"
    msg += "Tier 2: 3m checks (High)\n"
    msg += "Tier 3: 10m checks (Medium)\n"
    msg += "Tier 4: 24h checks (Standard)\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "✨ <b>FEATURES:</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "✅ Multi-buy detection\n"
    msg += "✅ Exit alerts\n"
    msg += "✅ Performance tracking\n"
    msg += "✅ Auto tier promotions\n\n"
    msg += "Use /help for all commands"
    return msg

def cmd_filters(chat_id):
    filters = bot_state.get('filters', DEFAULT_FILTERS)

    msg = "🎛️ <b>CURRENT FILTER SETTINGS</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💰 <b>Market Cap:</b>\n"
    msg += f"   Min: <b>${filters['mc_min']:,}</b>\n"
    msg += f"   Max: <b>${filters['mc_max']:,}</b>\n\n"
    msg += "💧 <b>Liquidity:</b>\n"
    msg += f"   Min: <b>${filters['liq_min']:,}</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "<b>🔒 Admin Only:</b> Use /setfilter to change"
    return msg

def cmd_pause(chat_id, user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b> - Admin only"

    bot_state['paused'] = True
    save_bot_state()
    return "⏸️ <b>BOT PAUSED</b>\n\nMonitoring stopped. Use /resume to restart."

def cmd_resume(chat_id, user_id):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b> - Admin only"

    bot_state['paused'] = False
    save_bot_state()
    return "▶️ <b>BOT RESUMED</b>\n\nMonitoring active!"

def cmd_setfilter(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b> - Admin only"

    parts = command_text.strip().split()

    if len(parts) < 3:
        return "❌ Usage: /setfilter [setting] [value]\n\nExample: /setfilter mc_min 50000"

    setting = parts[1]
    try:
        value = float(parts[2])
    except:
        return "❌ Invalid value - must be a number"

    if 'filters' not in bot_state:
        bot_state['filters'] = DEFAULT_FILTERS.copy()

    bot_state['filters'][setting] = value
    save_bot_state()

    return f"✅ <b>Filter Updated!</b>\n\n{setting} = ${value:,.0f}"

def cmd_addwhale(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b> - Admin only"

    parts = command_text.strip().split()

    if len(parts) < 3:
        return "❌ Usage: /addwhale [address] [chain]\n\nExample: /addwhale ABC123... solana"

    address = parts[1]
    chain = parts[2].lower()

    if chain not in ['solana', 'base']:
        return "❌ Chain must be 'solana' or 'base'"

    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        if any(w['address'] == address for w in whales):
            return "❌ Wallet already tracked"

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

        chain_icon = "🟣" if chain == "solana" else "🔵"
        
        msg = "✅ <b>Whale Added Successfully!</b>\n\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"{chain_icon} <code>{address[:16]}...</code>\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Chain: <b>{chain.upper()}</b>\n"
        msg += f"Tier: <b>1 (Elite)</b>\n"
        msg += f"Check Interval: <b>30 seconds</b>\n\n"
        msg += f"🐋 Now tracking <b>{len(whales)}</b> whales"
        
        return msg
    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_removewhale(chat_id, user_id, command_text):
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b> - Admin only"

    parts = command_text.strip().split()

    if len(parts) < 2:
        return "❌ Usage: /removewhale [address]\n\nExample: /removewhale ABC123..."

    address = parts[1]

    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        original = len(whales)
        whales = [w for w in whales if w['address'] != address]

        if len(whales) == original:
            return "❌ Wallet not found in tracking list"

        with open('whales_tiered_final.json', 'w') as f:
            json.dump(whales, f, indent=2)

        msg = "✅ <b>Whale Removed!</b>\n\n"
        msg += f"<code>{address[:16]}...</code>\n\n"
        msg += f"🐋 Now tracking <b>{len(whales)}</b> whales"
        
        return msg
    except Exception as e:
        return f"❌ Error: {str(e)}"
