# HiveMind Discord Bridge

This bridges a Discord bot to a HiveMind node. A HiveMind bridge is a
satellite whose input and output are a chat platform instead of a
microphone: messages sent to the bot become HiveMind utterances, and the
hub's spoken replies are posted back into the same Discord channel.

## Creating a Discord bot, from scratch

If you have never created a Discord bot before, follow these steps in
order. None of them need any Discord server admin rights beyond the one
you own or a friendly server owner will give you.

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   and log in with your normal Discord account.
2. Click **New Application**, give it a name (this is the app's display
   name, not the bot's username yet), and accept the terms.
3. In the left sidebar, open **Bot**. Click **Add Bot** if it is not
   already there, and confirm.
4. Still on the **Bot** page, turn on **MESSAGE CONTENT INTENT** under
   "Privileged Gateway Intents". This bridge reads message text, and
   Discord hides message content from bots by default unless this is
   enabled. Save changes.
5. On the same page, click **Reset Token** (or **Copy** if a token is
   already shown) to get the bot token. It looks like a long string of
   letters, numbers, and dots. Treat it like a password: anyone who has
   it can make your bot post messages. Do not commit it to a repo or
   paste it into a public issue.
6. In the left sidebar, open **OAuth2 → URL Generator**. Under
   "Scopes", check **bot**. Under "Bot Permissions", check at least
   **Read Messages/View Channels** and **Send Messages** (add **Read
   Message History** too if you want it to see context). Copy the
   generated URL at the bottom of the page.
7. Paste that URL into your browser, pick the server you want to add
   the bot to, and confirm. You need "Manage Server" permission on that
   server (or ask whoever does to click through it for you).
8. The bot now appears offline in your server's member list. It comes
   online once you actually run this bridge with the token from step 5.

## Registering the bridge on the hub

Every HiveMind client needs credentials and, separately, permission to
send the message types it uses. On the machine running `hivemind-core`:

```bash
hivemind-core add-client
```

This prints an access key and password; pass them to the bridge as
`--access-key` / `--password` (or store them once with
`hivemind-client set-identity` and omit the flags).

A freshly added client is denied every message type by default. The
bridge needs at least:

```bash
hivemind-core allow-msg recognizer_loop:utterance <client_id>
hivemind-core allow-msg speak <client_id>
```

`<client_id>` is printed by `add-client` (and by `hivemind-core
list-clients` afterwards). Skipping this step is the single most common
reason a bridge "connects fine" but nothing ever seems to happen: the hub
silently drops every message the client sends until it is whitelisted.

## Running the bridge

```bash
pip install .
hivemind-discord-bridge \
  --token <your-bot-token> \
  --access-key <key> --password <password> \
  --host ws://127.0.0.1 --port 5678
```

By default the bridge answers direct messages and any text channel the
bot can read. Pass `--allowed-channel <channel_id>` (repeatable) to
restrict channel replies to specific channels; DMs are always accepted
regardless of this setting. `--token` also reads from the
`DISCORD_BOT_TOKEN` environment variable if the flag is omitted.

Useful flags:

- `--site-id`: this bridge's HiveMind site id. If you run more than one
  bridge (or more than one instance of this bridge) on the same host,
  give each a distinct site id — otherwise they collide over the same
  identity file and pinned peer keys.
- `--self-signed`: accept a self-signed TLS certificate on `wss://` hubs.
- `--lang`: the language tag attached to forwarded utterances (default
  `en-us`).

Run `hivemind-discord-bridge --help` for the full list.

## Docker

```bash
docker build -t hivemind-discord-bridge .
docker run --rm \
  -e DISCORD_BOT_TOKEN=... \
  -e HIVEMIND_ACCESS_KEY=... \
  -e HIVEMIND_PASSWORD=... \
  -e HIVEMIND_HOST=ws://hivemind-core \
  hivemind-discord-bridge
```

or via `docker-compose.yml` — copy it, fill in the environment section,
and `docker compose up`.

## What this bridge does, precisely

- Connects to Discord with `discord.py`'s async `Client` (gateway
  websocket); connects to the HiveMind hub with
  `hivemind_bus_client.HiveMessageBusClient`.
- Skips its own messages (so it can never talk to itself) and any
  message with no text content.
- Only forwards messages once the HiveMind handshake has completed —
  forwarding earlier would get the connection killed by the hub instead
  of just failing the one message.
- Forwards each remaining message as a `recognizer_loop:utterance` bus
  message, carrying the Discord channel id and author in the message
  context so the hub's `speak` reply can be routed back to the right
  channel.
- Posts `speak` replies (and a fixed fallback line on
  `hive.complete_intent_failure`) back into the originating channel or DM.

## Voice channels — not built, documented as a future direction

This bridge is text-only. Discord voice channels (joining a voice call,
transcribing speech, speaking replies with TTS) are a substantially
different integration — a persistent voice gateway connection, audio
decode/encode, and a wake-word or push-to-talk model — and are not
implemented here. If you want voice support, treat it as a separate
follow-on bridge built on `discord.py`'s voice client, not an extension
of this text bridge.

## Testing

```bash
pip install -e .[test]
pytest tests/
```

The test suite mocks both the `discord.Client` and the HiveMind
`HiveMessageBusClient`, so it runs without a live token or hub. It has
not been exercised against a real Discord bot or a real HiveMind hub —
that needs an actual bot token, which this repository does not have.
