"""
All Telegram command handlers
Easy to add new commands here without touching main code
"""

import json
import time
from datetime import datetime
from config import ADMIN_USER_ID, WHALE_LIST_FILE, TIER_CONFIG
from state import bot_state, save_bot_state
from utils import is_admin

# ============================================================
# COMMAND: /stats
# ============================================================

def get_bot_stats():
    """Get bot statistics"""
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    tier_1 = [w for w in whales if w.get('tier') == 1]
    tier_2 = [w for w in whales if w.get('tier') == 2]
    tier_3 = [w for w in whales if w.get('tier') == 3]
    tier_4 = [w for w in whales if w.get('tier') == 4]
    
    uptime_hours = (time.time() - bot_state.get('start_time', time.time())) / 3600
    
    tracked_count = len(bot_state.get('tracked_tokens', {}))
    multi_buy_count = len(bot_state.get('multi_buys', {}))
    monitored_positions = len(bot_state.get('whale_token_balances', {}))
    
    return f"""
📊 <b>BOT STATISTICS</b>

━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALES TRACKED</b>
━━━━━━━━━━━━━━━━━━━━
🔥 Tier 1 (Elite): <b>{len(tier_1)}</b>
⭐ Tier 2 (Active): <b>{len(tier_2)}</b>
📊 Tier 3 (Semi): <b>{len(tier_3)}</b>
💤 Tier 4 (Dormant): <b>{len(tier_4)}</b>
🎯 Total: <b>{len(whales)}</b>

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

# ============================================================
# COMMAND: /topwhales
# ============================================================

def get_top_whales():
    """Get top 15 whales"""
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    tier_1 = [w for w in whales if w.get('tier') == 1]
    sorted_whales = sorted(tier_1, key=lambda x: x.get('win_count', 0), reverse=True)[:15]
    
    message = "🏆 <b>TOP 15 ELITE WHALES</b>\n\n"
    
    for i, whale in enumerate(sorted_whales, 1):
        chain_icon = "🟣" if whale['chain'] == 'solana' else "🔵"
        tier_emoji = TIER_CONFIG.get(whale.get('tier', 1), {}).get('emoji', '🔥')
        message += f"{i}. {chain_icon}{tier_emoji} <code>{whale['address'][:16]}...</code>\n   Wins: <b>{whale.get('win_count', 0)}</b> | WR: <b>{whale.get('win_rate', 0):.1f}%</b>\n"
        if i % 5 == 0:
            message += "\n"
    
    return message

# ============================================================
# COMMAND: /lastbuys
# ============================================================

def get_last_buys():
    """Get last 15 buys"""
    last_buys = bot_state.get('last_buys', [])
    
    if not last_buys:
        return "📭 No recent buys detected yet."
    
    message = "🔥 <b>LAST 15 QUALITY BUYS</b>\n\n"
    
    for i, buy in enumerate(reversed(last_buys[-15:]), 1):
        tier = buy.get('tier', 1)
        tier_emoji = TIER_CONFIG.get(tier, {}).get('emoji', '🔥')
        message += f"{i}. 💎 <b>{buy['symbol']}</b> {tier_emoji}\n   MC: ${buy['mc']:,.0f} | Tier {tier}\n   {buy['timestamp']} | <code>{buy['token'][:16]}...</code>\n\n"
    
    return message

# ============================================================
# COMMAND: /tracked
# ============================================================

def get_tracked_tokens():
    """Get tracked tokens"""
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

# ============================================================
# COMMAND: /multibuys
# ============================================================

def get_multi_buys():
    """Get multi-buy alerts"""
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

# ============================================================
# COMMAND: /performance
# ============================================================

def get_whale_performance_report():
    """Get whale performance leaderboard"""
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

# ============================================================
# COMMAND: /filters
# ============================================================

def get_filters_info():
    """Get current filter settings"""
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

# ============================================================
# TIER SYSTEM COMMANDS
# ============================================================

def get_tier_stats():
    """Get statistics for each tier"""
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    tier_1 = [w for w in whales if w.get('tier') == 1]
    tier_2 = [w for w in whales if w.get('tier') == 2]
    tier_3 = [w for w in whales if w.get('tier') == 3]
    tier_4 = [w for w in whales if w.get('tier') == 4]
    
    # Get performance data
    perf = bot_state.get('whale_performance', {})
    
    def get_tier_performance(tier_whales):
        addresses = [w['address'] for w in tier_whales]
        tier_perf = [perf[addr] for addr in addresses if addr in perf]
        
        if not tier_perf:
            return {'avg_gain': 0, 'success_rate': 0, 'total_calls': 0}
        
        total_gain = sum(p['total_gain'] for p in tier_perf)
        total_calls = sum(p['tokens_tracked'] for p in tier_perf)
        successful_calls = sum(p['successful_calls'] for p in tier_perf)
        
        avg_gain = total_gain / total_calls if total_calls > 0 else 0
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        return {
            'avg_gain': avg_gain,
            'success_rate': success_rate,
            'total_calls': total_calls
        }
    
    t1_perf = get_tier_performance(tier_1)
    t2_perf = get_tier_performance(tier_2)
    t3_perf = get_tier_performance(tier_3)
    t4_perf = get_tier_performance(tier_4)
    
    return f"""
