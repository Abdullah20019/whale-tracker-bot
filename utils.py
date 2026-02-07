"""
Utility functions for Whale Tracker Bot
Telegram, token checkers, filters, etc.
"""

import requests
import time
from config import *

# ============================================================
# TELEGRAM FUNCTIONS
# ============================================================

def send_telegram_message(message, chat_id=None):
    """Send message to Telegram"""
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
        # Send to both private and group
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": PRIVATE_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                success = True
        except:
            pass
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": GROUP_CHAT_ID,
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
    """Send alert and print confirmation"""
    success = send_telegram_message(message)
    if success:
        print("  ✅ Alert sent!")
    return success

# ============================================================
# TOKEN CHECKERS
# ============================================================

def get_solana_tokens(wallet_address):
    """Get Solana tokens for a wallet"""
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
        response = requests.post(HELIUS_RPC_URL, json=payload, timeout=10)
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
    """Get Base/EVM tokens for a wallet"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getTokenBalances",
        "params": [wallet_address, "erc20"]
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    
    try:
        response = requests.post(ALCHEMY_BASE_URL, json=payload, headers=headers, timeout=10)
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
    """Get token information from DexScreener"""
    try:
        url = f"{DEXSCREENER_API}/{token_address}"
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

# ============================================================
# FILTER FUNCTIONS
# ============================================================

def passes_filters(token_info, filters):
    """Check if token passes all filters"""
    if not token_info:
        return False, "No data"
    
    mc = token_info['market_cap']
    liq = token_info['liquidity']
    
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
# ADMIN CHECK
# ============================================================

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID
