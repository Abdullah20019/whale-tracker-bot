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
        return "❌ Unknown command. Use /help to see available commands."

def cmd_start(chat_id):
    """Welcome message"""
    msg = """
🐋 Welcome to Whale Tracker Bot V4!

I monitor elite crypto whales & KOLs across Solana and Base chains.
Get instant alerts when they buy tokens!

🌟 NEW: Now tracking crypto KOL wallets!

📱 Quick Commands:
/help - All commands
/stats - Bot statistics  
/kols - View tracked KOLs
/tracked - Active tokens
/guide - Complete guide

Let's catch some whales! 🚀
"""
    return msg

def cmd_help(chat_id):
    """Show all commands"""
    msg = """
📱 AVAILABLE COMMANDS

📊 STATISTICS:
/stats - Overall bot statistics
/kols - View all tracked KOLs
/tiers - Performance by tier
/tier1 to /tier4 - View specific tier

🎯 TRACKING:
/tracked - Currently tracked tokens
/topwhales - Top 15 performers
/performance - Whale leaderboard
/multibuys - Multi-whale signals

🔔 INFO:
/promotions - Recent tier changes
/guide - Detailed user guide
/help - This message

💡 Tip: Use /kols to see all crypto KOLs we're tracking!
"""
    return msg

def cmd_stats(chat_id, bot_state):
    """Overall bot statistics with KOL breakdown"""
    try:
        # Load whale data
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        # Count totals
        total_whales = len(whales)

        # Separate KOLs from regular whales
        kols = [w for w in whales if w.get('type') == 'kol']
        regular_whales = [w for w in whales if w.get('type') != 'kol']

        # Count by chain
        sol_whales = len([w for w in whales if w.get('chain') == 'sol'])
        base_whales = len([w for w in whales if w.get('chain') == 'base'])

        sol_kols = len([k for k in kols if k.get('chain') == 'sol'])
        base_kols = len([k for k in kols if k.get('chain') == 'base'])

        # Count by tier
        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for whale in whales:
            tier = whale.get('tier', 3)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Tracked tokens
        tracked_tokens = bot_state.get('tracked_tokens', {})
        active_tokens = len([t for t in tracked_tokens.values() if t.get('active', True)])

        msg = f"""
📊 BOT STATISTICS

🎯 Total Wallets Monitored: {total_whales:,}
🌟 KOLs: {len(kols)}
🐋 Regular Whales: {len(regular_whales)}

🔗 By Chain:
  Solana: {sol_whales} ({sol_kols} KOLs)
  Base: {base_whales} ({base_kols} KOLs)

🏆 By Tier:
  🔥 Tier 1 (Elite): {tier_counts[1]} whales
  ⭐ Tier 2 (Active): {tier_counts[2]} whales
  📊 Tier 3 (Semi): {tier_counts[3]} whales
  💤 Tier 4 (Dormant): {tier_counts[4]} whales

📈 Currently Tracking: {active_tokens} tokens

💡 Use /kols to see all KOLs!
"""
        return msg

    except Exception as e:
        return f"❌ Error loading stats: {str(e)}"

def cmd_kols(chat_id, bot_state):
    """Display all tracked KOLs"""
    try:
        # Load whale data
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        # Filter KOLs only
        kols = [w for w in whales if w.get('type') == 'kol']

        if not kols:
            return "⚠️ No KOLs found in tracker. Run kol_scraper.py to add KOLs!"

        # Sort by tier, then by chain
        kols.sort(key=lambda x: (x.get('tier', 4), x.get('chain', 'zzz')))

        # Group by tier
        tier_groups = {1: [], 2: [], 3: [], 4: []}
        for kol in kols:
            tier = kol.get('tier', 3)
            tier_groups[tier].append(kol)

        msg = f"🌟 CRYPTO KOL TRACKER

"
        msg += f"📊 Total KOLs: {len(kols)}

"

        tier_emojis = {1: '🔥', 2: '⭐', 3: '📊', 4: '💤'}
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

            msg += f"{tier_emojis[tier]} {tier_names[tier]}
