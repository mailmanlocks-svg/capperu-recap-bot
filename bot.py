import discord
from discord.ext import commands
from discord import app_commands
import os
import httpx
import random
from datetime import datetime
import pytz

PACIFIC = pytz.timezone("America/Los_Angeles")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
SUPABASE_URL = "https://bdjpmsvvqrktusadhwif.supabase.co"
SUPABASE_KEY = "sb_publishable_yuGx5nIEZAn0YJxmYS690g_x9YjBRQz"
RECAP_CHANNEL_ID = 1425232193361547284
UPSELL_CHANNEL_ID = 1418679104638554274
GUILD_ID = 1418667113467351143
VIP_ROLE_ID = 1421280688866332675
MEMBER_ROLE_ID = 1418679919181041846

FREE_TRIAL_LINK = "https://www.winible.com/checkout/1580622055835980651?pid=1580622055848563564&c=WIN3"

WINIBLE_BOT_ID = 1169619508382683238
PROPS_CHANNEL_IDS = [
    1437289118517428356,
    1437289161911435324,
    1502417916258422905,
    1437289059860086875,
]
UPSELL_MESSAGES = [
    ("# 📬 +{units}u tonight. VIP ate again.", "If you're in the free chat you already saw the picks — but you didn't cash out on them. That's what VIP is for.\n\nGet your first 3 days on us and see what you've been missing 👇\n{link}"),
    ("# 🔥 We just went {record} on the night. +{units}u.", "Free chat gets the recap. VIP gets the plays before the game, the reasoning, and the results delivered straight to the phone.\n\nFirst 3 days free 👇\n{link}"),
    ("# 📈 +{units}u. Another night the VIP locked in.", "We post in VIP before the games tip. By the time the free chat sees it, we've already cashed.\n\nJump in free for 3 days 👇\n{link}"),
    ("# 🎯 {record} on the night. +{units}u banked.", "You're already here watching. You already know we can pick. The only difference between you and VIP right now is one click.\n\nFirst 3 days on us 👇\n{link}"),
    ("# 💰 +{units}u tonight. VIP is built different.", "Plays straight to your phone. Full card every day. Recaps every night. This is what VIP looks like.\n\nTry it free for 3 days 👇\n{link}"),
    ("# 🔒 {record} tonight. We stay locked in.", "The free chat sees the results. VIP sees the process, the plays, and the payouts in real time.\n\nGet your first 3 days free 👇\n{link}"),
    ("# 📬 {record} on the card. +{units}u added to the bag.", "Capper U VIP isn't just picks. It's a whole community of people cashing out together every night.\n\nFirst 3 days on us 👇\n{link}"),
    ("# 🏆 +{units}u. The numbers don't lie.", "You've been watching from the free side. You know what we do. Come cash out with us.\n\nFirst 3 days free, no excuses 👇\n{link}"),
    ("# 🎓 Capper U VIP went {record} tonight. +{units}u.", "We track every single pick. Every win, every loss, all on the record. This is what a data-driven approach looks like in action.\n\nTry VIP free for 3 days 👇\n{link}"),
    ("# 🔥 +{units}u tonight and it wasn't even close.", "VIP members got these plays straight to their phone before tip off. Free chat got the recap after.\n\nFlip the script. First 3 days on us 👇\n{link}"),
    ("# 📈 {record} on the night. We keep cooking.", "This isn't luck. It's process, research, and consistency. VIP is where you plug in and start cashing.\n\nGet 3 days free and find out 👇\n{link}"),
    ("# 💎 +{units}u. VIP stays winning.", "Free chat is great. VIP is where the money is made. You already know the difference.\n\nFirst 3 days on us 👇\n{link}"),
    ("# 🧹 {record} tonight. Clean sweep.", "Every single pick tonight cashed. VIP members felt it. Free chat saw it after the fact.\n\nDon't miss the next one. 3 days free 👇\n{link}"),
    ("# 🎯 We went {record} tonight. +{units}u on the card.", "Plays delivered to your phone before games start. Full transparency on every pick. That's what VIP looks like every single day.\n\nJump in free for 3 days 👇\n{link}"),
    ("# 📬 +{units}u added to the tracker tonight.", "You're already in the Discord. You're already watching. Might as well be cashing.\n\nFirst 3 days free 👇\n{link}"),
]
PARTNER_EMOJI = {"mailman": "📬", "spade": "♠️", "pan": "🐼"}
PARTNER_DISPLAY = {"mailman": "MAILMAN", "spade": "SPADE", "pan": "PAN"}

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot._skip_check = lambda x, y: False
tree = bot.tree

async def fetch_picks(target_date):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/picks",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={"date": f"eq.{target_date}", "select": "*"}
        )
        return resp.json()

def calc_stats(picks):
    wins = sum(1 for p in picks if p.get("result","").upper() == "W")
    losses = sum(1 for p in picks if p.get("result","").upper() == "L")
    units = sum(float(p.get("gain_loss") or 0) for p in picks)
    wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    return wins, losses, units, wr

def did_sweep(picks):
    if len(picks) < 3:
        return False
    results = [p.get("result","").upper() for p in picks]
    return all(r == "W" for r in results)
