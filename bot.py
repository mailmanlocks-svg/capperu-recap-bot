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
]
GIVEBACKS = [
    "To celebrate and give back to everyone tapped in —",
    "In the spirit of the run we're on, we're dropping a deal —",
    "Because the bag deserves to be shared —",
    "To reward the ones who've been locked in with us —",
    "We're feeling generous after today —",
]
SCARCITY = [
    "⏰ LIMITED TIME — don't sleep on this.",
    "⚠️ Limited spots. No re-releases. No second chances.",
    "🔐 Lock in before this disappears.",
    "🚨 First come, first served. No exceptions.",
    "⏳ This deal won't last — act now.",
]
CLOSERS = [
    "If you've been on the fence, this is your sign. 👀",
    "You already saw the numbers. You know what to do. 💎",
    "The longer you wait, the more you miss. 😤",
    "Stop watching from the sidelines. 🎯",
    "Your move. 🤝",
]

PARTNER_EMOJI = {"mailman": "📬", "spade": "♠️", "pan": "🐼"}
PARTNER_DISPLAY = {"mailman": "MAILMAN", "spade": "SPADE", "pan": "PAN"}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
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

def get_tier(group_units, sweepers):
    if len(sweepers) >= 2:
        return 5
    if len(sweepers) == 1:
        return 4
    if group_units >= 3:
        return 3
    if group_units >= 2:
        return 2
    if group_units >= 1:
        return 1
    return None

def build_recap(target_date, all_picks):
    partners = ["mailman", "spade", "pan"]
    partner_data = {}
    for p in partners:
        picks = [x for x in all_picks if x.get("partner","").lower() == p]
        w, l, u, wr = calc_stats(picks)
        partner_data[p] = {"picks": picks, "w": w, "l": l, "units": u, "wr": wr, "sweep": did_sweep(picks)}
    sorted_partners = sorted(partner_data.items(), key=lambda x: x[1]["units"], reverse=True)
    total_w = sum(d["w"] for _, d in sorted_partners)
    total_l = sum(d["l"] for _, d in sorted_partners)
    total_u = sum(d["units"] for _, d in sorted_partners)
    total_wr = (total_w / (total_w + total_l) * 100) if (total_w + total_l) > 0 else 0
    display_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%-m/%-d")
    lines = [f"🎓 **CAPPER UNIVERSITY RECAP — {display_date}** 📅", "━━━━━━━━━━━━━━━━━━━━━"]
    for name, d in sorted_partners:
        emoji = PARTNER_EMOJI.get(name, "")
        disp = PARTNER_DISPLAY.get(name, name.upper())
        u_str = f"+{d['units']:.2f}u" if d["units"] >= 0 else f"{d['units']:.2f}u"
        sweep_badge = " 🧹 SWEEP" if d["sweep"] else ""
        lines.append(f"{emoji} **{disp}** ({u_str} | {d['w']}-{d['l']}){sweep_badge}")
        for pick in d["picks"]:
            res_emoji = "✅" if pick.get("result","").upper() == "W" else ("❌" if pick.get("result","").upper() == "L" else "⏳")
            gl = float(pick.get("gain_loss") or 0)
            gl_str = f"+{gl:.2f}u" if gl >= 0 else f"{gl:.2f}u"
            lines.append(f"{res_emoji} {pick.get('bet','')} ({gl_str})")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
    u_total_str = f"+{total_u:.2f}u" if total_u >= 0 else f"{total_u:.2f}u"
    wr_emoji = "✅" if total_wr >= 50 else "❌"
    lines.append(f"📊 **CAPPER U TODAY:** {u_total_str} | {total_w}-{total_l} | {total_wr:.0f}% {wr_emoji}")
    lines.append("<@&1421280688866332675>")
    return "\n".join(lines), sorted_partners, total_u

def build_upsell(tier_num, sorted_partners, total_u, total_w, total_l, sweepers):
    tier = TIERS[tier_num]
    headline = random.choice(HEADLINES)
    opener = random.choice(OPENERS)
    giveback = random.choice(GIVEBACKS)
    scarcity = random.choice(SCARCITY)
    closer = random.choice(CLOSERS)
    u_str = f"+{total_u:.2f}u" if total_u >= 0 else f"{total_u:.2f}u"
    lines = [headline, "", opener, "", f"We went **{total_w}-{total_l}** today and pocketed **{u_str}** 👇", ""]
    for name, d in sorted_partners:
        if not d["picks"]: continue
        emoji = PARTNER_EMOJI.get(name, "")
        disp = PARTNER_DISPLAY.get(name, name.upper())
        du = f"+{d['units']:.2f}u" if d["units"] >= 0 else f"{d['units']:.2f}u"
        sweep_tag = " 🧹 SWEEP" if d["sweep"] else ""
        lines.append(f"{emoji} **{disp}**{sweep_tag} — {du} | {d['w']}-{d['l']} | {d['wr']:.0f}% WR")
    if sweepers:
        lines.append("")
        sweep_names = " & ".join([PARTNER_DISPLAY.get(s, s.upper()) for s in sweepers])
        lines.append(f"🧹 **{sweep_names} SWEPT** — hit every single pick today!")
    lines += ["", giveback, "We're dropping a limited deal to celebrate 👇", "", f"💎 **{tier['discount']} — {tier['label']}** 💎", "", scarcity, f"🎟️ Code: `{tier['code']}`", f"👉 {tier['link']}", ""]
    lines.append("<@&1418679919181041846>")
    lines.append(closer)
    return "\n".join(lines)

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot ready as {bot.user}")

@tree.command(name="recap", description="Post today's picks recap", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(date_str="Date (YYYY-MM-DD). Leave blank for today.")
async def recap(interaction: discord.Interaction, date_str: str = None):
    await interaction.response.defer(ephemeral=True)
    target = date_str or datetime.now(PACIFIC).strftime("%Y-%m-%d")
    all_picks = await fetch_picks(target)
    if not all_picks:
        await interaction.followup.send(f"No picks found for {target}.", ephemeral=True)
        return
    recap_text, sorted_partners, total_u = build_recap(target, all_picks)
    recap_channel = bot.get_channel(RECAP_CHANNEL_ID)
    await recap_channel.send(recap_text)
    total_w = sum(d["w"] for _, d in sorted_partners)
    total_l = sum(d["l"] for _, d in sorted_partners)
    sweepers = [name for name, d in sorted_partners if d["sweep"]]
    tier_num = get_tier(total_u, sweepers)
    if tier_num:
        upsell_text = build_upsell(tier_num, sorted_partners, total_u, total_w, total_l, sweepers)
        upsell_channel = bot.get_channel(UPSELL_CHANNEL_ID)
        await upsell_channel.send(upsell_text)
        await interaction.followup.send(f"✅ Recap posted! Tier {tier_num} upsell fired.", ephemeral=True)
    else:
        await interaction.followup.send("✅ Recap posted. No upsell today.", ephemeral=True)

bot.run(DISCORD_TOKEN)
