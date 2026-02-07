"""
All Telegram command handlers
Easy to add new commands by adding functions here
"""

import json
from datetime import datetime
from config import TIER_CONFIG

def handle_command(update, context, bot_state):
    """
    Route commands to appropriate handlers
    """
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    # Command routing
    if text == '/start':
        return cmd_start(chat_id)
    elif text == '/help':
        return cmd_help(chat_id)
    elif text == '/stats':
        return cmd_stats(chat_id, bot_state)
    elif text == '/tracked':
        return cmd_tracked(chat_id, bot_state)
    elif text == '/topwhales':
        return cmd_topwhales(chat_id, bot_state)
    elif text == '/performance':
        return cmd_performance(chat_id, bot_state)
    elif text == '/tiers':
        return cmd_tiers(chat_id, bot_state)
    elif text == '/tier1':
        return cmd_tier_detail(chat_id, bot_state, 1)
    elif text == '/tier2':
        return cmd_tier_detail(chat_id, bot_state, 2)
    elif text == '/tier3':
        return cmd_tier_detail(chat_id, bot_state, 3)
    elif text == '/tier4':
        return cmd_tier_detail(chat_id, bot_state, 4)
    elif text == '/multibuys':
        return cmd_multibuys(chat_id, bot_state)
    elif text == '/promotions':
        return cmd_promotions(chat_id, bot_state)
    elif text == '/guide':
        return cmd_guide(chat_id)
    elif text == '/kols':
        return cmd_kols(chat_id, bot_state)
    else:
        return "Unknown command. Use /help to see available commands."

def cmd_start(chat_id):
    """Welcome message"""
    msg = "Welcome to Whale Tracker Bot V4!\n\n"
    msg += "I monitor elite crypto whales & KOLs across Solana and Base chains.\n"
    msg += "Get instant alerts when they buy tokens!\n\n"
    msg += "NEW: Now tracking crypto KOL wallets!\n\n"
    msg += "Quick Commands:\n"
    msg += "/help - All commands\n"
    msg += "/stats - Bot statistics\n"
    msg += "/kols - View tracked KOLs\n"
    msg += "/tracked - Active tokens\n"
    msg += "/guide - Complete guide\n\n"
    msg += "Let's catch some whales!"
    return msg

def cmd_help(chat_id):
    """Show all commands"""
    msg = "AVAILABLE COMMANDS\n\n"
    msg += "STATISTICS:\n"
    msg += "/stats - Overall bot statistics\n"
    msg += "/kols - View all tracked KOLs\n"
    msg += "/tiers - Performance by tier\n"
    msg += "/tier1 to /tier4 - View specific tier\n\n"
    msg += "TRACKING:\n"
    msg += "/tracked - Currently tracked tokens\n"
    msg += "/topwhales - Top 15 performers\n"
    msg += "/performance - Whale leaderboard\n"
    msg += "/multibuys - Multi-whale signals\n\n"
    msg += "INFO:\n"
    msg += "/promotions - Recent tier changes\n"
    msg += "/guide - Detailed user guide\n"
    msg += "/help - This message\n\n"
    msg += "Tip: Use /kols to see all crypto KOLs we're tracking!"
    return msg

