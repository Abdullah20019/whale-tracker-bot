"""
Bot state management
Handles saving/loading bot state
"""

import json
import time
from config import DEFAULT_FILTERS, BOT_STATE_FILE

# ============================================================
# BOT STATE
# ============================================================

bot_state = {
    'paused': False,
    'filters': DEFAULT_FILTERS.copy(),
    'alerts_sent': 0,
    'tokens_filtered': 0,
    'last_buys': [],
    'start_time': time.time(),
    'last_update_id': 0,
    'tracked_tokens': {},
    'multi_buys': {},
    'whale_performance': {},
    'whale_token_balances': {}
}

def save_bot_state():
    """Save bot state to file"""
    try:
        with open(BOT_STATE_FILE, 'w') as f:
            json.dump(bot_state, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving state: {e}")

def load_bot_state():
    """Load bot state from file"""
    global bot_state
    try:
        with open(BOT_STATE_FILE, 'r') as f:
            loaded = json.load(f)
            bot_state.update(loaded)
            bot_state['start_time'] = time.time()
            
            # Ensure all keys exist
            if 'tracked_tokens' not in bot_state:
                bot_state['tracked_tokens'] = {}
            if 'multi_buys' not in bot_state:
                bot_state['multi_buys'] = {}
            if 'whale_performance' not in bot_state:
                bot_state['whale_performance'] = {}
            if 'whale_token_balances' not in bot_state:
                bot_state['whale_token_balances'] = {}
    except FileNotFoundError:
        save_bot_state()
    except Exception as e:
        print(f"❌ Error loading state: {e}")
        save_bot_state()

def get_state():
    """Get current bot state"""
    return bot_state

def update_state(key, value):
    """Update specific state value"""
    bot_state[key] = value
    save_bot_state()