📊 <b>TIERED SYSTEM STATISTICS</b>

━━━━━━━━━━━━━━━━━━━━
🔥 <b>TIER 1 - ELITE</b>
━━━━━━━━━━━━━━━━━━━━
Whales: <b>{len(tier_1)}</b>
Check Interval: <b>30 seconds</b>
Avg Gain: <b>{t1_perf['avg_gain']:+.1f}%</b>
Success Rate: <b>{t1_perf['success_rate']:.1f}%</b>
Total Calls: <b>{t1_perf['total_calls']}</b>

━━━━━━━━━━━━━━━━━━━━
⭐ <b>TIER 2 - ACTIVE</b>
━━━━━━━━━━━━━━━━━━━━
Whales: <b>{len(tier_2)}</b>
Check Interval: <b>3 minutes</b>
Avg Gain: <b>{t2_perf['avg_gain']:+.1f}%</b>
Success Rate: <b>{t2_perf['success_rate']:.1f}%</b>
Total Calls: <b>{t2_perf['total_calls']}</b>

━━━━━━━━━━━━━━━━━━━━
📊 <b>TIER 3 - SEMI-ACTIVE</b>
━━━━━━━━━━━━━━━━━━━━
Whales: <b>{len(tier_3)}</b>
Check Interval: <b>10 minutes</b>
Avg Gain: <b>{t3_perf['avg_gain']:+.1f}%</b>
Success Rate: <b>{t3_perf['success_rate']:.1f}%</b>
Total Calls: <b>{t3_perf['total_calls']}</b>

━━━━━━━━━━━━━━━━━━━━
💤 <b>TIER 4 - DORMANT</b>
━━━━━━━━━━━━━━━━━━━━
Whales: <b>{len(tier_4)}</b>
Check Interval: <b>24 hours</b>
Avg Gain: <b>{t4_perf['avg_gain']:+.1f}%</b>
Success Rate: <b>{t4_perf['success_rate']:.1f}%</b>
Total Calls: <b>{t4_perf['total_calls']}</b>

━━━━━━━━━━━━━━━━━━━━
🎯 <b>TOTAL TRACKED: {len(whales)}</b>
"""

def get_tier_whales(tier_number):
    """Get whales in specific tier"""
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    tier_whales = [w for w in whales if w.get('tier') == tier_number]
    
    if not tier_whales:
        return f"📭 No whales in Tier {tier_number}"
    
    tier_info = TIER_CONFIG[tier_number]
    
    message = f"""
{tier_info['emoji']} <b>TIER {tier_number} - {tier_info['name'].upper()}</b>

Check Interval: <b>{tier_info['check_interval']}s</b>
Priority: <b>{tier_info['alert_priority']}</b>
Whales: <b>{len(tier_whales)}</b>

━━━━━━━━━━━━━━━━━━━━
<b>TOP 15 WHALES:</b>
━━━━━━━━━━━━━━━━━━━━

