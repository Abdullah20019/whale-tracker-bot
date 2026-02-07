"""
Utility functions for API calls and Telegram messaging
"""

import requests
import time
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_GROUP_ID

def send_telegram_message(message, chat_id=None, parse_mode=None):
    """
    Send message to Telegram
    If chat_id not specified, sends to both private and group
    """
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Telegram bot token not set")
        return False

    # Determine target chats
    if chat_id:
        # Send to specific chat only
        target_chats = [chat_id]
    else:
        # Send to both private and group
        target_chats = []
        if TELEGRAM_CHAT_ID:
            target_chats.append(TELEGRAM_CHAT_ID)
        if TELEGRAM_GROUP_ID:
            target_chats.append(TELEGRAM_GROUP_ID)

    if not target_chats:
        print("❌ No Telegram chat IDs configured")
        return False

    # Send to each target
    success = False
    for target in target_chats:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

            payload = {
                'chat_id': target,
                'text': message
            }

            if parse_mode:
                payload['parse_mode'] = parse_mode

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ Response sent to {target}!")
                success = True
            else:
                print(f"   ⚠️ Failed to send to {target}: {response.status_code}")
                print(f"   Response: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ Error sending to {target}: {str(e)}")

    return success

def get_solana_token_info(token_address):
    """
    Get token info from Solana
    """
    try:
        # Using DexScreener API
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
        print(f"Error fetching Solana token info: {str(e)}")
        return None

def get_base_token_info(token_address):
    """
    Get token info from Base chain
    """
    try:
        # Using DexScreener API
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('pairs') and len(data['pairs']) > 0:
                # Filter for Base chain pairs
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
        print(f"Error fetching Base token info: {str(e)}")
        return None

def check_token_quality(token_info, filters):
    """
    Check if token passes quality filters
    """
    if not token_info:
        return False, "No token info"

    mc = token_info.get('mc', 0)
    liquidity = token_info.get('liquidity', 0)
    volume_24h = token_info.get('volume_24h', 0)

    # Market cap check
    if mc < filters.get('mc_min', 0):
        return False, f"MC too low (${mc:,.0f})"
    if mc > filters.get('mc_max', float('inf')):
        return False, f"MC too high (${mc:,.0f})"

    # Liquidity check
    if liquidity < filters.get('liq_min', 0):
        return False, f"Liquidity too low (${liquidity:,.0f})"

    # Volume/Liquidity ratio
    if liquidity > 0:
        vol_liq_ratio = (volume_24h / liquidity) * 100
        if vol_liq_ratio > filters.get('vol_liq_max', 100):
            return False, f"Suspicious volume/liq ratio ({vol_liq_ratio:.1f}%)"

    return True, "Passed all filters"

def format_number(num):
    """
    Format large numbers with K, M, B suffixes
    """
    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.1f}K"
    else:
        return f"${num:.2f}"

def get_wallet_transactions(wallet_address, chain='sol'):
    """
    Get recent transactions for a wallet
    This is a placeholder - implement with actual blockchain API
    """
    # In production, use Helius (Solana) or Alchemy (Base)
    # For now, return empty list
    return []