def cmd_stats(chat_id, bot_state):
    """Overall bot statistics with KOL breakdown"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        total_whales = len(whales)
        kols = [w for w in whales if w.get('type') == 'kol']
        regular_whales = [w for w in whales if w.get('type') != 'kol']

        sol_whales = len([w for w in whales if w.get('chain') == 'sol'])
        base_whales = len([w for w in whales if w.get('chain') == 'base'])
        sol_kols = len([k for k in kols if k.get('chain') == 'sol'])
        base_kols = len([k for k in kols if k.get('chain') == 'base'])

        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for whale in whales:
            tier = whale.get('tier', 3)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        tracked_tokens = bot_state.get('tracked_tokens', {})
        active_tokens = len([t for t in tracked_tokens.values() if t.get('active', True)])

        msg = "BOT STATISTICS\n\n"
        msg += f"Total Wallets Monitored: {total_whales:,}\n"
        msg += f"KOLs: {len(kols)}\n"
        msg += f"Regular Whales: {len(regular_whales)}\n\n"
        msg += "By Chain:\n"
        msg += f"  Solana: {sol_whales} ({sol_kols} KOLs)\n"
        msg += f"  Base: {base_whales} ({base_kols} KOLs)\n\n"
        msg += "By Tier:\n"
        msg += f"  Tier 1 (Elite): {tier_counts[1]} whales\n"
        msg += f"  Tier 2 (Active): {tier_counts[2]} whales\n"
        msg += f"  Tier 3 (Semi): {tier_counts[3]} whales\n"
        msg += f"  Tier 4 (Dormant): {tier_counts[4]} whales\n\n"
        msg += f"Currently Tracking: {active_tokens} tokens\n\n"
        msg += "Use /kols to see all KOLs!"

        return msg

    except Exception as e:
        return f"Error loading stats: {str(e)}"

def cmd_kols(chat_id, bot_state):
    """Display all tracked KOLs"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        kols = [w for w in whales if w.get('type') == 'kol']

        if not kols:
            return "No KOLs found in tracker. Run kol_scraper.py to add KOLs!"

        kols.sort(key=lambda x: (x.get('tier', 4), x.get('chain', 'zzz')))

        tier_groups = {1: [], 2: [], 3: [], 4: []}
        for kol in kols:
            tier = kol.get('tier', 3)
            tier_groups[tier].append(kol)

        msg = "CRYPTO KOL TRACKER\n\n"
        msg += f"Total KOLs: {len(kols)}\n\n"

        tier_names = {
            1: 'TIER 1 - ELITE (30s checks)',
            2: 'TIER 2 - ACTIVE (3m checks)',
            3: 'TIER 3 - SEMI-ACTIVE (10m checks)',
            4: 'TIER 4 - DORMANT (24h checks)'
        }

        for tier in [1, 2, 3, 4]:
            tier_kols = tier_groups[tier]
            if not tier_kols:
                continue

            msg += f"{tier_names[tier]}\n"
            msg += "--------------------\n"

            for i, kol in enumerate(tier_kols[:10], 1):
                name = kol.get('name', 'Unknown')
                twitter = kol.get('twitter', 'N/A')
                chain = kol.get('chain', '?').upper()
                winrate = kol.get('win_rate', 0)

                if len(name) > 20:
                    name = name[:17] + "..."

                msg += f"{i}. {name}\n"
                msg += f"   {twitter} | {chain}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "\n"

                if i >= 10:
                    remaining = len(tier_kols) - 10
                    if remaining > 0:
                        msg += f"   ... and {remaining} more\n"
                    break

            msg += "\n"

        msg += "Use /tier1 through /tier4 for full lists!"

        return msg

    except Exception as e:
        return f"Error loading KOLs: {str(e)}"