"""
    
    sorted_whales = sorted(tier_whales, key=lambda x: x.get('win_rate', 0), reverse=True)[:15]
    
    for i, whale in enumerate(sorted_whales, 1):
        chain_icon = "🟣" if whale['chain'] == 'solana' else "🔵"
        message += f"{i}. {chain_icon} <code>{whale['address'][:16]}...</code>\n"
        message += f"   WR: <b>{whale.get('win_rate', 0):.1f}%</b> | Wins: {whale.get('win_count', 0)}\n"
        if i % 5 == 0:
            message += "\n"
    
    return message

def get_recent_promotions():
    """Show recent tier changes"""
    promotions = bot_state.get('tier_changes', [])
    
    if not promotions:
        return "📭 No tier changes yet."
    
    message = "📈 <b>RECENT TIER CHANGES</b>\n\n"
    
    for change in reversed(promotions[-15:]):
        direction = "⬆️" if change['new_tier'] < change['old_tier'] else "⬇️"
        message += f"{direction} <code>{change['whale'][:16]}...</code>\n"
        message += f"   Tier {change['old_tier']} → Tier {change['new_tier']}\n"
        message += f"   Reason: {change['reason']}\n"
        message += f"   {change['timestamp']}\n\n"
    
    return message

# ============================================================
# COMMAND: /help
# ============================================================

def get_help():
    """Get help message"""
    return """
🤖 <b>WHALE TRACKER BOT V4 - TIERED</b>

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
🎯 <b>TIER SYSTEM</b>
━━━━━━━━━━━━━━━━━━━━
/tiers - Tier statistics
/tier1 - Elite whales (30s)
/tier2 - Active whales (3m)
/tier3 - Semi-active (10m)
/tier4 - Dormant (24h)
/promotions - Recent tier changes

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
✅ 4-Tier monitoring system
✅ Auto-promotion/demotion
✅ Multi-buy detection
✅ Whale exit alerts
✅ Performance tracking
"""

# ============================================================
# COMMAND: /guide
# ============================================================

def get_guide():
    """Get comprehensive user guide"""
    return """
🐋 <b>WHALE TRACKER BOT V4 - USER GUIDE</b>

━━━━━━━━━━━━━━━━━━━━
📋 <b>AVAILABLE COMMANDS</b>
━━━━━━━━━━━━━━━━━━━━

<b>📊 MONITORING COMMANDS</b>

/stats - View current monitoring statistics
• Total whales tracked per tier
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

<b>🎯 TIER SYSTEM</b>

/tiers - Complete tier statistics
• Performance by tier
• Check intervals

/tier1 - Elite whales (30s checks)
/tier2 - Active whales (3m checks)
/tier3 - Semi-active (10m checks)
/tier4 - Dormant (24h checks)

/promotions - Recent tier changes
• See who got promoted/demoted
• Performance reasons

━━━━━━━━━━━━━━━━━━━━
🔔 <b>ALERT TYPES</b>
━━━━━━━━━━━━━━━━━━━━

<b>🚨 NEW POSITION ALERTS</b>
When a whale buys a new token:
• Token name & symbol
• Tier & priority level
• Market cap & liquidity
• Buy amount in USD
• Whale win rate
• Multi-buy detection (2+ whales)
• Wake-up alerts for dormant whales

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
⚙️ <b>TIER SYSTEM EXPLAINED</b>
━━━━━━━━━━━━━━━━━━━━

<b>🔥 Tier 1 - Elite Active Whales</b>
• 60%+ success rate
• 50%+ average gain
• 10+ successful calls
• Checked every 30 seconds
• REAL-TIME monitoring

<b>⭐ Tier 2 - Active Whales</b>
• 50%+ success rate
• 30%+ average gain
• 5+ successful calls
• Checked every 3 minutes

<b>📊 Tier 3 - Semi-Active Whales</b>
• 40%+ success rate
• 10%+ average gain
• Background monitoring
• Checked every 10 minutes

<b>💤 Tier 4 - Dormant Whales</b>
• Inactive 90+ days
• Checked every 24 hours
• Wake-up alerts when they trade
• Often signals insider info

<b>🔄 Auto-Promotion System:</b>
• Bot evaluates performance hourly
• Whales automatically move tiers
• Based on success rate & avg gain
• You get notified of changes

━━━━━━━━━━━━━━━━━━━━
🎯 <b>HOW IT WORKS</b>
━━━━━━━━━━━━━━━━━━━━

<b>1. BASELINE SCAN</b>
Bot snapshots all whale positions

