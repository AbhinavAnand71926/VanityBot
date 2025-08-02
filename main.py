import os
import discord
from discord.ext import commands, tasks

# --- Load Environment Variables ---
TOKEN = os.getenv("DISCORD_TOKEN")  # Secure token from Render environment variables
ROLE_ID = 1396710984491728967  # Replace with your actual role ID
VANITY = "discord.gg/silvermart"  # Replace with your vanity link

# --- Intents ---
intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)


def has_vanity_in_status(member: discord.Member) -> bool:
    """Check if the member's custom status contains the vanity link."""
    for activity in member.activities:
        if isinstance(activity, discord.CustomActivity) and activity.name:
            if VANITY.lower() in activity.name.lower():
                return True
    return False


@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    check_vanity_roles.start()


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Check vanity changes immediately on member update."""
    await update_vanity_role(after)


async def update_vanity_role(member: discord.Member):
    """Assign or remove the vanity role based on current status."""
    guild = member.guild
    role = guild.get_role(ROLE_ID)
    if not role:
        return  # Role not found

    has_vanity = has_vanity_in_status(member)

    # Add role if vanity is present
    if has_vanity and role not in member.roles:
        try:
            await member.add_roles(role, reason="Vanity detected in status")
            print(f"✅ Added {role.name} to {member}")
        except discord.Forbidden:
            print(f"⚠️ Cannot assign role to {member} (permission issue)")

    # Remove role if vanity is gone
    elif not has_vanity and role in member.roles:
        try:
            await member.remove_roles(role, reason="Vanity removed from status")
            print(f"❌ Removed {role.name} from {member}")
        except discord.Forbidden:
            print(f"⚠️ Cannot remove role from {member} (permission issue)")


@tasks.loop(minutes=10)
async def check_vanity_roles():
    """Periodic check to ensure role accuracy in case Discord misses events."""
    for guild in bot.guilds:
        role = guild.get_role(ROLE_ID)
        if not role:
            continue

        for member in guild.members:
            if not member.bot:
                await update_vanity_role(member)


# --- Run the Bot ---
if __name__ == "__main__":
    if TOKEN is None:
        print("❌ ERROR: DISCORD_TOKEN environment variable not set!")
    else:
        bot.run(TOKEN)