"
            msg += f"━━━━━━━━━━━━━━━━━━━━
"

            for i, kol in enumerate(tier_kols, 1):
                name = kol.get('name', 'Unknown')
                twitter = kol.get('twitter', 'N/A')
                chain = kol.get('chain', '?').upper()
                winrate = kol.get('win_rate', 0)

                # Truncate name if too long
                if len(name) > 20:
                    name = name[:17] + "..."

                msg += f"{i}. {name}
"
                msg += f"   🐦 {twitter} | {chain}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "
"

                # Limit to 10 per tier to avoid message length issues
                if i >= 10:
                    remaining = len(tier_kols) - 10
                    if remaining > 0:
                        msg += f"   ... and {remaining} more
"
                    break

            msg += "
"

        msg += "💡 Use /tier1 through /tier4 for full lists!"

        return msg

    except Exception as e:
        return f"❌ Error loading KOLs: {str(e)}"

def cmd_tier_detail(chat_id, bot_state, tier_num):
    """Show detailed view of specific tier with KOL indicators"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        tier_whales = [w for w in whales if w.get('tier') == tier_num]

        if not tier_whales:
            return f"⚠️ No whales in Tier {tier_num}"

        # Separate KOLs and regular whales
        kols = [w for w in tier_whales if w.get('type') == 'kol']
        regular = [w for w in tier_whales if w.get('type') != 'kol']

        tier_emojis = {1: '🔥', 2: '⭐', 3: '📊', 4: '💤'}
        tier_names = {
            1: 'TIER 1 - ELITE WHALES (30s checks)',
            2: 'TIER 2 - ACTIVE WHALES (3m checks)',
            3: 'TIER 3 - SEMI-ACTIVE WHALES (10m checks)',
            4: 'TIER 4 - DORMANT WHALES (24h checks)'
        }

        msg = f"{tier_emojis[tier_num]} {tier_names[tier_num]}

"
        msg += f"📊 Total: {len(tier_whales)} wallets
"
        msg += f"🌟 KOLs: {len(kols)}
"
        msg += f"🐋 Regular Whales: {len(regular)}

"

        # Show KOLs first
        if kols:
            msg += "🌟 KOLS:
"
            msg += "━━━━━━━━━━━━━━━━━━━━
"

            for i, kol in enumerate(kols[:15], 1):
                name = kol.get('name', 'Unknown')
                twitter = kol.get('twitter', 'N/A')
                chain = kol.get('chain', '?').upper()
                winrate = kol.get('win_rate', 0)

                if len(name) > 15:
                    name = name[:12] + "..."

                msg += f"{i}. {name} | {chain}
"
                msg += f"   🐦 {twitter}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "
"

            if len(kols) > 15:
                msg += f"
... and {len(kols) - 15} more KOLs
"

            msg += "
"

        # Show regular whales
        if regular:
            msg += "🐋 REGULAR WHALES:
"
            msg += "━━━━━━━━━━━━━━━━━━━━
"

            for i, whale in enumerate(regular[:10], 1):
                addr = whale.get('address', 'Unknown')
                chain = whale.get('chain', '?').upper()
                winrate = whale.get('win_rate', 0)

                short_addr = f"{addr[:6]}...{addr[-4:]}"
                msg += f"{i}. {short_addr} | {chain}"

                if winrate > 0:
                    msg += f" | {winrate:.0f}% WR"

                msg += "
"

            if len(regular) > 10:
                msg += f"
... and {len(regular) - 10} more whales
"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_tiers(chat_id, bot_state):
    """Show tier statistics including KOL breakdown"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        msg = "🏆 TIER STATISTICS

"

        for tier in [1, 2, 3, 4]:
            tier_whales = [w for w in whales if w.get('tier') == tier]
            tier_kols = [w for w in tier_whales if w.get('type') == 'kol']

            tier_emojis = {1: '🔥', 2: '⭐', 3: '📊', 4: '💤'}
            tier_names = {1: 'Elite', 2: 'Active', 3: 'Semi-Active', 4: 'Dormant'}
            check_intervals = {1: '30s', 2: '3m', 3: '10m', 4: '24h'}

            msg += f"{tier_emojis[tier]} TIER {tier} - {tier_names[tier]}