<b>2. TIERED MONITORING</b>
Continuous checks based on tier:
• Elite whales: Real-time (30s)
• Active whales: Every 3m
• Semi-active: Every 10m
• Dormant: Daily checks

<b>3. INSTANT ALERTS</b>
Filtered quality plays sent with:
• Full token metrics
• Whale tier & priority
• DexScreener link

<b>4. PERFORMANCE TRACKING</b>
Bot monitors and reports:
• Price milestones
• Whale exits
• Success rates
• Tier promotions

━━━━━━━━━━━━━━━━━━━━
💡 <b>PRO TIPS</b>
━━━━━━━━━━━━━━━━━━━━

<b>✅ Do This:</b>
• Prioritize Tier 1 alerts
• Check /tiers weekly
• Watch for multi-buy + Tier 1
• Review /performance regularly
• Act on wake-up alerts fast
• Set your own stop losses

<b>⚠️ Avoid This:</b>
• Ignoring tier levels
• FOMO on Tier 4 alerts
• Missing exit signals
• Over-leveraging

<b>🔥 Best Signals:</b>
• Tier 1 + Multi-buy = 🔥🔥🔥
• Dormant whale wake-up = 🚨
• 3+ whales same token = 💎

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

✅ 4-Tier monitoring system
✅ Auto-promotion/demotion
✅ Multi-buy detection
✅ TRUE whale exit alerts  
✅ Performance tracking
✅ Wake-up alerts
✅ Price follow-ups
✅ Quality filtering
✅ 24/7 monitoring

━━━━━━━━━━━━━━━━━━━━
🚀 <b>Happy Whale Hunting!</b>

Bot running on Railway ☁️
Tier-based intelligent monitoring 🎯
Auto-optimizing performance 🔄
"""

# ============================================================
# ADMIN COMMANDS
# ============================================================

def add_wallet(address, chain, user_id):
    """Add wallet to tracking (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    if any(w['address'] == address for w in whales):
        return f"❌ Wallet already tracked"
    
    new_whale = {
        'address': address,
        'chain': chain.lower(),
        'tier': 3,  # Start at tier 3
        'win_count': 0,
        'win_rate': 0,
        'is_active': True,
        'source': 'manual_add',
        'added_date': datetime.now().strftime("%Y-%m-%d")
    }
    
    whales.append(new_whale)
    
    with open(WHALE_LIST_FILE, 'w') as f:
        json.dump(whales, f, indent=2)
    
    return f"✅ Wallet added to Tier 3! Now tracking {len(whales)} whales."

def remove_wallet(address, user_id):
    """Remove wallet from tracking (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    with open(WHALE_LIST_FILE, 'r') as f:
        whales = json.load(f)
    
    original_count = len(whales)
    whales = [w for w in whales if w['address'] != address]
    
    if len(whales) == original_count:
        return f"❌ Wallet not found"
    
    with open(WHALE_LIST_FILE, 'w') as f:
        json.dump(whales, f, indent=2)
    
    return f"✅ Wallet removed! Now tracking {len(whales)} whales."

def set_filter(setting, value, user_id):
    """Set filter value (admin only)"""
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
    """Pause bot monitoring (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    bot_state['paused'] = True
    save_bot_state()
    return "⏸️ <b>BOT PAUSED</b>"

def resume_bot(user_id):
    """Resume bot monitoring (admin only)"""
    if not is_admin(user_id):
        return "🔒 <b>ACCESS DENIED</b>"
    
    bot_state['paused'] = False
    save_bot_state()
    return "▶️ <b>BOT RESUMED</b>"

# ============================================================
# COMMAND ROUTER
# ============================================================

def handle_command(command_text, user_id):
    """Route commands to appropriate handlers"""
    parts = command_text.strip().split()
    command = parts[0].lower()
    
    # Remove bot username if present
    if '@' in command:
        command = command.split('@')[0]
    
    # Route to appropriate handler
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
    
    # TIER SYSTEM COMMANDS
    elif command == '/tiers':
        return get_tier_stats()
    elif command == '/tier1':
        return get_tier_whales(1)
    elif command == '/tier2':
        return get_tier_whales(2)
    elif command == '/tier3':
        return get_tier_whales(3)
    elif command == '/tier4':
        return get_tier_whales(4)
    elif command == '/promotions':
        return get_recent_promotions()
    
    # ADMIN COMMANDS
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
