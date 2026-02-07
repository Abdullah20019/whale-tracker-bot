"""
Configuration file for Whale Tracker Bot V4
Contains all settings, API keys, and constants
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API Keys
# ============================================================

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
BASESCAN_API_KEY = os.getenv('BASESCAN_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')

# ============================================================
# File Paths
# ============================================================

WHALE_LIST_FILE = 'whales_tiered_final.json'
BOT_STATE_FILE = 'bot_state.json'

# ============================================================
# Tier Configuration
# ============================================================

TIER_CONFIG = {
    1: {'interval': 30, 'name': 'Elite', 'emoji': '🔥'},
    2: {'interval': 180, 'name': 'Active', 'emoji': '⭐'},
    3: {'interval': 600, 'name': 'Semi-Active', 'emoji': '📊'},
    4: {'interval': 86400, 'name': 'Dormant', 'emoji': '💤'}
}

# ============================================================
# Filter Defaults
# ============================================================

DEFAULT_FILTERS = {
    'mc_min': 100000,
    'mc_max': 10000000,
    'liq_min': 10000,
    'vol_liq_max': 50,
    'buy_sell_max': 5,
    'min_age_hours': 1,
    'min_txns': 50
}

# ============================================================
# Blacklist Tokens
# ============================================================

BLACKLIST_TOKENS = {
    'So11111111111111111111111111111111111111112',  # SOL
    'EPjFWdd5AufqSSqewy3WZaNW1pF3Q8dTMm24FYzJR8o',  # USDC
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  # USDT
    '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',  # ETH
    'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',  # mSOL
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',  # BONK
    '0x4200000000000000000000000000000000000006',  # WETH (Base)
    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # USDC (Base)
    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',  # DAI (Base)
}

# ============================================================
# Price Alert Milestones (%)
# ============================================================

PRICE_MILESTONES = [10, 25, 50, 100, 200, 500, 1000]

# ============================================================
# Admin Configuration
# ============================================================

ADMIN_USER_ID = 1930784205

def is_admin(user_id):
    """Check if user is admin"""
    return user_id == ADMIN_USER_ID
