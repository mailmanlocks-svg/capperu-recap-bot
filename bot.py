import discord
from discord.ext import commands
from discord import app_commands
import os
import httpx
import random
from datetime import date


DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
SUPABASE_URL = "https://bdjpmsvvqrktusadhwif.supabase.co"
SUPABASE_KEY = "sb_publishable_yuGx5nIEZAn0YJxmYS690g_x9YjBRQz"
RECAP_CHANNEL_ID = 1425232193361547284
UPSELL_CHANNEL_ID = 1418679104638554274
GUILD_ID = 1418667113467351143


TIERS = {
    1: {"label": "1 WEEK ACCESS", "discount": "50% OFF", "code": "TIER1", "link": "https://dubclub.win/r/p/pri-8u2hm/?checkout=1&coupon=TIER1"},
    2: {"label": "1 MONTH ACCESS", "discount": "60% OFF", "code": "TIER2", "link": "https://dubclub.win/r/p/pri-psr7s/?checkout=1&coupon=TIER2"},
    3: {"label": "3 MONTHS ACCESS", "discount": "70% OFF", "code": "TIER3", "link": "https://dubclub.win/r/p/pri-bc75x/?checkout=1&coupon=TIER3"},
    4: {"label": "6 MONTHS ACCESS", "discount": "80% OFF", "code": "TIER4", "link": "https://dubclub.win/r/p/pri-8n2d8/?checkout=1&coupon=TIER4"},
    5: {"label": "1 YEAR ACCESS", "discount": "85% OFF", "code": "TIER5", "link": "https://dubclub.win/r/p/pri-7jaaz/?checkout=1&coupon=TIER5"},
}


HEADLINES = [
    "🚨🔥 CAPPER UNIVERSITY IS COOKING 🔥🚨",
    "🚨💰 WE STAY CASHING 💰🚨",
    "🚨🎯 LOCKED IN AND LOCKED ON 🎯🚨",
    "🚨📈 THE NUMBERS DON'T LIE 📈🚨",
    "🚨🏆 ANOTHER DAY, ANOTHER BAG 🏆🚨",
]
OPENERS = [
    "We called it. We cashed it. Simple. 💰",
    "Another day locked in, another day printing 🎯",
    "The results speak for themselves. 📊",
    "Day in, day out — we stay dialed. 🔒",
    "Running it back every single day 📈",
