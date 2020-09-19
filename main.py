import asyncio
import datetime
import json
import os
import pickle
from pathlib import Path

from discord.ext import commands

import objects

"""ShackHelper bot written by William Greenlee"""
__version__ = 'v1.0.3rc3'


def main():
    # Press the green button in the gutter to run the script.
    black_list_dir = Path('lts/blacklist')
    prefixes_list_dir = Path('lts/prefixes.json')
    reminder_file_dir = Path('lts/reminders')
    timer_loop = asyncio.get_event_loop()

    def read_blacklist() -> [str]:
        if os.path.exists(black_list_dir):
            with open(black_list_dir, 'rb') as f:
                return pickle.load(f)
        return []

    def save_b_list(black_list):
        with open(black_list_dir, 'wb') as f:
            pickle.dump(black_list, f)

    def read_prefixes() -> {str}:
        if os.path.exists(prefixes_list_dir):
            with open(prefixes_list_dir, 'r') as f:
                pf = json.load(f)
            return pf
        return {}

    def get_prefix(client_place_holder, message) -> str:
        prefix = '!'
        try:
            prefix = prefixes[str(message.guild.id)]
        except KeyError:
            set_prefix(message.guild, '!')
        return prefix

    def set_prefix(guild, prefix):
        if prefix is None:
            prefixes.pop(str(guild.id))
        prefixes[str(guild.id)] = prefix

    def save_prefixes(pfs: {str}):
        with open(prefixes_list_dir, 'w') as f:
            json.dump(pfs, f, indent=4)

    def read_reminders() -> [objects.Reminder]:
        if os.path.exists(reminder_file_dir):
            with open(reminder_file_dir, 'rb') as f:
                r_list = pickle.load(f)
            return r_list
        return []

    def save_reminders(reminders: [objects.Reminder]):
        with open(reminder_file_dir, 'wb') as f:
            pickle.dump(reminders, f)

    blacklist: [str] = read_blacklist()
    prefixes: {} = read_prefixes()
    active_reminders: [objects.Reminder] = []

    startup_reminders: [objects.Reminder] = read_reminders()
    client = commands.Bot(command_prefix=get_prefix)

    def reminder_ctest(array, reminder):
        for r in array:
            if reminder.__eq__(r):
                return True
        return False

    def activate_reminder(reminder) -> bool:
        """Activates a given reminder in a given context, returns False if failed.
            :param reminder Reminder to activate."""

        if not reminder_ctest(active_reminders, reminder):

            time_diff = int((reminder.start_time - datetime.datetime.now()).total_seconds())

            async def msg_coro():
                await asyncio.sleep(reminder.duration - time_diff)
                active_reminders.remove(reminder)
                await client.get_channel(reminder.channel_id).send(reminder.message)

            asyncio.run_coroutine_threadsafe(msg_coro(), timer_loop)
            active_reminders.append(reminder)
            return True
        else:
            return False

    @client.command(aliases=['desc'])
    async def description(ctx):
        await ctx.send('This bot mirrors all of the commands from the Taco Shack bot and lets you know when '
                       'timed events such as boosts and cooldowns have run out. Enjoy!\n'
                       '\n**Special Commands**:\n'
                       f'**{client.command_prefix(client, ctx.message)}customreminder/remind <reminder name> <h-m-s>** '
                       'creates a custom reminder with a name and set duration')

    @client.event
    async def on_ready():
        if not os.path.exists('lts/'):
            os.mkdir(Path('lts/').absolute())
        for reminder in startup_reminders:
            activate_reminder(reminder)
        print(f'Initialized ShackHelper {__version__}')

    @client.event
    async def on_guild_join(guild):
        set_prefix(guild, '!')

    @client.event
    async def on_guild_remove(guild):
        set_prefix(guild, None)

    @client.command(aliases=['s'])
    async def status(ctx):
        if client.is_ready():
            await ctx.send('Let\'s get cookin\'\n'
                           f'Use {client.command_prefix(client, ctx.message)}changeprefix to sync this bot\'s prefix '
                           'with the TacoShack bot.')
        else:
            await ctx.send('HOLD YOUR HORSES, I\'M GETTING SET UP')

    @client.command()
    async def ping(ctx):
        await ctx.send(f'Pong! Latency is {round(client.latency * 1000)}ms.')

    @client.command(aliases=['changeprefix'])
    async def change_prefix(ctx, *, args):
        set_prefix(ctx.guild, str(args))
        ctx.message.guild.me.nickname = f'[{args}]ShackHelper'
        await ctx.send(f'Changed prefix to ``{args}`` for this server.')

    @client.command(aliases=['optout', 'noreminders'])
    async def opt_out(ctx):
        if f'{ctx.message.author.id}' not in blacklist:
            blacklist.append(f'{ctx.message.author.id}')
        await ctx.send(f'<@{ctx.message.author.id}> will no longer receive reminders about cooldowns.')

    @client.command(aliases=['optin', 'reminders'])
    async def opt_in(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            blacklist.remove(f'{ctx.message.author.id}')
        await ctx.send(f'<@{ctx.message.author.id}> will now receive reminders about cooldowns.')

    @client.command(aliases=['w', 'cook'])
    async def work(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to work!',
                                    datetime.datetime.now(), 600)
        activate_reminder(reminder)

    @client.command(aliases=['t', 'tip'])
    async def tips(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to earn tips!',
                                    datetime.datetime.now(), 300)
        activate_reminder(reminder)

    @client.command(aliases=['ot'])
    async def overtime(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to do overtime!',
                                    datetime.datetime.now(), 1800)
        activate_reminder(reminder)

    @client.command()
    async def clean(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to clean your shack!',
                                    datetime.datetime.now(), 86400)
        activate_reminder(reminder)

    @client.command(aliases=['d'])
    async def daily(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to collect your daily reward!',
                                    datetime.datetime.now(), 86400)
        activate_reminder(reminder)

    @client.command(aliases=['reward'])
    async def claim(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> you\'re ready to vote!',
                                    datetime.datetime.now(), 43200)
        activate_reminder(reminder)

    @client.command()
    async def buy(ctx):
        if f'{ctx.message.author.id}' in blacklist:
            return

        arg: str = str(ctx.message.content).split(' ')[1].lower()
        duration = {
            'flipper': 28800,
            'karaoke': 21600,
            'music': 14400,
            'airplane': 86400,
            'chef': 14400
        }

        if arg in duration.keys():
            reminder = objects.Reminder(ctx.message.channel.id,
                                        f'<@{ctx.message.author.id}> your ``{arg}`` boost has run out!',
                                        datetime.datetime.now(), duration[arg])
            activate_reminder(reminder)

    @client.command(aliases=['customreminder', 'remind'])
    async def custom_reminder(ctx):
        args = str(ctx.message.content).split(' ')
        time = args[1].split('-')
        reminder = objects.Reminder(ctx.message.channel.id,
                                    f'<@{ctx.message.author.id}> ding dong reminder "{args[0]}" is activated',
                                    datetime.datetime.now(), time[0] * pow(60, 2) + time[1] * 60 + time[2])
        if not activate_reminder(reminder):
            await ctx.send(f'Custom reminder already exists for @<{ctx.message.author.id}>')

    @client.command(aliases=['shutdown'])
    async def stop(ctx):
        if ctx.message.author.id == 216302359435804684:
            save_reminders(active_reminders)
            save_b_list(blacklist)
            save_prefixes(prefixes)
            await ctx.send("Shutting Down, be right back!")
            timer_loop.stop()
            exit()

    client.run(str(input('Please input bot Token: ')))


if __name__ == '__main__':
    main()