"
            msg += f"Check Interval: {check_intervals[tier]}
"
            msg += f"Total: {len(tier_whales)} wallets
"
            msg += f"  🌟 KOLs: {len(tier_kols)}
"
            msg += f"  🐋 Whales: {len(tier_whales) - len(tier_kols)}
"

            # Calculate performance if available
            total_calls = sum(w.get('total_calls', 0) for w in tier_whales)
            if total_calls > 0:
                wins = sum(w.get('win_count', 0) for w in tier_whales)
                winrate = (wins / total_calls * 100) if total_calls > 0 else 0
                msg += f"Performance: {winrate:.1f}% WR | {total_calls} calls
"

            msg += "
"

        msg += "💡 Use /tier1 to /tier4 for detailed lists!"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_tracked(chat_id, bot_state):
    """Currently tracked tokens"""
    tracked = bot_state.get('tracked_tokens', {})
    active = {k: v for k, v in tracked.items() if v.get('active', True)}

    if not active:
        return "📊 No tokens currently being tracked."

    msg = f"📊 TRACKED TOKENS ({len(active)})

"

    sorted_tokens = sorted(active.items(), 
                          key=lambda x: x[1].get('current_gain', 0), 
                          reverse=True)[:15]

    for i, (addr, data) in enumerate(sorted_tokens, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        gain = data.get('current_gain', 0)
        whale_count = len(data.get('whale_buyers', []))

        # Check if any buyers are KOLs
        kol_buyers = [w for w in data.get('whale_buyers', []) if w.get('is_kol', False)]

        gain_emoji = "📈" if gain > 0 else "📉"
        msg += f"{i}. {symbol} {gain_emoji}
"
        msg += f"   Gain: {gain:+.1f}%
"
        msg += f"   Whales: {whale_count}"

        if kol_buyers:
            msg += f" ({len(kol_buyers)} KOLs 🌟)"

        msg += f"
   {addr[:8]}...

"

    return msg

def cmd_topwhales(chat_id, bot_state):
    """Top 15 performing whales including KOLs"""
    try:
        with open('whales_tiered_final.json', 'r') as f:
            whales = json.load(f)

        # Filter whales with calls
        active_whales = [w for w in whales if w.get('total_calls', 0) > 0]

        if not active_whales:
            return "📊 No whale performance data yet. Wait for some trades!"

        # Sort by win rate then total gain
        sorted_whales = sorted(active_whales, 
                             key=lambda x: (x.get('win_rate', 0), x.get('total_gain', 0)), 
                             reverse=True)[:15]

        msg = "🏆 TOP 15 PERFORMERS

"

        for i, whale in enumerate(sorted_whales, 1):
            is_kol = whale.get('type') == 'kol'

            if is_kol:
                name = whale.get('name', 'Unknown KOL')
                twitter = whale.get('twitter', 'N/A')
                identifier = f"🌟 {name} ({twitter})"
            else:
                addr = whale.get('address', 'Unknown')
                identifier = f"🐋 {addr[:6]}...{addr[-4:]}"

            winrate = whale.get('win_rate', 0)
            total_gain = whale.get('total_gain', 0)
            total_calls = whale.get('total_calls', 0)
            chain = whale.get('chain', '?').upper()

            msg += f"{i}. {identifier}
"
            msg += f"   {chain} | {winrate:.0f}% WR | {total_calls} calls
"
            msg += f"   Total Gain: {total_gain:+.1f}%

"

        return msg

    except Exception as e:
        return f"❌ Error: {str(e)}"

def cmd_performance(chat_id, bot_state):
    """Alias for topwhales"""
    return cmd_topwhales(chat_id, bot_state)

def cmd_multibuys(chat_id, bot_state):
    """Show tokens with multiple whale buyers"""
    tracked = bot_state.get('tracked_tokens', {})

    multibuys = {k: v for k, v in tracked.items() 
                if len(v.get('whale_buyers', [])) >= 2 and v.get('active', True)}

    if not multibuys:
        return "📊 No multi-buy signals currently."

    sorted_multibuys = sorted(multibuys.items(), 
                            key=lambda x: len(x[1].get('whale_buyers', [])), 
                            reverse=True)[:10]

    msg = "🚨 MULTI-BUY SIGNALS

"

    for i, (addr, data) in enumerate(sorted_multibuys, 1):
        symbol = data.get('symbol', 'UNKNOWN')
        whale_count = len(data.get('whale_buyers', []))
        gain = data.get('current_gain', 0)

        # Count KOL buyers
        kol_count = sum(1 for w in data.get('whale_buyers', []) if w.get('is_kol', False))

        msg += f"{i}. {symbol}
"
        msg += f"   {whale_count} whales bought"

        if kol_count > 0:
            msg += f" ({kol_count} KOLs 🌟)"

        msg += f"
   Current: {gain:+.1f}%

"

    return msg

def cmd_promotions(chat_id, bot_state):
    """Show recent tier changes"""
    promotions = bot_state.get('tier_changes', [])

    if not promotions:
        return "📊 No tier changes yet."

    recent = promotions[-10:]
    msg = "📈 RECENT TIER CHANGES

"

    for change in reversed(recent):
        whale_addr = change.get('whale', 'Unknown')
        old_tier = change.get('old_tier', 0)
        new_tier = change.get('new_tier', 0)
        reason = change.get('reason', 'N/A')

        direction = "📈 PROMOTED" if new_tier < old_tier else "📉 DEMOTED"
        short_addr = f"{whale_addr[:6]}...{whale_addr[-4:]}"

        msg += f"{direction}
"
        msg += f"{short_addr}
"
        msg += f"Tier {old_tier} → Tier {new_tier}
"
        msg += f"Reason: {reason}

"

    return msg

def cmd_guide(chat_id):
    """Comprehensive user guide"""
    msg = """
📚 WHALE TRACKER BOT - COMPLETE GUIDE

🎯 WHAT THIS BOT DOES:
Monitors 2,000+ elite whale & KOL wallets across Solana and Base chains. Alerts you instantly when they buy tokens!

🌟 KOL TRACKING (NEW!):
We now track crypto Key Opinion Leaders (influencers) who often buy BEFORE tweeting. Get 5-30 min edge!

🏆 4-TIER SYSTEM:
🔥 Tier 1 (Elite) - 30s checks - Top performers
⭐ Tier 2 (Active) - 3m checks - Good performers  
📊 Tier 3 (Semi) - 10m checks - Decent performers
💤 Tier 4 (Dormant) - 24h checks - Inactive whales

📱 KEY COMMANDS:
/stats - Bot statistics
/kols - View all tracked KOLs
/tracked - Active token tracking
/topwhales - Performance leaderboard
/multibuys - High conviction signals
/tiers - Tier performance stats

🚨 ALERT TYPES:
1. 🐋 Whale Buy - Regular whale buys token
2. 🌟 KOL Alert - Crypto influencer buys (with Twitter handle!)
3. 🚨 Multi-Buy - 2+ whales buy same token (high conviction)
4. 💰 Sell Alert - Whale exits 30%+ of position
5. 📊 Price Milestones - +10%, +25%, +50%, +100%, +200%
6. 💤 Wake-Up - Dormant whale suddenly trades

💡 HOW TO USE:
1. Wait for alerts in Telegram
2. Check token metrics (MC, liquidity, volume)
3. Research on Dexscreener
4. Decide if you want to buy
5. Set take-profit and stop-loss
6. Track performance with /tracked

⚠️ IMPORTANT:
- Whale alerts = research starting point
- Always DYOR (Do Your Own Research)
- Not financial advice
- Manage risk appropriately

🔥 KOL ADVANTAGE:
KOLs often buy 5-30 mins BEFORE tweeting. You get alerted when they buy, giving you early entry before their followers pump the token!

📊 PERFORMANCE TRACKING:
Bot automatically tracks whale performance and adjusts tiers hourly based on win rates and profits.

Need help? Ask in the group!
"""
    return msg
