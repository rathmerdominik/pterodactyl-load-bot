from discord.ext import tasks
from discord import Message, TextChannel, NotFound
from yaml.loader import SafeLoader
from time import sleep
import discord
import dotenv
import pydactyl
import os
import yaml
import humanize
import math
import datetime as dt

dotenv.load_dotenv()

discord_client = discord.Client()

ptero_client = pydactyl.PterodactylClient(
    os.environ["PTERO_SERVER"], os.environ["PTERO_API_KEY"]
)


@tasks.loop(seconds=20)
async def update_message():
    await discord_client.wait_until_ready()
    server_id: str = discord_client.server_id
    message: Message = discord_client.message
    await message.edit(content=await get_formatted_current_load(server_id))
    print(f"Updated Server Info {dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")


@discord_client.event
async def on_ready():
    server_id, message_id = await get_server_id()
    print("2gbPteroLoadData Bot ready and logged in as {0.user}".format(discord_client))
    channel: TextChannel = discord_client.get_channel(
        int(os.environ["DISCORD_CHANNEL_ID"])
    )
    message: Message = await get_editable_message(channel, server_id, message_id)
    discord_client.server_id: str = server_id
    discord_client.message: Message = message
    update_message.start()


async def get_editable_message(
    channel: TextChannel, server_id: str, message_id: int | None
) -> Message:

    try:
        if not message_id:
            message: Message = await channel.send(
                await get_formatted_current_load(server_id)
            )
            with open("config.yaml", "r+") as f:
                config = yaml.load(f, Loader=SafeLoader)
                config["messageId"] = message.id
                f.seek(0)
                yaml.dump(config, f)
                f.truncate()
        else:
            message: Message = await channel.fetch_message(message_id)
    except NotFound:
        await get_editable_message(channel, None)
    return message


async def get_formatted_current_load(server_id: str) -> str:

    server: dict = ptero_client.client.servers.get_server(server_id)
    server_util: dict = ptero_client.client.servers.get_server_utilization(server_id)
    server_max: dict = server["limits"]
    server_resources: dict = server_util["resources"]

    status = "Server status: {0}".format(server_util["current_state"])
    memory = "RAM usage: {0} from {1}".format(
        humanize.naturalsize(server_resources["memory_bytes"], True),
        humanize.naturalsize(server_max["memory"] * 1000 * 1000),
    )
    disk = "Disk usage: {0} from {1}".format(
        humanize.naturalsize(server_resources["disk_bytes"], True),
        humanize.naturalsize(server_max["disk"] * 1000 * 1000),
    )
    cpu = await get_formatted_cpu_load(
        server_resources["cpu_absolute"], server_max["cpu"]
    )
    network_up = "Network UP: {0} for current uptime".format(
        humanize.naturalsize(server_resources["network_rx_bytes"], True),
    )
    network_down = "Network DOWN: {0} for current uptime".format(
        humanize.naturalsize(server_resources["network_tx_bytes"], True),
    )
    uptime = "Server has been consistently up for {0}".format(
        humanize.precisedelta(
            dt.timedelta(milliseconds=server_resources["uptime"]),
            format="%0.0f",
            suppress=["seconds"],
        ),
    )

    return "\n".join([status, uptime, cpu, memory, disk, network_up, network_down])


async def get_formatted_cpu_load(cpu_load: float, cpu_max: int) -> str:
    threads: int = math.floor(int(cpu_load) / 100)
    percentage = int(cpu_load) % 100
    if cpu_max == 0:
        cpu_max = "all available CPU threads"
    elif cpu_max % 100 == 0:
        cpu_max = "{0} CPU Thread/s".format(int(cpu_max / 100))
    else:
        cpu_max = "{0} CPU Thread/s and {1}% on another CPU Thread".format(
            math.floor(int(cpu_max) / 100), int(cpu_load) % 100
        )
    return "CPU usage: {0} CPU Thread/s and {1}% on another CPU Thread from {2}".format(
        threads, percentage, cpu_max
    )


async def setup_server_id(config: dict) -> str:
    servers = ptero_client.client.servers.list_servers()
    server_identifiers: dict = {}
    for server in servers:
        for item in server.data:
            id: int = item["attributes"]["internal_id"]
            name: str = item["attributes"]["name"]
            identifier: str = item["attributes"]["identifier"]
            print(
                f"{id} : {name}",
            )
            server_identifiers[id] = identifier
    server_id: int = int(input("Please enter Server ID to monitor load for > "))
    config["serverId"] = server_identifiers[server_id]
    with open("config.yaml", "w") as f:
        yaml.dump(config, f)
    return config["serverId"]


async def get_server_id() -> tuple[str, int]:
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=SafeLoader)

    server_id: str | None = config["serverId"]
    message_id: int | None = config["messageId"]

    if not config["serverId"]:
        server_id: int = await setup_server_id(config)
        await get_server_id()
    return server_id, message_id


if __name__ == "__main__":
    # TODO Write tests
    # TODO Proper comments
    try:
        discord_client.run(os.environ["DISCORD_TOKEN"])
    except KeyboardInterrupt:
        print("Bot shutting down")
