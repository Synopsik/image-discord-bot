import logging
import os
from dotenv import load_dotenv


load_dotenv()
from discord.ext import commands
from util.database.database_service import (
    DatabaseService, insert_server, insert_user, insert_channel,
    insert_message, insert_discord_log
)

logger = logging.getLogger(__name__)

HOME_CHANNEL_ID = os.getenv("HOME_CHANNEL_ID")
class LoggingCog(commands.Cog, name="Logging"):
    def __init__(self, bot):
        self.bot = bot
        self.home_channel = self.bot.get_channel(HOME_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("Loaded Log Cog")
        
        # Initialize database with server/channel/user data when bot starts
        await self._initialize_database()

    async def _initialize_database(self):
        """Initialize database with current Discord entities"""
        await DatabaseService.initialize_discord_entities(self.bot)
            
    # ----------------------------------------------------------------------------
    # Guild Events (Server management)
    # ----------------------------------------------------------------------------
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Bot joins a new server"""
        await insert_server(
            server_id=guild.id,
            server_name=guild.name,
            region=str(guild.region) if hasattr(guild, 'region') else None
        )
        
        await insert_discord_log(
            level="INFO",
            event_type="discord_guild_join",
            message=f"Bot joined server: {guild.name}",
            server_id=guild.id
        )
        logger.info(f"Bot joined server: {guild.name}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Bot leaves a server"""
        await insert_discord_log(
            level="WARNING",
            event_type="discord_guild_leave",
            message=f"Bot left server: {guild.name}",
            server_id=guild.id
        )
        logger.warning(f"Bot left server: {guild.name}")

    # ----------------------------------------------------------------------------
    # Channel Events
    # ----------------------------------------------------------------------------
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """New channel created"""
        channel_type = 'text' if hasattr(channel, 'send') else 'voice'
        await insert_channel(
            channel_id=channel.id,
            server_id=channel.guild.id,
            channel_name=channel.name,
            channel_type=channel_type
        )
        
        await insert_discord_log(
            level="INFO",
            event_type="discord_channel_create",
            message=f"Channel created: #{channel.name}",
            server_id=channel.guild.id,
            channel_id=channel.id
        )
        logger.info(f"Channel created: #{channel.name}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Channel deleted"""
        await insert_discord_log(
            level="WARNING",
            event_type="discord_channel_delete",
            message=f"Channel deleted: #{channel.name}",
            server_id=channel.guild.id,
            channel_id=channel.id
        )
        logger.warning(f"Channel deleted: #{channel.name}")

    # ----------------------------------------------------------------------------
    # Messages
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author == self.bot.user:
            # Ensure user exists in database
            await insert_user(
                user_id=message.author.id,
                username=message.author.name,
                display_name=message.author.display_name
            )
            
            # Ensure server exists in database FIRST (for non-DM messages)
            if message.guild:
                await insert_server(
                    server_id=message.guild.id,
                    server_name=message.guild.name,
                    region=str(message.guild.region) if hasattr(message.guild, 'region') else None
                )
            
            # Now ensure channel exists in database
            await insert_channel(
                channel_id=message.channel.id,
                server_id=message.guild.id if message.guild else None,
                channel_name=message.channel.name if hasattr(message.channel, 'name') else None,
                channel_type='DM' if not message.guild else 'text'
            )
            
            # Insert the message
            await insert_message(
                channel_id=message.channel.id,
                user_id=message.author.id,
                content=message.content,
                discord_message_id=message.id
            )
            
            # Log the event
            await insert_discord_log(
                level="INFO",
                event_type="discord_message",
                message=f"{message.author.name}: {message.content[:100]}{'...' if len(message.content) > 100 else ''}",
                server_id=message.guild.id if message.guild else None,
                user_id=message.author.id,
                channel_id=message.channel.id
            )
            
            logger.info(f"{message.author}: {message.content}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await insert_discord_log(
            level="WARNING",
            event_type="discord_message_delete",
            message=f"{message.author.name} deleted message: {message.content[:100]}{'...' if len(message.content) > 100 else ''}",
            server_id=message.guild.id if message.guild else None,
            user_id=message.author.id,
            channel_id=message.channel.id
        )
        logger.warning(f"{message.author.name} has deleted a message: {message.content}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await insert_discord_log(
            level="INFO",
            event_type="discord_message_edit",
            message=f"{before.author.name} edited message: {before.content[:50]}{'...' if len(before.content) > 50 else ''} -> {after.content[:50]}{'...' if len(after.content) > 50 else ''}",
            server_id=after.guild.id if after.guild else None,
            user_id=after.author.id,
            channel_id=after.channel.id
        )
        
        # msg = {"content": f"Before: {before.content}\nAfter: {after.content}"}
        # await send_message(after.channel, message=msg)
        logger.warning(f"{before.author.name} has edited a message: {before.content} -> {after.content}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await insert_discord_log(
            level="DEBUG",
            event_type="discord_reaction_add",
            message=f"{user.name} added reaction {reaction.emoji}",
            server_id=reaction.message.guild.id if reaction.message.guild else None,
            user_id=user.id,
            channel_id=reaction.message.channel.id
        )
        logger.debug(f"{user.name} has added a reaction to a message: {reaction.emoji}")

    # ----------------------------------------------------------------------------
    # Members
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Insert/update user in database
        await insert_user(
            user_id=member.id,
            username=member.name,
            display_name=member.display_name
        )
        
        # Log the event
        await insert_discord_log(
            level="INFO",
            event_type="discord_member_join",
            message=f"{member.name} joined the server",
            server_id=member.guild.id,
            user_id=member.id
        )
        
        message = {"content": f"{member} just joined the server!"}
        # await send_message(self.home_channel, message)
        logger.debug(f"{member.name} just joined the server!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await insert_discord_log(
            level="WARNING",
            event_type="discord_member_leave",
            message=f"{member.name} left the server",
            server_id=member.guild.id,
            user_id=member.id
        )
        logger.warning(f"{member.name} just left the server!")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Update user information
        await insert_user(
            user_id=after.id,
            username=after.name,
            display_name=after.display_name
        )
        
        await insert_discord_log(
            level="INFO",
            event_type="discord_member_update",
            message=f"{before.name} changed profile (nickname: {before.display_name} -> {after.display_name})",
            server_id=after.guild.id,
            user_id=after.id
        )
        logger.warning(f"{before.name} has changed their nickname to {after.name}")

    # ----------------------------------------------------------------------------
    # Commands
    # ----------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await insert_discord_log(
            level="INFO",
            event_type="discord_command",
            message=f"Command completed: {ctx.prefix}{ctx.command}",
            server_id=ctx.guild.id if ctx.guild else None,
            user_id=ctx.author.id,
            channel_id=ctx.channel.id
        )
        logger.debug(f"Command completed: {ctx.prefix}{ctx.command}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await insert_discord_log(
            level="ERROR",
            event_type="discord_command_error",
            message=f"Command error: {ctx.prefix}{ctx.command} - {str(error)}",
            server_id=ctx.guild.id if ctx.guild else None,
            user_id=ctx.author.id,
            channel_id=ctx.channel.id,
            ctx=ctx
        )
        logger.error(f"Command error: {ctx.prefix}{error}")

    # ----------------------------------------------------------------------------
    # Utility Commands for Database Queries
    # ----------------------------------------------------------------------------
    
    @commands.command(name="db_stats")
    @commands.has_permissions(administrator=True)
    async def database_stats(self, ctx):
        """Get database statistics for the current server"""
        from util.database.setup_database import get_server_stats
        
        try:
            stats = await get_server_stats(ctx.guild.id)
            if stats:
                embed = discord.Embed(title=f"Database Stats for {stats['server_name']}", color=0x00ff00)
                embed.add_field(name="Channels", value=stats['channel_count'], inline=True)
                embed.add_field(name="Users", value=stats['user_count'], inline=True)
                embed.add_field(name="Messages", value=stats['message_count'], inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("No statistics found for this server.")
        except Exception as e:
            await ctx.send(f"Error retrieving stats: {e}")

    @commands.command(name="recent_logs")
    @commands.has_permissions(administrator=True)
    async def recent_logs(self, ctx, limit: int = 10):
        """Get recent Discord logs for this server"""
        from util.database.setup_database import get_discord_logs
        
        try:
            logs = await get_discord_logs(limit=limit, server_id=ctx.guild.id)
            if logs:
                embed = discord.Embed(title=f"Recent Discord Logs ({limit})", color=0x0099ff)
                for log in logs[:5]:  # Show first 5 in embed
                    embed.add_field(
                        name=f"{log['level']} - {log['event_type']}",
                        value=f"{log['message'][:100]}{'...' if len(log['message']) > 100 else ''}",
                        inline=False
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send("No recent logs found for this server.")
        except Exception as e:
            await ctx.send(f"Error retrieving logs: {e}")


async def setup(bot):
    await bot.add_cog(LoggingCog(bot))

async def teardown(bot):
    pass