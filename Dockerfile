FROM python:3.12-slim

WORKDIR /app
COPY . /app

# force the current hivemind-bus-client alpha rather than whatever a stale
# base layer might already have cached, since this bridge depends on the
# run_forever()-after-connect() fix and the current identity/handshake API
RUN pip install --no-cache-dir --upgrade "hivemind-bus-client>=1.0.13a1" \
    && pip install --no-cache-dir .

# credentials are passed as environment variables at `docker run` /
# compose time, never baked into the image. hivemind-discord-bridge's CLI
# takes flags, not env vars, so this shell form maps the conventional
# DISCORD_BOT_TOKEN / HIVEMIND_* names onto them at container start.
ENV HIVEMIND_HOST=ws://127.0.0.1 \
    HIVEMIND_PORT=5678 \
    HIVEMIND_SITE_ID=discord \
    HIVEMIND_LANG=en-us

ENTRYPOINT ["sh", "-c", "exec hivemind-discord-bridge \
  --token \"$DISCORD_BOT_TOKEN\" \
  --access-key \"$HIVEMIND_ACCESS_KEY\" \
  --password \"$HIVEMIND_PASSWORD\" \
  --host \"$HIVEMIND_HOST\" \
  --port \"$HIVEMIND_PORT\" \
  --site-id \"$HIVEMIND_SITE_ID\" \
  --lang \"$HIVEMIND_LANG\" \
  $EXTRA_ARGS"]
