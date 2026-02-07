"""
Feature functions for Whale Tracker Bot
All tracking, monitoring, and detection features
ADD NEW FEATURES HERE!
"""

import time
from datetime import datetime
from state import bot_state, save_bot_state
from utils import get_token_info, get_solana_tokens, get_base_tokens, send_telegram_alert
from config import BLACKLIST_TOKENS, PRICE_MILESTONES

# ============================================================
# PERFORMANCE TRACKING
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
            'alerts_sent': {str(m): False for m in PRICE_MILESTONES},
            'status': 'active',
            'sells_detected': []
        }
    else:
        if whale_address not in bot_state['tracked_tokens'][token_address]['whales_bought']:
            bot_state['tracked_tokens'][token_address]['whales_bought'].append(whale_address)
            bot_state['tracked_tokens'][token_address]['whale_balances'][whale_address] = balance
    
    # Track in whale_token_balances for sell detection
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
# SELL DETECTION
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
# PRICE TRACKING
# ============================================================

def track_token_performance():
    """Track token performance and send price milestone alerts"""
    
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
            
            # Check milestones
            for milestone in PRICE_MILESTONES:
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
