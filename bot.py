from discord.ext import tasks
import discord
import configparser

import watcher


DISCORD_TOKEN = None
ID = None
REFRESH = 60

class Watcher(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.check_events.start()

    async def on_ready(self):
        print(f"logged in as {self.user} (ID: {self.user.id})")

    @tasks.loop(seconds=REFRESH)
    async def check_events(self):
        channel = self.get_channel(ID)

        message = watcher.run()

        if len(message) > 0:
            print("new event(s) detected. sending...", message)
            await channel.send(message)

    @check_events.before_loop
    async def before_check_events(self):
        await self.wait_until_ready()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config')
    
    DISCORD_TOKEN = config['bot']['token']
    ID = int(config['bot']['channel'])

    client = Watcher()
    client.run(DISCORD_TOKEN)
