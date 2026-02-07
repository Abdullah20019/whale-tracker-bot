"""
Whale tracking features and functions
Contains all logic for checking whales, sending alerts, tracking performance
"""

import time
import requests
from datetime import datetime

# Import from other modules
from config import BLACKLIST_TOKENS, PRICE_MILESTONES, HELIUS_API_KEY, ALCHEMY_API_KEY, TELEGRAM_BOT_TOKEN
from state import bot_state, save_bot_state
from utils import send_telegram_alert, send_telegram_message, get_token_info, passes_filters

# ============================================================
# Main Whale Checking Function
# ============================================================

def check_whale_for_new_buys(whale, whale_tokens, is_baseline=False):
    """
    Check a whale wallet for new token buys
    
    Args:
        whale: Whale dict with address and chain
        whale_tokens: Dict tracking known tokens per whale
        is_baseline: If True, just build baseline without alerts
    """
    
    whale_address = whale['address']
    chain = whale['chain']
    
    try:
        # Get current tokens
        if chain == 'solana':
            current_tokens = get_solana_tokens(whale_address)
        elif chain == 'base':
            current_tokens = get_base_tokens(whale_address)
        else:
            return
        
        # Get known tokens for this whale
        known_tokens = whale_tokens.get(whale_address, set())
        
        # Find new tokens
        new_tokens = []
        for token in current_tokens:
            token_addr = token['address']
            
            if token_addr not in known_tokens:
                new_tokens.append(token)
                whale_tokens[whale_address].add(token_addr)
        
        # If baseline scan, just track tokens
        if is_baseline:
            return
        
        # Process new token buys
        for token in new_tokens:
            token_addr = token['address']
            balance = token.get('balance', 0)
            
            # Get token info from DexScreener
            token_info = get_token_info(token_addr, chain)
            
            if not token_info:
                continue
            
            # Check if passes filters
            passes, reason = passes_filters(token_info)
            
            if passes:
                # Send alert
                send_whale_buy_alert(whale, token_info, balance)
                
                # Track token
                track_token_buy(
                    token_addr, 
                    whale_address, 
                    token_info['price'],
                    token_info['market_cap'],
                    token_info['symbol'],
                    chain,
                    balance
                )
                
                bot_state['alerts_sent'] = bot_state.get('alerts_sent', 0) + 1
                
                # Add to last buys
                if 'last_buys' not in bot_state:
                    bot_state['last_buys'] = []
                
                bot_state['last_buys'].append({
                    'symbol': token_info['symbol'],
                    'token': token_addr,
                    'mc': token_info['market_cap'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                
                # Keep only last 30 buys
                bot_state['last_buys'] = bot_state['last_buys'][-30:]
                
                save_bot_state()
            else:
                bot_state['tokens_filtered'] = bot_state.get('tokens_filtered', 0) + 1
    
    except Exception as e:
        print(f"  ⚠️ Error checking {whale_address[:8]}: {e}")

# ============================================================
# Token Fetching Functions
# ============================================================

def get_solana_tokens(wallet_address):
    """Get all tokens held by a Solana wallet"""
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
    except Exception as e:
        return []

def get_base_tokens(wallet_address):
    """Get all tokens held by a Base wallet"""
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
    except Exception as e:
        return []

# ============================================================
# Alert Functions
# ============================================================

def send_whale_buy_alert(whale, token_info, balance):
    """Send Telegram alert for whale buy"""
    
    whale_addr = whale['address']
    chain = whale['chain'].upper()
    tier = whale.get('tier', 3)
    
    tier_emoji = {1: '🔥', 2: '⭐', 3: '📊', 4: '💤'}.get(tier, '📊')
    
    message = f"""
🚨 {tier_emoji} <b>TIER {tier} WHALE BUY!</b>

💎 <b>{token_info['symbol']}</b>
📊 MC: <b>${token_info['market_cap']:,.0f}</b>
💧 Liq: <b>${token_info['liquidity']:,.0f}</b>

━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE</b>
━━━━━━━━━━━━━━━━━━━━
Address: <code>{whale_addr[:16]}...</code>
Chain: <b>{chain}</b>
Balance: <b>{balance:,.0f}</b> tokens

━━━━━━━━━━━━━━━━━━━━
📈 <b>DETAILS</b>
━━━━━━━━━━━━━━━━━━━━
Price: ${token_info['price']:.8f}
5m: <b>{token_info.get('price_change_5m', 0):+.1f}%</b>
1h: <b>{token_info.get('price_change_1h', 0):+.1f}%</b>

DEX: {token_info.get('dex', 'Unknown')}

🔗 <a href="{token_info['url']}">View Chart</a>
📝 <code>{token_info['symbol']}</code>
━━━━━━━━━━━━━━━━━━━━
"""
    
    send_telegram_alert(message)
    
    print(f"  ✅ {tier_emoji} Alert: {token_info['symbol']} (${token_info['market_cap']:,.0f})")

def send_multi_buy_alert(token_address, whale_count, symbol, mc):
    """Send alert when multiple whales buy same token"""
    
    message = f"""
🔥🔥🔥 <b>MULTI-WHALE BUY!</b> 🔥🔥🔥

💎 <b>{symbol}</b>
<b>{whale_count} WHALES</b> bought this token!

📊 MC: <b>${mc:,.0f}</b>

━━━━━━━━━━━━━━━━━━━━
⚠️ <b>HIGH CONVICTION PLAY!</b>
━━━━━━━━━━━━━━━━━━━━
"""
    
    send_telegram_alert(message)
    print(f"  🔥🔥🔥 MULTI-BUY: {symbol} ({whale_count} whales)")

# ============================================================
# Token Tracking Functions
# ============================================================

def track_token_buy(token_address, whale_address, initial_price, mc, symbol, chain, balance):
    """Start tracking a token after whale buy"""
    
    if 'tracked_tokens' not in bot_state:
        bot_state['tracked_tokens'] = {}
    
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
            'alerts_sent': {},
            'status': 'active',
            'sells_detected': []
        }
    else:
        # Another whale bought same token
        if whale_address not in bot_state['tracked_tokens'][token_address]['whales_bought']:
            bot_state['tracked_tokens'][token_address]['whales_bought'].append(whale_address)
            bot_state['tracked_tokens'][token_address]['whale_balances'][whale_address] = balance
            
            # Multi-buy alert
            whale_count = len(bot_state['tracked_tokens'][token_address]['whales_bought'])
            if whale_count >= 2:
                # Track multi-buys
                if 'multi_buys' not in bot_state:
                    bot_state['multi_buys'] = {}
                
                if token_address not in bot_state['multi_buys']:
                    bot_state['multi_buys'][token_address] = {
                        'whale_count': whale_count,
                        'detected_time': time.time()
                    }
                    send_multi_buy_alert(token_address, whale_count, symbol, mc)
    
    # NEW: Track whale balance for sell detection
    if 'whale_token_balances' not in bot_state:
        bot_state['whale_token_balances'] = {}
    
    balance_key = f"{whale_address}_{token_address}"
    bot_state['whale_token_balances'][balance_key] = {
        'whale': whale_address,
        'token': token_address,
        'symbol': symbol,
        'chain': chain,
        'initial_balance': balance,
        'current_balance': balance,
        'last_check': time.time()
    }
    
    save_bot_state()

# ============================================================
# Performance Tracking
# ============================================================

def update_whale_performance(whale_address, gain_pct):
    """Update whale performance stats"""
    
    if 'whale_performance' not in bot_state:
        bot_state['whale_performance'] = {}
    
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
    stats['total_gain'] += gain_pct
    
    if gain_pct >= 100:
        stats['successful_calls'] += 1
    
    if gain_pct > stats['best_call']:
        stats['best_call'] = gain_pct
    
    if stats['worst_call'] == 0 or gain_pct < stats['worst_call']:
        stats['worst_call'] = gain_pct
    
    save_bot_state()

# ============================================================
# SELL DETECTION FUNCTIONS (NEW!)
# ============================================================

def check_whale_sells():
    """Check if tracked whales sold any positions"""
    
    whale_balances = bot_state.get('whale_token_balances', {})
    
    if not whale_balances:
        return
    
    print(f"  🔍 Checking {len(whale_balances)} positions for sells...")
    
    for balance_key, balance_data in list(whale_balances.items()):
        try:
            # Skip if checked recently
            if time.time() - balance_data.get('last_check', 0) < 120:
                continue
            
            whale_address = balance_data['whale']
            token_address = balance_data['token']
            initial_balance = balance_data['initial_balance']
            chain = balance_data['chain']
            
            # Get current balance
            if chain == 'solana':
                current_tokens = get_solana_tokens(whale_address)
            else:
                current_tokens = get_base_tokens(whale_address)
            
            current_balance = 0
            for token in current_tokens:
                if token['address'].lower() == token_address.lower():
                    current_balance = token['balance']
                    break
            
            # Update tracking
            balance_data['current_balance'] = current_balance
            balance_data['last_check'] = time.time()
            
            # Calculate balance change
            if initial_balance > 0:
                balance_change_pct = ((current_balance - initial_balance) / initial_balance) * 100
                
                # SELL DETECTED: Sold 30%+ of position
                if balance_change_pct < -30:
                    send_sell_alert(balance_data, balance_change_pct)
                    
                    # Remove from tracking if fully sold
                    if current_balance == 0:
                        del bot_state['whale_token_balances'][balance_key]
            
            save_bot_state()
            
        except Exception as e:
            print(f"  ⚠️ Error checking sell for {balance_key[:16]}: {e}")
            continue


def send_sell_alert(balance_data, sold_pct):
    """Send Telegram alert when whale sells"""
    
    whale_addr = balance_data['whale']
    token_addr = balance_data['token']
    symbol = balance_data['symbol']
    chain = balance_data['chain']
    initial_balance = balance_data['initial_balance']
    current_balance = balance_data['current_balance']
    
    # Get token info for current price
    token_info = get_token_info(token_addr, chain)
    
    if not token_info:
        return
    
    # Get tracked token data for entry price
    tracked = bot_state.get('tracked_tokens', {}).get(token_addr, {})
    initial_price = tracked.get('initial_price', 0)
    current_price = token_info['price']
    
    # Calculate profit/loss
    if initial_price > 0:
        price_gain = ((current_price - initial_price) / initial_price) * 100
    else:
        price_gain = 0
    
    sold_amount = initial_balance - current_balance
    sold_pct_abs = abs(sold_pct)
    
    # Determine if profit or loss
    profit_emoji = "✅" if price_gain > 0 else "❌"
    
    message = f"""
🚨 <b>WHALE EXIT DETECTED!</b> 🚨

💎 <b>{symbol}</b>

━━━━━━━━━━━━━━━━━━━━
🐋 <b>WHALE SOLD</b>
━━━━━━━━━━━━━━━━━━━━
Whale: <code>{whale_addr[:16]}...</code>
Chain: <b>{chain.upper()}</b>

💰 Sold: <b>{sold_pct_abs:.1f}%</b> of position
🪙 Amount: <b>{sold_amount:,.0f}</b> tokens
📊 Remaining: <b>{current_balance:,.0f}</b> tokens

━━━━━━━━━━━━━━━━━━━━
{profit_emoji} <b>PERFORMANCE</b>
━━━━━━━━━━━━━━━━━━━━
Entry: ${initial_price:.8f}
Exit: ${current_price:.8f}
P&L: <b>{price_gain:+.1f}%</b>

Current MC: ${token_info['market_cap']:,.0f}

━━━━━━━━━━━━━━━━━━━━
⚠️ <b>{'PROFIT TAKING' if price_gain > 0 else 'STOP LOSS'}!</b>
Consider {'taking profits' if price_gain > 0 else 'cutting losses'} if holding.

🔗 <a href="{token_info['url']}">View Chart</a>
━━━━━━━━━━━━━━━━━━━━
"""
    
    send_telegram_alert(message)
    
    # Update whale performance
    update_whale_performance(whale_addr, price_gain)
    
    # Mark sell in tracked tokens
    if token_addr in bot_state.get('tracked_tokens', {}):
        if 'sells_detected' not in bot_state['tracked_tokens'][token_addr]:
            bot_state['tracked_tokens'][token_addr]['sells_detected'] = []
        
        bot_state['tracked_tokens'][token_addr]['sells_detected'].append({
            'whale': whale_addr,
            'sold_pct': sold_pct_abs,
            'profit_pct': price_gain,
            'timestamp': time.time()
        })
    
    print(f"  🚨 SELL ALERT: {symbol} by {whale_addr[:8]}... ({price_gain:+.1f}%)")

# ============================================================
# Thread Starters (kept for compatibility)
# ============================================================

def start_performance_tracker():
    """Placeholder - actual tracker is in main.py"""
    pass

def start_sell_detector():
    """Placeholder - actual detector is in main.py"""
    pass