def cmd_tier_detail(chat_id, bot_state, tier_num):
    """Show detailed view of specific tier"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        tier_whales = [w for w in whales if w.get('tier') == tier_num]

        if not tier_whales:
            return f"No whales in Tier {tier_num}"

        kols = [w for w in tier_whales if w.get('type') == 'kol']
        regular = [w for w in tier_whales if w.get('type') != 'kol']

        tier_names = {
            1: 'TIER 1 - ELITE WHALES (30s checks)',
            2: 'TIER 2 - ACTIVE WHALES (3m checks)',
            3: 'TIER 3 - SEMI-ACTIVE WHALES (10m checks)',
            4: 'TIER 4 - DORMANT WHALES (24h checks)'
        }

        msg = f"{tier_names[tier_num]}\n\n"
        msg += f"Total: {len(tier_whales)} wallets\n"
        msg += f"KOLs: {len(kols)}\n"
        msg += f"Regular Whales: {len(regular)}\n\n"

        if kols:
            msg += "KOLS:\n"
            msg += "--------------------\n"

            for i, kol in enumerate(kols[:15], 1):
                name = kol.get('name', 'Unknown')
                twitter = kol.get('twitter', 'N/A')
                chain = kol.get('chain', '?').upper()
                winrate = kol.get('win_rate', 0)

                if len(name) > 15:
                    name = name[:12] + "..."

                msg += f"{i}. {name} | {chain}\n"
                msg += f"   {twitter}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "\n"

            if len(kols) > 15:
                msg += f"\n... and {len(kols) - 15} more KOLs\n"

            msg += "\n"

        if regular:
            msg += "REGULAR WHALES:\n"
            msg += "--------------------\n"

            for i, whale in enumerate(regular[:10], 1):
                addr = whale.get('address', 'Unknown')
                chain = whale.get('chain', '?').upper()
                winrate = whale.get('win_rate', 0)

                short_addr = f"{addr[:6]}...{addr[-4:]}"
                msg += f"{i}. {short_addr} | {chain}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "\n"

            if len(regular) > 10:
                msg += f"\n... and {len(regular) - 10} more whales\n"

        return msg

    except Exception as e:
        return f"Error: {str(e)}"

def cmd_tiers(chat_id, bot_state):
    """Show tier statistics"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        msg = "TIER STATISTICS\n\n"

        tier_names = {1: 'Elite', 2: 'Active', 3: 'Semi-Active', 4: 'Dormant'}
        check_intervals = {1: '30s', 2: '3m', 3: '10m', 4: '24h'}

        for tier in [1, 2, 3, 4]:
            tier_whales = [w for w in whales if w.get('tier') == tier]
            tier_kols = [w for w in tier_whales if w.get('type') == 'kol']

            msg += f"TIER {tier} - {tier_names[tier]}\n"
            msg += f"Check Interval: {check_intervals[tier]}\n"
            msg += f"Total: {len(tier_whales)} wallets\n"
            msg += f"  KOLs: {len(tier_kols)}\n"
            msg += f"  Whales: {len(tier_whales) - len(tier_kols)}\n"

            total_calls = sum(w.get('total_calls', 0) for w in tier_whales)
            if total_calls > 0:
                wins = sum(w.get('win_count', 0) for w in tier_whales)
                winrate = (wins / total_calls * 100) if total_calls > 0 else 0
                msg += f"Performance: {winrate:.1f}% WR | {total_calls} calls\n"

            msg += "\n"

        msg += "Use /tier1 to /tier4 for detailed lists!"

        return msg

    except Exception as e:
        return f"Error: {str(e)}"

