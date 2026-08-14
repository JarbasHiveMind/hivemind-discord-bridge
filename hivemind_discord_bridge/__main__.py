"""CLI entry point for the HiveMind <-> Discord bridge.

HiveMind identity (key/password/host/port) defaults to the values stored
by ``hivemind-client set-identity``; flags override them.
"""
import click
from ovos_utils.log import LOG

from hivemind_discord_bridge import HiveMindDiscordBridge


def connect_discord_to_hivemind(token, key=None, password=None,
                                host=None, port=5678, self_signed=False,
                                lang="en-us", site_id="discord",
                                allowed_channels=None):
    bridge = HiveMindDiscordBridge(
        token=token, key=key, password=password, host=host, port=port,
        self_signed=self_signed, lang=lang, site_id=site_id,
        allowed_channels=allowed_channels,
    )
    bridge.start()
    return bridge


@click.command()
@click.option("--token", required=True, envvar="DISCORD_BOT_TOKEN",
             help="Discord bot token from the Developer Portal")
@click.option("--allowed-channel", "allowed_channels", multiple=True, type=int,
             help="Discord text channel id allowed to talk to the bridge "
                  "(repeatable); default: any channel the bot can read, plus DMs")
@click.option("--access-key", "key", default=None,
             help="HiveMind access key (default: from identity file)")
@click.option("--password", default=None,
             help="HiveMind password (default: from identity file)")
@click.option("--host", default=None,
             help="HiveMind host, e.g. ws://127.0.0.1 (default: from identity file)")
@click.option("--port", type=int, default=5678, help="HiveMind port (default: 5678)")
@click.option("--site-id", default="discord",
             help="this bridge's HiveMind site id (default: discord)")
@click.option("--self-signed", is_flag=True, help="accept self-signed SSL certificates")
@click.option("--lang", default="en-us", help="utterance language")
def main(token, allowed_channels, key, password, host, port, site_id,
        self_signed, lang):
    """Bridge a Discord bot to a HiveMind node."""
    if host and not host.startswith("ws://") and not host.startswith("wss://"):
        host = "ws://" + host

    LOG.info("bridge starting; press Ctrl-C to stop")
    try:
        connect_discord_to_hivemind(
            token=token, key=key, password=password,
            host=host, port=port, self_signed=self_signed,
            lang=lang, site_id=site_id,
            allowed_channels=list(allowed_channels) or None,
        )
    except KeyboardInterrupt:
        LOG.info("shutting down")


if __name__ == '__main__':
    main()
