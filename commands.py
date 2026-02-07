"""
All Telegram command handlers
Easy to add new commands by adding functions here
"""

import json
from datetime import datetime
from config import TIER_CONFIG, DEFAULT_FILTERS, is_admin
from state import bot_state, save_bot_state

def handle_command(command_text, user_id):
    """
    Route commands to appropriate handlers
    """
    text = command_text.strip()
    
    # Remove @botname if present
    if '@' in text:
        text = text.split('@')[0]
    
    # Command routing
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
        return "❌ Unknown command. Use /help to see available commands."

def cmd_start(chat_id):
    """Welcome message"""
    msg = "🐋 <b>WHALE TRACKER BOT V4</b>\n\n"
    msg += "Welcome! I monitor elite crypto whales & KOLs across Solana and Base chains.\n"
    msg += "Get instant alerts when they buy tokens!\n\n"
    msg += "🆕 <b>NEW: Multi-Tier Tracking System!</b>\n\n"
    msg += "<b>Quick Commands:</b>\n"
    msg += "/help - All commands\n"
    msg += "/stats - Bot statistics\n"
    msg += "/tracked - Active tokens\n"
    msg += "/tiers - View tier system\n"
    msg += "/guide - Complete guide\n\n"
    msg += "Let's catch some whales! 🚀"
    return msg

def cmd_help(chat_id):
    """Show all commands"""
    msg = "📚 <b>AVAILABLE COMMANDS</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📊 <b>STATISTICS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "/stats - Overall bot statistics\n"
    msg += "/tiers - Performance by tier\n"
    msg += "/tier1 to /tier4 - View specific tier\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📈 <b>TRACKING</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "/tracked - Currently tracked tokens\n"
    msg += "/topwhales - Top 15 performers\n"
    msg += "/performance - Whale leaderboard\n"
    msg += "/multibuys - Multi-whale signals\n"
    msg += "/lastbuys - Recent whale buys\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "ℹ️ <b>INFO</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "/promotions - Recent tier changes\n"
    msg += "/guide - Detailed user guide\n"
    msg += "/help - This message\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🔒 <b>ADMIN COMMANDS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "/pause - Pause bot monitoring\n"
    msg += "/resume - Resume bot monitoring\n"
    msg += "/filters - View current filters\n"
    msg += "/setfilter - Change filters\n"
    msg += "/addwhale - Add whale manually\n"
    msg += "/removewhale - Remove whale\n\n"
    msg += "💡 <b>Tip:</b> Use /tiers to understand the tier system!"
    return msg

