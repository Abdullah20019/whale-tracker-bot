"""
Utility functions for API calls and Telegram messaging
"""

import requests
import time
import os

# Get config values - handle missing TELEGRAM_GROUP_ID gracefully
try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    try:
        from config import TELEGRAM_GROUP_ID
    except ImportError:
        TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
except ImportError:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')

def send_telegram_message(message, chat_id=None, parse_mode=None):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Telegram bot token not set")
        return False
    
    if chat_id:
        target_chats = [chat_id]
    else:
        target_chats = []
        if TELEGRAM_CHAT_ID:
            target_chats.append(TELEGRAM_CHAT_ID)
        if TELEGRAM_GROUP_ID:
            target_chats.append(TELEGRAM_GROUP_ID)
    
    if not target_chats:
        print("❌ No Telegram chat IDs configured")
        return False
    
    success = False
    for target in target_chats:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {'chat_id': target, 'text': message}
            if parse_mode:
                payload['parse_mode'] = parse_mode
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Sent to {target}!")
                success = True
            else:
                print(f"   ⚠️ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return success

def get_token_info(token_address, chain='sol'):
    """
    Get token info for any chain (wrapper function)
    Calls chain-specific functions
    """
    if chain == 'sol':
        return get_solana_token_info(token_address)
    elif chain == 'base':
        return get_base_token_info(token_address)
    else:
        print(f"❌ Unsupported chain: {chain}")
        return None

def get_solana_token_info(token_address):
    """Get token info from Solana via DexScreener"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('pairs') and len(data['pairs']) > 0:
                pair = data['pairs'][0]
                return {
                    'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                    'name': pair.get('baseToken', {}).get('name', 'Unknown Token'),
                    'price': float(pair.get('priceUsd', 0)),
                    'mc': float(pair.get('fdv', 0)),
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                    'dex_url': pair.get('url', ''),
                    'pool_created': pair.get('pairCreatedAt', 0)
                }
        return None
    except Exception as e:
        print(f"Error fetching Solana token: {str(e)}")
        return None

def get_base_token_info(token_address):
    """Get token info from Base chain via DexScreener"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('pairs'):
                base_pairs = [p for p in data['pairs'] if p.get('chainId') == 'base']
                if base_pairs:
                    pair = base_pairs[0]
                    return {
                        'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                        'name': pair.get('baseToken', {}).get('name', 'Unknown Token'),
                        'price': float(pair.get('priceUsd', 0)),
                        'mc': float(pair.get('fdv', 0)),
                        'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                        'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                        'dex_url': pair.get('url', ''),
                        'pool_created': pair.get('pairCreatedAt', 0)
                    }
        return None
    except Exception as e:
        print(f"Error fetching Base token: {str(e)}")
        return None

def get_solana_tokens(wallet_address):
    """Get all tokens held by a Solana wallet"""
    try:
        url = f"https://public-api.solscan.io/account/tokens?account={wallet_address}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tokens = []
            if isinstance(data, list):
                for token in data:
                    tokens.append({
                        'mint': token.get('tokenAddress', ''),
                        'amount': float(token.get('tokenAmount', {}).get('uiAmount', 0)),
                        'decimals': int(token.get('tokenAmount', {}).get('decimals', 0))
                    })
            return tokens
        return []
    except Exception as e:
        print(f"Error fetching Solana wallet tokens: {str(e)}")
        return []

def get_base_tokens(wallet_address):
    """Get all tokens held by a Base wallet"""
    try:
        return []
    except Exception as e:
        print(f"Error fetching Base wallet tokens: {str(e)}")
        return []

def check_token_quality(token_info, filters):
    """Check if token passes quality filters"""
    if not token_info:
        return False, "No token info"
    
    mc = token_info.get('mc', 0)
    liquidity = token_info.get('liquidity', 0)
    volume_24h = token_info.get('volume_24h', 0)
    
    if mc < filters.get('mc_min', 0):
        return False, f"MC too low (${mc:,.0f})"
    if mc > filters.get('mc_max', float('inf')):
        return False, f"MC too high (${mc:,.0f})"
    if liquidity < filters.get('liq_min', 0):
        return False, f"Liquidity too low (${liquidity:,.0f})"
    
    if liquidity > 0:
        vol_liq_ratio = (volume_24h / liquidity) * 100
        if vol_liq_ratio > filters.get('vol_liq_max', 100):
            return False, f"Suspicious volume/liq ratio ({vol_liq_ratio:.1f}%)"
    
    return True, "Passed all filters"

def format_number(num):
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.1f}K"
    else:
        return f"${num:.2f}"

def get_wallet_transactions(wallet_address, chain='sol'):
    """Get recent transactions for a wallet"""
    return []

def get_token_holders(token_address, chain='sol'):
    """Get top holders of a token"""
    return []

def check_whale_balance(wallet_address, token_address, chain='sol'):
    """Check if wallet still holds a token"""
    if chain == 'sol':
        tokens = get_solana_tokens(wallet_address)
        for token in tokens:
            if token.get('mint', '').lower() == token_address.lower():
                return token.get('amount', 0)
    elif chain == 'base':
        tokens = get_base_tokens(wallet_address)
        pass
    return 0