def build_recap(target_date, all_picks):
    partners = ["mailman", "spade", "pan"]
    partner_data = {}
    for p in partners:
        picks = [x for x in all_picks if x.get("partner","").lower() == p]
        picks = sorted(picks, key=lambda x: (0 if x.get("result","").upper() == "W" else 1))
        w, l, u, wr = calc_stats(picks)
        partner_data[p] = {"picks": picks, "w": w, "l": l, "units": u, "wr": wr, "sweep": did_sweep(picks)}
    sorted_partners = sorted(partner_data.items(), key=lambda x: x[1]["units"], reverse=True)
    seen_bets = set()
    unique_picks = []
    for p in all_picks:
        bet_key = p.get("bet","").strip().lower()
        if bet_key not in seen_bets:
            seen_bets.add(bet_key)
            unique_picks.append(p)
    total_w, total_l, total_u, total_wr = calc_stats(unique_picks)
    display_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%-m/%-d")
    lines = [f"🎓 **CAPPER UNIVERSITY RECAP — {display_date}** 📅", "━━━━━━━━━━━━━━━━━━━━━"]
    for name, d in sorted_partners:
        emoji = PARTNER_EMOJI.get(name, "")
        disp = PARTNER_DISPLAY.get(name, name.upper())
        u_str = f"+{d['units']:.2f}u" if d["units"] >= 0 else f"{d['units']:.2f}u"
        sweep_badge = " 🧹 SWEEP" if d["sweep"] else ""
        lines.append(f"{emoji} **{disp}** ({u_str} | {d['w']}-{d['l']}){sweep_badge}")
        if not d["picks"]:
            lines.append("— No plays today")
        else:
            for pick in d["picks"]:
                res_emoji = "✅" if pick.get("result","").upper() == "W" else ("❌" if pick.get("result","").upper() == "L" else "⏳")
                gl = float(pick.get("gain_loss") or 0)
                gl_str = f"+{gl:.2f}u" if gl >= 0 else f"{gl:.2f}u"
                lines.append(f"{res_emoji} {pick.get('bet','')} ({gl_str})")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
    u_total_str = f"+{total_u:.2f}u" if total_u >= 0 else f"{total_u:.2f}u"
    wr_emoji = "✅" if total_wr >= 50 else "❌"
    lines.append(f"📊 **CAPPER U TODAY:** {u_total_str} | {total_w}-{total_l} | {total_wr:.0f}% {wr_emoji}")
    lines.append(f"<@&{VIP_ROLE_ID}>")
    return "\n".join(lines), sorted_partners, total_u, total_w, total_l
def build_upsell(total_u, total_w, total_l):
    record = f"{total_w}-{total_l}"
    header_template, body_template = random.choice(UPSELL_MESSAGES)
    header = header_template.format(units=f"{total_u:.1f}", record=record)
    body = body_template.format(units=f"{total_u:.1f}", record=record, link=FREE_TRIAL_LINK)
    return f"{header}\n\n{body}\n\n<@&{MEMBER_ROLE_ID}>"

def is_winible_bot(message):
    if message.author.id == WINIBLE_BOT_ID:
        return True
    if message.author.name.lower() == "winible bot":
        return True
    if message.webhook_id is not None and "winible" in message.author.name.lower():
        return True
    return False

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot ready as {bot.user}")

@bot.event
async def on_message(message):
    if not is_winible_bot(message):
        await bot.process_commands(message)
        return
    if message.channel.id not in PROPS_CHANNEL_IDS:
        await bot.process_commands(message)
        return
    print(f"Winible post detected — author: {message.author.name} ({message.author.id}) webhook: {message.webhook_id}")
    lines = message.content.strip().split("\n")
    prop_line = lines[1].strip() if len(lines) >= 2 else lines[0].strip() if lines else None
    if not prop_line:
        await bot.process_commands(message)
        return
    await message.reply(f"**{prop_line}**\n\n<@&{VIP_ROLE_ID}>", mention_author=False)
    await bot.process_commands(message)

@tree.command(name="recap", description="Post today's picks recap", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(date_str="Date (YYYY-MM-DD). Leave blank for today.")
async def recap(interaction: discord.Interaction, date_str: str = None):
    await interaction.response.defer(ephemeral=True)
    target = date_str or datetime.now(PACIFIC).strftime("%Y-%m-%d")
    all_picks = await fetch_picks(target)
    if not all_picks:
        await interaction.followup.send(f"No picks found for {target}.", ephemeral=True)
        return
    recap_text, sorted_partners, total_u, total_w, total_l = build_recap(target, all_picks)
    recap_channel = bot.get_channel(RECAP_CHANNEL_ID)
    await recap_channel.send(recap_text)
    if total_u >= 1.0:
        upsell_text = build_upsell(total_u, total_w, total_l)
        upsell_channel = bot.get_channel(UPSELL_CHANNEL_ID)
        await upsell_channel.send(upsell_text)
        await interaction.followup.send(f"✅ Recap posted! Upsell fired (+{total_u:.2f}u threshold met).", ephemeral=True)
    else:
        await interaction.followup.send("✅ Recap posted. No upsell today (under +1u threshold).", ephemeral=True)

bot.run(DISCORD_TOKEN)