def cmd_stats(chat_id, bot_state):
    """Overall bot statistics"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        total_whales = len(whales)
        sol_whales = len([w for w in whales if w.get('chain') == 'solana'])
        base_whales = len([w for w in whales if w.get('chain') == 'base'])

        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for whale in whales:
            tier = whale.get('tier', 3)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        tracked_tokens = bot_state.get('tracked_tokens', {})
        active_tokens = len([t for t in tracked_tokens.values() if t.get('status') == 'active'])
        alerts_sent = bot_state.get('alerts_sent', 0)
        tokens_filtered = bot_state.get('tokens_filtered', 0)

        msg = "📊 <b>BOT STATISTICS</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🐋 <b>WHALES TRACKED</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Total: <b>{total_whales:,}</b>\n"
        msg += f"  • Solana: <b>{sol_whales}</b>\n"
        msg += f"  • Base: <b>{base_whales}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "🎯 <b>BY TIER</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🔥 Tier 1 (Elite): <b>{tier_counts[1]}</b>\n"
        msg += f"⭐ Tier 2 (Active): <b>{tier_counts[2]}</b>\n"
        msg += f"📊 Tier 3 (Semi): <b>{tier_counts[3]}</b>\n"
        msg += f"💤 Tier 4 (Dormant): <b>{tier_counts[4]}</b>\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "📈 <b>ACTIVITY</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"Alerts Sent: <b>{alerts_sent}</b>\n"
        msg += f"Tokens Tracked: <b>{active_tokens}</b>\n"
        msg += f"Filtered: <b>{tokens_filtered}</b>\n\n"
        
        status = "⏸️ PAUSED" if bot_state.get('paused') else "✅ ACTIVE"
        msg += f"🔔 Status: <b>{status}</b>"

        return msg

    except Exception as e:
        return f"❌ Error loading stats: {str(e)}"

def cmd_tiers(chat_id, bot_state):
    """Show tier statistics"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        msg = "🎯 <b>TIER SYSTEM</b>\n\n"

        tier_info = {
            1: {'name': 'Elite', 'interval': '30s', 'emoji': '🔥'},
            2: {'name': 'Active', 'interval': '3m', 'emoji': '⭐'},
            3: {'name': 'Semi-Active', 'interval': '10m', 'emoji': '📊'},
            4: {'name': 'Dormant', 'interval': '24h', 'emoji': '💤'}
        }

        for tier in [1, 2, 3, 4]:
            tier_whales = [w for w in whales if w.get('tier') == tier]
            info = tier_info[tier]

            msg += f"━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"{info['emoji']} <b>TIER {tier} - {info['name'].upper()}</b>\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"Check Interval: <b>{info['interval']}</b>\n"
            msg += f"Whales: <b>{len(tier_whales)}</b>\n"

            sol = len([w for w in tier_whales if w.get('chain') == 'solana'])
            base = len([w for w in tier_whales if w.get('chain') == 'base'])
            msg += f"  • Solana: {sol}\n"
            msg += f"  • Base: {base}\n\n"

        msg += "💡 Use /tier1 through /tier4 for detailed lists!"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_tier_detail(chat_id, bot_state, tier_num):
    """Show detailed view of specific tier"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        tier_whales = [w for w in whales if w.get('tier') == tier_num]

        if not tier_whales:
            return f"No whales in Tier {tier_num}"

        tier_names = {
            1: '🔥 TIER 1 - ELITE (30s)',
            2: '⭐ TIER 2 - ACTIVE (3m)',
            3: '📊 TIER 3 - SEMI-ACTIVE (10m)',
            4: '💤 TIER 4 - DORMANT (24h)'
        }

        # Sort by win rate
        sorted_whales = sorted(
            tier_whales, 
            key=lambda x: x.get('win_rate', 0), 
            reverse=True
        )

        msg = f"<b>{tier_names[tier_num]}</b>\n\n"
        msg += f"Total Whales: <b>{len(tier_whales)}</b>\n\n"

        sol = [w for w in tier_whales if w.get('chain') == 'solana']
        base = [w for w in tier_whales if w.get('chain') == 'base']

        msg += f"🟣 Solana: <b>{len(sol)}</b>\n"
        msg += f"🔵 Base: <b>{len(base)}</b>\n\n"

        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += "<b>TOP 10 PERFORMERS</b>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"

        for i, whale in enumerate(sorted_whales[:10], 1):
            addr = whale.get('address', 'Unknown')
            chain_emoji = '🟣' if whale.get('chain') == 'solana' else '🔵'
            winrate = whale.get('win_rate', 0)
            win_count = whale.get('win_count', 0)

            short_addr = f"{addr[:8]}...{addr[-4:]}"
            msg += f"{i}. {chain_emoji} <code>{short_addr}</code>\n"
            
            if winrate > 0:
                msg += f"   WR: <b>{winrate:.0f}%</b> | Wins: {win_count}\n"
            
            msg += "\n"

        if len(tier_whales) > 10:
            msg += f"... and <b>{len(tier_whales) - 10}</b> more whales\n"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_tracked(chat_id, bot_state):
    """Currently tracked tokens"""
    tracked = bot_state.get('tracked_tokens', {})
    active = {k: v for k, v in tracked.items() if v.get('status') == 'active'}

    if not active:
        return "📭 No tokens currently being tracked."

    sorted_tokens = sorted(
        active.items(), 
        key=lambda x: x[1].get('current_gain', 0), 
        reverse=True
    )[:20]

    msg = f"📊 <b>TRACKED TOKENS ({len(active)})</b>\n\n"

    for i, (addr, data) in enumerate(sorted_tokens, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        gain = data.get('current_gain', 0)
        max_gain = data.get('max_gain', 0)
        whale_count = len(data.get('whales_bought', []))

        gain_emoji = "🟢" if gain > 0 else "🔴" if gain < -10 else "⚪"
        multi_emoji = "🔥" if whale_count >= 3 else "⭐" if whale_count >= 2 else ""

        msg += f"{i}. {gain_emoji} <b>{symbol}</b> {multi_emoji}\n"
        msg += f"   Gain: <b>{gain:+.1f}%</b> | ATH: <b>{max_gain:.1f}%</b>\n"
        msg += f"   Whales: <b>{whale_count}</b>\n\n"

    return msg

def cmd_topwhales(chat_id, bot_state):
    """Top 15 performing whales"""
    try:
        perf = bot_state.get('whale_performance', {})

        if not perf:
            return "📭 No performance data yet. Wait for some whale activity!"

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

        msg = "🏆 <b>TOP 15 PERFORMING WHALES</b>\n\n"

        for i, stats in enumerate(whale_stats[:15], 1):
            addr = stats['address']
            short_addr = f"{addr[:8]}...{addr[-4:]}"
            
            msg += f"{i}. <code>{short_addr}</code>\n"
            msg += f"   Success: <b>{stats['success_rate']:.0f}%</b> | "
            msg += f"Avg: <b>{stats['avg_gain']:+.1f}%</b>\n"
            msg += f"   Best: <b>{stats['best_call']:.0f}%</b> | "
            msg += f"Calls: {stats['tokens_tracked']}\n\n"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_performance(chat_id, bot_state):
    """Alias for topwhales"""
    return cmd_topwhales(chat_id, bot_state)

def cmd_multibuys(chat_id, bot_state):
    """Show tokens with multiple whale buyers"""
    multi_buys = bot_state.get('multi_buys', {})
    tracked = bot_state.get('tracked_tokens', {})

    if not multi_buys:
        return "📭 No multi-buy events detected yet."

    msg = "🔥 <b>MULTI-BUY ALERTS</b>\n\n"

    for token_addr, multi_data in list(multi_buys.items())[:15]:
        if token_addr in tracked:
            data = tracked[token_addr]
            whale_count = len(data.get('whales_bought', []))
            gain = data.get('current_gain', 0)
            symbol = data.get('symbol', 'UNKNOWN')

            msg += f"🔥 <b>{symbol}</b>\n"
            msg += f"   Whales: <b>{whale_count}</b> | Gain: <b>{gain:+.1f}%</b>\n"
            msg += f"   <code>{token_addr[:16]}...</code>\n\n"

    return msg

def cmd_lastbuys(chat_id, bot_state):
    """Show last 15 whale buys"""
    last_buys = bot_state.get('last_buys', [])

    if not last_buys:
        return "📭 No recent buys detected yet."

    msg = "🔥 <b>LAST 15 QUALITY BUYS</b>\n\n"

    for i, buy in enumerate(reversed(last_buys[-15:]), 1):
        symbol = buy.get('symbol', 'UNKNOWN')
        mc = buy.get('mc', 0)
        timestamp = buy.get('timestamp', 'Unknown')

        msg += f"{i}. 💎 <b>{symbol}</b> | MC: ${mc:,.0f}\n"
        msg += f"   {timestamp}\n\n"

    return msg

def cmd_promotions(chat_id, bot_state):
    """Show recent tier changes"""
    promotions = bot_state.get('tier_changes', [])

    if not promotions:
        return "📭 No tier changes yet."

    recent = promotions[-10:]
    msg = "🎯 <b>RECENT TIER CHANGES</b>\n\n"

    for change in reversed(recent):
        whale_addr = change.get('whale', 'Unknown')
        old_tier = change.get('old_tier', 0)
        new_tier = change.get('new_tier', 0)
        reason = change.get('reason', 'N/A')
        timestamp = change.get('timestamp', 'Unknown')

        direction = "⬆️ PROMOTED" if new_tier < old_tier else "⬇️ DEMOTED"
        short_addr = f"{whale_addr[:8]}...{whale_addr[-4:]}"

        msg += f"{direction}\n"
        msg += f"<code>{short_addr}</code>\n"
        msg += f"Tier {old_tier} → Tier {new_tier}\n"
        msg += f"{reason}\n"
        msg += f"{timestamp}\n\n"

    return msg

def cmd_guide(chat_id):
    """User guide"""
    msg = "📚 <b>WHALE TRACKER BOT - GUIDE</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🎯 <b>WHAT THIS BOT DOES</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "Monitors 1,963 elite whale wallets across Solana and Base chains.\n"
    msg += "Get instant alerts when they buy quality tokens!\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🔥 <b>4-TIER SYSTEM</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🔥 Tier 1 (Elite) - 30s checks\n"
    msg += "⭐ Tier 2 (Active) - 3m checks\n"
    msg += "📊 Tier 3 (Semi) - 10m checks\n"
    msg += "💤 Tier 4 (Dormant) - 24h checks\n\n"
    msg += "Whales auto-promote/demote based on performance!\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📊 <b>KEY COMMANDS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "/stats - Bot statistics\n"
    msg += "/tiers - View tier system\n"
    msg += "/tracked - Active tokens\n"
    msg += "/topwhales - Leaderboard\n"
    msg += "/multibuys - High conviction signals\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🚨 <b>ALERT TYPES</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "1. Whale Buy - Single whale buys\n"
    msg += "2. Multi-Buy - 2+ whales buy same token\n"
    msg += "3. Price Milestones - +10%, +25%, +50%, +100%\n"
    msg += "4. Tier Promotions - Whale performance updates\n\n"
    msg += "⚠️ <b>Always DYOR! Not financial advice.</b>"
    return msg

def cmd_filters(chat_id):
    """Show current filters"""
    filters = bot_state.get('filters', DEFAULT_FILTERS)
    
    msg = "⚙️ <b>CURRENT FILTERS</b>\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💰 <b>Market Cap</b>\n"
    msg += f"  Min: ${filters['mc_min']:,}\n"
    msg += f"  Max: ${filters['mc_max']:,}\n\n"
    msg += "💧 <b>Liquidity</b>\n"
    msg += f"  Min: ${filters['liq_min']:,}\n\n"
    msg += "📊 <b>Ratios</b>\n"
    msg += f"  Max Vol/Liq: {filters['vol_liq_max']}x\n"
    msg += f"  Max Buy/Sell: {filters['buy_sell_max']}:1\n\n"
    msg += "⏰ <b>Token Age</b>\n"
    msg += f"  Min: {filters['min_age_hours']}h\n\n"
    msg += "🔒 <b>Admin:</b> Use /setfilter to change"
    
    return msg

def cmd_pause(chat_id, user_id):
    """Pause bot (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>\n\nAdmin only command."
    
    bot_state['paused'] = True
    save_bot_state()
    return "⏸️ <b>BOT PAUSED</b>\n\nMonitoring stopped. Use /resume to continue."

def cmd_resume(chat_id, user_id):
    """Resume bot (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>\n\nAdmin only command."
    
    bot_state['paused'] = False
    save_bot_state()
    return "▶️ <b>BOT RESUMED</b>\n\nMonitoring active!"

def cmd_setfilter(chat_id, user_id, command_text):
    """Set filter (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>\n\nAdmin only command."
    
    parts = command_text.strip().split()
    
    if len(parts) < 3:
        return "❌ <b>Usage:</b> /setfilter [setting] [value]\n\n<b>Settings:</b>\nmc_min, mc_max, liq_min, vol_liq_max, buy_sell_max, min_age_hours"
    
    setting = parts[1]
    try:
        value = float(parts[2])
    except:
        return "❌ Invalid value. Must be a number."
    
    valid_settings = ['mc_min', 'mc_max', 'liq_min', 'vol_liq_max', 'buy_sell_max', 'min_age_hours']
    
    if setting not in valid_settings:
        return f"❌ Invalid setting.\n\n<b>Valid settings:</b>\n{', '.join(valid_settings)}"
    
    if 'filters' not in bot_state:
        bot_state['filters'] = DEFAULT_FILTERS.copy()
    
    bot_state['filters'][setting] = value
    save_bot_state()
    
    return f"✅ <b>Filter updated!</b>\n\n{setting} = {value:,.0f}"

def cmd_addwhale(chat_id, user_id, command_text):
    """Add whale (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>\n\nAdmin only command."
    
    parts = command_text.strip().split()
    
    if len(parts) < 3:
        return "❌ <b>Usage:</b> /addwhale [address] [chain]\n\n<b>Chain:</b> solana or base"
    
    address = parts[1]
    chain = parts[2].lower()
    
    if chain not in ['solana', 'base']:
        return "❌ Chain must be 'solana' or 'base'"
    
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        if any(w['address'] == address for w in whales):
            return "❌ Whale already tracked!"
        
        new_whale = {
            'address': address,
            'chain': chain,
            'tier': 3,
            'win_count': 0,
            'win_rate': 0,
            'total_calls': 0,
            'source': 'manual_add',
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        whales.append(new_whale)
        
        with open('whales_tiered_final.json', 'w') as f:
            json.dump(whales, f, indent=2)
        
        return f"✅ <b>Whale added!</b>\n\nNow tracking {len(whales)} whales.\n\n📍 {address[:16]}...\n⛓️ {chain.upper()}\n🎯 Tier 3"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_removewhale(chat_id, user_id, command_text):
    """Remove whale (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>\n\nAdmin only command."
    
    parts = command_text.strip().split()
    
    if len(parts) < 2:
        return "❌ <b>Usage:</b> /removewhale [address]"
    
    address = parts[1]
    
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)
        
        original_count = len(whales)
        whales = [w for w in whales if w['address'] != address]
        
        if len(whales) == original_count:
            return "❌ Whale not found!"
        
        with open('whales_tiered_final.json', 'w') as f:
            json.dump(whales, f, indent=2)
        
        return f"✅ <b>Whale removed!</b>\n\nNow tracking {len(whales)} whales."
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