def cmd_tracked(chat_id, bot_state):
    """Currently tracked tokens"""
    tracked = bot_state.get('tracked_tokens', {})
    active = {k: v for k, v in tracked.items() if v.get('active', True)}

    if not active:
        return "No tokens currently being tracked."

    msg = f"TRACKED TOKENS ({len(active)})\n\n"

    sorted_tokens = sorted(active.items(), 
                          key=lambda x: x[1].get('current_gain', 0), 
                          reverse=True)[:15]

    for i, (addr, data) in enumerate(sorted_tokens, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        gain = data.get('current_gain', 0)
        whale_count = len(data.get('whale_buyers', []))
        kol_buyers = [w for w in data.get('whale_buyers', []) if w.get('is_kol', False)]

        msg += f"{i}. {symbol}\n"
        msg += f"   Gain: {gain:+.1f}%\n"
        msg += f"   Whales: {whale_count}"

        if kol_buyers:
            msg += f" ({len(kol_buyers)} KOLs)"

        msg += f"\n   {addr[:8]}...\n\n"

    return msg

def cmd_topwhales(chat_id, bot_state):
    """Top 15 performing whales"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        active_whales = [w for w in whales if w.get('total_calls', 0) > 0]

        if not active_whales:
            return "No whale performance data yet. Wait for some trades!"

        sorted_whales = sorted(active_whales, 
                             key=lambda x: (x.get('win_rate', 0), x.get('total_gain', 0)), 
                             reverse=True)[:15]

        msg = "TOP 15 PERFORMERS\n\n"

        for i, whale in enumerate(sorted_whales, 1):
            is_kol = whale.get('type') == 'kol'

            if is_kol:
                name = whale.get('name', 'Unknown KOL')
                twitter = whale.get('twitter', 'N/A')
                identifier = f"{name} ({twitter})"
            else:
                addr = whale.get('address', 'Unknown')
                identifier = f"{addr[:6]}...{addr[-4:]}"

            winrate = whale.get('win_rate', 0)
            total_gain = whale.get('total_gain', 0)
            total_calls = whale.get('total_calls', 0)
            chain = whale.get('chain', '?').upper()

            msg += f"{i}. {identifier}\n"
            msg += f"   {chain} | {winrate:.0f}% WR | {total_calls} calls\n"
            msg += f"   Total Gain: {total_gain:+.1f}%\n\n"

        return msg

    except Exception as e:
        return f"Error: {str(e)}"

def cmd_performance(chat_id, bot_state):
    """Alias for topwhales"""
    return cmd_topwhales(chat_id, bot_state)

def cmd_multibuys(chat_id, bot_state):
    """Show tokens with multiple whale buyers"""
    tracked = bot_state.get('tracked_tokens', {})

    multibuys = {k: v for k, v in tracked.items() 
                if len(v.get('whale_buyers', [])) >= 2 and v.get('active', True)}

    if not multibuys:
        return "No multi-buy signals currently."

    sorted_multibuys = sorted(multibuys.items(), 
                            key=lambda x: len(x[1].get('whale_buyers', [])), 
                            reverse=True)[:10]

    msg = "MULTI-BUY SIGNALS\n\n"

    for i, (addr, data) in enumerate(sorted_multibuys, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        whale_count = len(data.get('whale_buyers', []))
        gain = data.get('current_gain', 0)
        kol_count = sum(1 for w in data.get('whale_buyers', []) if w.get('is_kol', False))

        msg += f"{i}. {symbol}\n"
        msg += f"   {whale_count} whales bought"

        if kol_count > 0:
            msg += f" ({kol_count} KOLs)"

        msg += f"\n   Current: {gain:+.1f}%\n\n"

    return msg

def cmd_promotions(chat_id, bot_state):
    """Show recent tier changes"""
    promotions = bot_state.get('tier_changes', [])

    if not promotions:
        return "No tier changes yet."

    recent = promotions[-10:]
    msg = "RECENT TIER CHANGES\n\n"

    for change in reversed(recent):
        whale_addr = change.get('whale', 'Unknown')
        old_tier = change.get('old_tier', 0)
        new_tier = change.get('new_tier', 0)
        reason = change.get('reason', 'N/A')

        direction = "PROMOTED" if new_tier < old_tier else "DEMOTED"
        short_addr = f"{whale_addr[:6]}...{whale_addr[-4:]}"

        msg += f"{direction}\n"
        msg += f"{short_addr}\n"
        msg += f"Tier {old_tier} -> Tier {new_tier}\n"
        msg += f"Reason: {reason}\n\n"

    return msg

def cmd_guide(chat_id):
    """User guide"""
    msg = "WHALE TRACKER BOT - GUIDE\n\n"
    msg += "WHAT THIS BOT DOES:\n"
    msg += "Monitors 2,000+ elite whale & KOL wallets across Solana and Base chains.\n\n"
    msg += "KOL TRACKING (NEW!):\n"
    msg += "Track crypto influencers who often buy BEFORE tweeting. Get 5-30 min edge!\n\n"
    msg += "4-TIER SYSTEM:\n"
    msg += "Tier 1 (Elite) - 30s checks\n"
    msg += "Tier 2 (Active) - 3m checks\n"
    msg += "Tier 3 (Semi) - 10m checks\n"
    msg += "Tier 4 (Dormant) - 24h checks\n\n"
    msg += "KEY COMMANDS:\n"
    msg += "/stats - Bot statistics\n"
    msg += "/kols - View all tracked KOLs\n"
    msg += "/tracked - Active tokens\n"
    msg += "/topwhales - Leaderboard\n"
    msg += "/multibuys - High conviction signals\n\n"
    msg += "ALERT TYPES:\n"
    msg += "1. Whale Buy - Regular whale buys\n"
    msg += "2. KOL Alert - Influencer buys\n"
    msg += "3. Multi-Buy - 2+ whales buy same token\n"
    msg += "4. Sell Alert - Whale exits position\n"
    msg += "5. Price Milestones - +10%, +25%, +50%, etc\n\n"
    msg += "Always DYOR! Not financial advice."
    return msg
