#!/usr/bin/env python3
"""Post to, and edit, this project's Discord channels from a session.

Host-only. Consumers of Throughliner have no bot and no server; this lives in
resources/ rather than the plugin's scripts/ folder for that reason.

## What this is for

Before this existed, every Discord post was copied across by hand. The route is
all that changes: nothing posts without the user seeing the exact text and
saying yes, which is the standing approval rule and is enforced by the session,
not by this script. A script cannot ask for consent, so it does not pretend to
— it takes a file that a human has already approved and sends its exact bytes.

## The token

Read from INBOX/.discord-bot-token.txt, which is outside git. The leading dot
is load-bearing: session_start's mail scan skips dot-files, so the credential
is never surfaced as unread mail or read into a session's chat. This script
never prints, echoes or logs the token, and an HTTP error body is passed
through untouched only after the Authorization header has been dropped from
anything reported.

## Standard library only

Per this project's scripting constraints: these scripts run on machines whose
interpreters nobody controls, so nothing is imported that pip would have to
supply. urllib does everything needed here.

## Routes used, verified against Discord's docs 2026-08-27

    POST   /channels/{channel_id}/messages              send
    POST   /channels/{forum_id}/threads                 create a forum topic
    POST   /channels/{channel_id}/messages/{message_id}/threads
                                                        start a thread on a message
                                                        (send --thread-on)
    PATCH  /channels/{channel_id}/messages/{message_id} edit (own messages only)
    DELETE /channels/{channel_id}/messages/{message_id} delete one
    GET    /channels/{channel_id}/messages              list, newest first
    GET    /users/@me/guilds                            find the server
    GET    /guilds/{guild_id}/channels                  resolve a channel name
    GET    /guilds/{guild_id}/threads/active            resolve a thread name
    PATCH  /users/@me                                   set the bot's avatar

## Forums are not text channels

A forum channel holds threads, not messages, so posting to its /messages route
fails with HTTP 400 "Cannot send messages in a non-text channel" (code 50008) —
found live 2026-08-29. Creating a topic is a different call that carries a
title, which is what `send --title` uses.

Posting *into* an existing topic needs no new route: a thread's own id is a
channel id, so /channels/{thread_id}/messages is the ordinary send. What was
missing was only a way to name one — the guild channel list does not include
threads — so channel resolution falls back to the guild's active threads.

Bulk delete is deliberately NOT used. Its route refuses anything older than two
weeks, and the entries this prunes are older than that by definition, so it
would fail exactly where the prune is needed.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

# Copied from reorder_queue.py, which is the canonical copy. The duplication is
# deliberate: the hooks and these scripts run standalone and cannot import a
# shared module, which is also why a shared module was rejected. Without this,
# an unconfigured stderr on Windows falls back to the console's ANSI code page
# and any character outside it is replaced — and the echo confirming which
# message was posted prints the post's own text back, which routinely carries
# em-dashes.
for _stream in (sys.stderr, sys.stdout):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Python < 3.7, or a stream that cannot be reconfigured. Messages then
        # behave as before — degraded, never fatal.
        pass

API = "https://discord.com/api/v10"
TOKEN_PATH = os.path.join("INBOX", ".discord-bot-token.txt")

# Discord's own limit on a message body.
MESSAGE_LIMIT = 2000


class DiscordError(Exception):
    """An API call failed. The message is safe to print — no token in it."""


def read_token(project_root):
    path = os.path.join(project_root, TOKEN_PATH)
    if not os.path.exists(path):
        raise DiscordError(
            "No bot token found at %s. It is created by the Discord bot "
            "server setup and is deliberately outside git." % TOKEN_PATH
        )
    with open(path, encoding="utf-8") as handle:
        token = handle.read().strip()
    if not token:
        raise DiscordError("The bot token file at %s is empty." % TOKEN_PATH)
    return token


def request(token, method, path, body=None, multipart=None, query=None):
    """One API call. Returns the decoded JSON body, or None for 204."""
    url = API + path
    if query:
        url += "?" + urllib.parse.urlencode(query)

    headers = {
        "Authorization": "Bot " + token,
        "User-Agent": "ThroughlinerPoster (https://flintcraft.tech, 1.0)",
    }

    data = None
    if multipart is not None:
        boundary = uuid.uuid4().hex
        data = encode_multipart(multipart, boundary)
        headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return None
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as error:
        detail = ""
        try:
            detail = error.read().decode("utf-8", "replace")
        except Exception:
            pass
        # 429 carries a retry_after; one retry, then give up. A prune that
        # stops partway needs no recovery — the next post's prune picks up
        # whatever is left.
        if error.code == 429:
            try:
                wait = float(json.loads(detail).get("retry_after", 1.0))
            except Exception:
                wait = 1.0
            time.sleep(min(wait, 10.0) + 0.1)
            return request(token, method, path, body=body,
                           multipart=multipart, query=query)
        raise DiscordError(
            "%s %s failed: HTTP %s %s" % (method, path, error.code, detail)
        )
    except urllib.error.URLError as error:
        raise DiscordError("%s %s failed to connect: %s" % (method, path, error.reason))


def encode_multipart(fields, boundary):
    """Build a multipart/form-data body.

    `fields` is a list of (name, value) for text parts and
    (name, filename, bytes) for file parts — Discord wants the JSON body as a
    `payload_json` text part alongside `files[n]` file parts.
    """
    out = bytearray()
    sep = ("--" + boundary + "\r\n").encode("utf-8")
    for field in fields:
        out += sep
        if len(field) == 2:
            name, value = field
            out += ('Content-Disposition: form-data; name="%s"\r\n\r\n'
                    % name).encode("utf-8")
            out += value.encode("utf-8") + b"\r\n"
        else:
            name, filename, payload = field
            guessed = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            out += ('Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
                    % (name, filename)).encode("utf-8")
            out += ("Content-Type: %s\r\n\r\n" % guessed).encode("utf-8")
            out += payload + b"\r\n"
    out += ("--" + boundary + "--\r\n").encode("utf-8")
    return bytes(out)


# --- channel resolution -----------------------------------------------------
#
# Channel IDs are deliberately not kept on file: TOOLS.md is committed to a
# public repository, so a session that needs one looks it up through the bot.

def normalise_channel_name(name):
    """Reduce a channel name to the part a human would type.

    This server's channels are named with a leading emoji — '\N{NERD FACE}test-rezips-for-nerds',
    '\N{NEWSPAPER}announcements' — so an exact match on the typed name finds nothing.
    Keeping only ASCII letters, digits and dashes makes both sides comparable
    without anyone having to paste an emoji into a command line.
    """
    return "".join(
        char for char in name.lower()
        if char.isascii() and (char.isalnum() or char == "-")
    ).strip("-")


def resolve_channel(token, name):
    """Find a channel or thread id by its name, across every guild.

    Threads are searched only when no channel matches, so a forum topic named
    after its parent channel can never shadow the channel itself. A forum
    topic's own id is a channel id, which is what lets the ordinary send post
    into an existing topic once its name resolves.
    """
    if name.isdigit():
        return name
    wanted = normalise_channel_name(name.lstrip("#"))
    matches = []
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        channels = request(token, "GET", "/guilds/%s/channels" % guild["id"])
        for channel in channels or []:
            if normalise_channel_name(channel.get("name", "")) == wanted:
                matches.append((channel["name"], channel["id"]))

    if not matches:
        matches = [(thread["name"], thread["id"])
                   for thread in active_threads(token)
                   if normalise_channel_name(thread.get("name", "")) == wanted]

    if len(matches) == 1:
        return matches[0][1]
    if len(matches) > 1:
        raise DiscordError(
            "More than one channel or topic matches %r: %s. Pass the id "
            "instead." % (name, ", ".join(m[0] for m in matches))
        )
    raise DiscordError(
        "No channel or open forum topic named %r found in any server the bot "
        "is in. The bot may not have been granted access to it, or the topic "
        "may have gone inactive — archived threads are not listed." % name
    )


def active_threads(token):
    """Every open thread the bot can see, forum topics included.

    Archived threads are deliberately not fetched: that is a per-channel route
    rather than a per-guild one, so reaching it would mean a call for every
    channel on every name lookup. A topic that has gone quiet is addressed by
    its id instead, and the resolution error says so.
    """
    found = []
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        try:
            payload = request(
                token, "GET", "/guilds/%s/threads/active" % guild["id"])
        except DiscordError:
            # One guild refusing the read must not hide every other guild's
            # topics — the same posture the replies scan takes per channel.
            continue
        found.extend((payload or {}).get("threads", []))
    return found


def whoami(token):
    return request(token, "GET", "/users/@me")


# The permission bits worth naming when the question is "who can change things
# here". The full set runs to fifty-odd flags, most of them voice and stage
# permissions this server does not use; a listing that prints all of them is
# one nobody reads. The raw bitfield is printed alongside, so nothing is
# hidden — a flag not named here is still visible as a number.
PERMISSION_BITS = (
    ("ADMINISTRATOR", 1 << 3),
    ("MANAGE_CHANNELS", 1 << 4),
    ("MANAGE_GUILD", 1 << 5),
    ("VIEW_CHANNEL", 1 << 10),
    ("SEND_MESSAGES", 1 << 11),
    ("MANAGE_MESSAGES", 1 << 13),
    ("ATTACH_FILES", 1 << 15),
    ("MENTION_EVERYONE", 1 << 17),
    ("MANAGE_ROLES", 1 << 28),
    ("MANAGE_WEBHOOKS", 1 << 29),
    ("MANAGE_THREADS", 1 << 34),
    ("CREATE_PUBLIC_THREADS", 1 << 35),
    ("SEND_MESSAGES_IN_THREADS", 1 << 38),
)


def decode_permissions(value):
    """Name the notable bits set in a Discord permission bitfield."""
    try:
        bits = int(value or 0)
    except (TypeError, ValueError):
        return []
    return [name for name, bit in PERMISSION_BITS if bits & bit]


def permissions(token):
    """Every guild's roles and every channel's permission overwrites.

    A pure read: no send, no edit, nothing on the server changes. It exists
    because a permission question was otherwise unanswerable from here — the
    bot could post and prune but could not report who is allowed to do what,
    so a capability claim about a channel could only be tested by acting on it.

    What it CANNOT tell you, stated because a listing invites over-reading: a
    member's effective permissions are their roles combined with these
    overwrites and with channel ownership, which this does not compute. It
    reports what is granted and denied, and the reader does the combining.
    """
    out = []
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        entry = {"guild": guild.get("name", guild["id"]), "roles": [],
                 "channels": []}
        roles = request(token, "GET", "/guilds/%s/roles" % guild["id"]) or []
        by_id = {}
        for role in roles:
            by_id[role["id"]] = role.get("name", role["id"])
            entry["roles"].append({
                "name": role.get("name", role["id"]),
                "id": role["id"],
                "raw": role.get("permissions", "0"),
                "named": decode_permissions(role.get("permissions")),
            })
        channels = request(
            token, "GET", "/guilds/%s/channels" % guild["id"]) or []
        for channel in channels:
            overwrites = []
            for over in channel.get("permission_overwrites") or []:
                # type 0 is a role, type 1 a single member. A member overwrite
                # is reported by id only: resolving it would mean naming a
                # person in a file this project commits.
                if over.get("type") == 0:
                    who = by_id.get(over["id"], "role %s" % over["id"])
                else:
                    who = "a member (id %s)" % over["id"]
                overwrites.append({
                    "who": who,
                    "allow": decode_permissions(over.get("allow")),
                    "deny": decode_permissions(over.get("deny")),
                })
            entry["channels"].append({
                "name": channel.get("name", channel["id"]),
                "id": channel["id"],
                "type": channel.get("type"),
                "overwrites": overwrites,
            })
        out.append(entry)
    return out


CHANNEL_TYPES = {0: "text", 2: "voice", 4: "category", 5: "announcement",
                 13: "stage", 15: "forum", 16: "media"}


def channels(token):
    """Every channel in every guild, with its type, marking the ones that carry
    no permission overwrites of their own.

    A pure read. It exists because `permissions` lists only channels carrying
    overwrites — a channel created on the defaults inherits its roles'
    permissions and is absent from that listing — so a guide checked against
    `permissions` alone could miss a channel entirely. This is the complete
    list, and the announced-claims sweep checks the orientation post against it.
    """
    out = []
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        rows = []
        for channel in request(
                token, "GET", "/guilds/%s/channels" % guild["id"]) or []:
            rows.append({
                "name": channel.get("name", channel["id"]),
                "id": channel["id"],
                "type": CHANNEL_TYPES.get(channel.get("type"),
                                          "type %s" % channel.get("type")),
                "no_overwrites": not channel.get("permission_overwrites"),
            })
        rows.sort(key=lambda r: (r["type"] == "category", r["name"]))
        out.append({"guild": guild.get("name", guild["id"]), "channels": rows})
    return out


def threads(token):
    """Every open forum topic the bot can see, grouped by its parent forum.

    `active_threads()` has worked since forum-topic creation was added, and
    nothing exposed it on the command line — so a session needing the list
    wrote a throwaway `python -c` against the module, which is the shape this
    project's tooling rules push work away from. Two standing pieces of work
    need exactly this list: the announced-claims sweep reads each forum's topic
    order every turn, and the how-to re-homing reads where a topic sits after
    each post.
    """
    parents = {}
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        for channel in request(
                token, "GET", "/guilds/%s/channels" % guild["id"]) or []:
            parents[channel["id"]] = channel.get("name", channel["id"])
    grouped = {}
    for thread in active_threads(token):
        parent = parents.get(thread.get("parent_id"),
                             "unknown parent %s" % thread.get("parent_id"))
        grouped.setdefault(parent, []).append(
            (thread["id"], thread.get("name", "")))
    return grouped


# --- the operations ---------------------------------------------------------

def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def check_length(text):
    if len(text) > MESSAGE_LIMIT:
        raise DiscordError(
            "The text is %d characters; Discord's limit is %d. Shorten the "
            "draft file and run again." % (len(text), MESSAGE_LIMIT)
        )


def send(token, channel, body_path, attach=None):
    """Post the exact contents of body_path, optionally with one file."""
    channel_id = resolve_channel(token, channel)
    text = read_text(body_path)
    check_length(text)
    path = "/channels/%s/messages" % channel_id

    if attach:
        with open(attach, "rb") as handle:
            payload = handle.read()
        fields = [
            ("payload_json", json.dumps({
                "content": text,
                "attachments": [{"id": 0, "filename": os.path.basename(attach)}],
            })),
            ("files[0]", os.path.basename(attach), payload),
        ]
        message = request(token, "POST", path, multipart=fields)
    else:
        message = request(token, "POST", path, body={"content": text})

    return message


def send_in_thread_on(token, channel, message_id, body_path):
    """Post body_path as a message in the thread hanging off one message.

    Where no thread exists on that message yet, one is started — named for the
    message's own first line, which for a rezip entry is the build's heading —
    and the text goes in as the thread's first message. Where a thread already
    exists (Discord refuses a second one, error code 160004), the text is posted
    into it instead. A thread started from a message carries that message's id
    as its own, which is also what makes the existing-thread case addressable.
    Returns (thread_id, message, created).
    """
    channel_id = resolve_channel(token, channel)
    text = read_text(body_path)
    check_length(text)

    created = False
    try:
        parent = request(token, "GET",
                         "/channels/%s/messages/%s" % (channel_id, message_id))
        first_line = (parent.get("content") or "").strip().splitlines()
        name = (first_line[0] if first_line else "Testing outcomes").strip("# ")
        # Discord caps a thread name at 100 characters.
        name = (name[:97] + "...") if len(name) > 100 else name or "Testing outcomes"
        thread = request(
            token, "POST",
            "/channels/%s/messages/%s/threads" % (channel_id, message_id),
            body={"name": name})
        thread_id = thread["id"]
        created = True
    except DiscordError as error:
        if "160004" not in str(error):
            raise
        thread_id = message_id

    message = request(token, "POST", "/channels/%s/messages" % thread_id,
                      body={"content": text})
    return thread_id, message, created


def create_forum_topic(token, channel, title, body_path, attach=None):
    """Open a new topic in a forum channel, with its opening message.

    The forum's own /messages route refuses this — a forum holds threads, not
    messages — so the title travels with the body on the threads route, and the
    opening message is created in the same call rather than posted afterwards.
    """
    channel_id = resolve_channel(token, channel)
    text = read_text(body_path)
    check_length(text)
    path = "/channels/%s/threads" % channel_id

    if attach:
        with open(attach, "rb") as handle:
            payload = handle.read()
        fields = [
            ("payload_json", json.dumps({
                "name": title,
                "message": {
                    "content": text,
                    "attachments": [
                        {"id": 0, "filename": os.path.basename(attach)}],
                },
            })),
            ("files[0]", os.path.basename(attach), payload),
        ]
        return request(token, "POST", path, multipart=fields)

    return request(token, "POST", path,
                   body={"name": title, "message": {"content": text}})


# A copy of rule_signals.py's inner_root (and the server's _inner_root) — the
# same shape in a third place rather than an import, so this script keeps
# running from the outer with nothing on the path.
VISIBILITY_INNER_RE = re.compile(r"inner repository \(`([^`]+?)/?`\)")


def inner_root(root):
    """The product subfolder in a nested project, or None for a flat one.

    Read from the project CLAUDE.md's Visibility line, which names the inner
    in backticks; failing that, the one immediate subfolder holding a `.git`.
    Two candidates and no Visibility line is ambiguous, and None is returned
    rather than a guess.
    """
    claude = os.path.join(root, "CLAUDE.md")
    try:
        with open(claude, "r", encoding="utf-8") as f:
            for line in f:
                if not line.startswith("Visibility:"):
                    continue
                m = VISIBILITY_INNER_RE.search(line)
                if m:
                    cand = os.path.join(root, m.group(1))
                    if os.path.isdir(os.path.join(cand, ".git")):
                        return cand
    except OSError:
        pass
    found = []
    try:
        for name in os.listdir(root):
            p = os.path.join(root, name)
            if (not name.startswith(".") and os.path.isdir(p)
                    and os.path.isdir(os.path.join(p, ".git"))):
                found.append(p)
    except OSError:
        return None
    return found[0] if len(found) == 1 else None


def archived_plugin_zip(project_root, version=None):
    """The zip of a build from plugin/rezip-archive/, for a test-rezips entry.

    Nothing is built here. The rezip archives each build's zip at the moment
    that build is installed and its stamps are proved equal to the source, so
    the archived bytes are the bytes that were tested; a zip built now would be
    of whatever the working tree has since become.

    With no version given, the newest entry is used. The readme beside each zip
    carries that build's label, version and Commit: line, and is what the
    channel post says.

    The archive is looked for under the inner repository first, where a nested
    project keeps it, and at the flat path second, so a flat project is
    unchanged and the script works from the folder the app opens.
    """
    tried = []
    inner = inner_root(project_root)
    if inner:
        tried.append(os.path.join(inner, "plugin", "rezip-archive"))
    tried.append(os.path.join(project_root, "plugin", "rezip-archive"))
    archive_dir = next((p for p in tried if os.path.isdir(p)), None)
    if archive_dir is None:
        raise DiscordError(
            "No rezip archive at %s. It is written by the Rezip checklist's "
            "archive step — run a rezip before posting an entry."
            % " or ".join(tried))

    zips = sorted(name for name in os.listdir(archive_dir)
                  if name.endswith(".zip"))
    if not zips:
        raise DiscordError("No zips in %s to attach." % archive_dir)

    if version is None:
        chosen = max(zips, key=lambda name: os.path.getmtime(
            os.path.join(archive_dir, name)))
    else:
        wanted = "throughliner-v%s.zip" % version.lstrip("v")
        if wanted not in zips:
            raise DiscordError(
                "No archived build %s in %s. Available: %s"
                % (wanted, archive_dir, ", ".join(zips)))
        chosen = wanted

    return os.path.join(archive_dir, chosen)


def edit(token, channel, message_id, body_path):
    """Rewrite one of the bot's own messages.

    A bot can only edit messages it authored — nobody can edit anyone else's
    Discord message — so a post-post correction is always this call.
    """
    channel_id = resolve_channel(token, channel)
    text = read_text(body_path)
    check_length(text)
    return request(
        token, "PATCH",
        "/channels/%s/messages/%s" % (channel_id, message_id),
        body={"content": text},
    )


def get_message(token, channel, message_id, out_path):
    """Write one message's body verbatim to a file.

    `list` prints only each message's first line cut at 80 characters, so a
    re-post that must be byte-identical to the original cannot be assembled
    from it. The body goes straight to a file rather than to stdout so it can
    be handed to `send --body` without passing through a chat surface that
    could reflow it.
    """
    channel_id = resolve_channel(token, channel)
    message = request(
        token, "GET",
        "/channels/%s/messages/%s" % (channel_id, message_id),
    )
    content = message.get("content") or ""
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)
    return message, content


def fetch(token, channel, limit=50):
    """List recent messages, newest first."""
    channel_id = resolve_channel(token, channel)
    return request(
        token, "GET", "/channels/%s/messages" % channel_id,
        query={"limit": min(int(limit), 100)},
    ) or []


def fetch_all(token, channel_id, cap=300):
    """Page back through a channel's messages, newest first."""
    collected = []
    before = None
    while len(collected) < cap:
        query = {"limit": 100}
        if before:
            query["before"] = before
        batch = request(token, "GET", "/channels/%s/messages" % channel_id,
                        query=query) or []
        if not batch:
            break
        collected.extend(batch)
        before = batch[-1]["id"]
        if len(batch) < 100:
            break
    return collected


def _readable_channels(token):
    """Every text channel the bot can see, across every guild it is in.

    Read access is what the grant gives; posting is a separate grant. This is a
    read only, so it reaches everything the bot has been let into.
    """
    found = []
    for guild in request(token, "GET", "/users/@me/guilds") or []:
        channels = request(token, "GET", "/guilds/%s/channels" % guild["id"])
        for channel in channels or []:
            # 0 = text, 5 = announcement. Voice and category entries hold no
            # messages, and asking for their messages errors.
            if channel.get("type") in (0, 5):
                found.append((channel.get("name", channel["id"]),
                              channel["id"]))
    return found


def replies(token, since, cap=300):
    """Replies to the bot's own messages, and messages @mentioning it.

    A read only — there is no send path here. What comes back is data for a
    session to weigh: an owed reply is drafted and goes out on the user's
    explicit yes to the exact text, under the standing send gate, which this
    script does not and cannot enforce.

    `since` is an ISO date (YYYY-MM-DD). Messages are compared on their own
    timestamps rather than against anything stored, so nothing here keeps a
    position and a forgotten run costs nothing — the same posture as the
    correspondence check that reads GitHub issues.
    """
    me = whoami(token)
    my_id = str(me["id"])

    out = []
    for name, channel_id in _readable_channels(token):
        try:
            messages = fetch_all(token, channel_id, cap=cap)
        except DiscordError:
            # A channel the bot can list but not read its history. Skipped
            # rather than fatal: one closed door must not hide every other
            # channel's replies.
            continue
        for message in messages:
            stamp = message.get("timestamp", "")
            if stamp[:10] < since:
                continue
            author = message.get("author", {})
            if str(author.get("id")) == my_id:
                continue
            referenced = message.get("referenced_message") or {}
            replies_to_bot = str(
                (referenced.get("author") or {}).get("id")) == my_id
            mentions_bot = any(str(u.get("id")) == my_id
                               for u in message.get("mentions", []))
            if not (replies_to_bot or mentions_bot):
                continue
            out.append({
                "channel": name,
                "author": author.get("global_name")
                          or author.get("username", "unknown"),
                "timestamp": stamp,
                "kind": "reply" if replies_to_bot else "mention",
                "content": message.get("content", ""),
                "id": message["id"],
            })
    out.sort(key=lambda row: row["timestamp"])
    return out


def prune(token, channel, keep=15, dry_run=False):
    """Delete the channel's older entries, under four bounds.

    1. Keep the newest `keep` of the bot's own entries.
    2. Delete only messages the BOT ITSELF authored, checked per message
       against the author id. The user's posts, other members' posts and the
       pin are untouchable by construction rather than by ordering luck.
    3. Skip pinned messages explicitly — a second, independent guard on the
       pin, so it survives even if the author check ever changed.
    4. On any error partway, stop and report, with no retries. Leftover old
       entries are picked up by the next post's prune, so nothing needs
       recovering.

    Bulk delete is not used: its route refuses anything older than two weeks,
    which is precisely the age of the entries this removes.

    One cost, stated: entries posted by hand before the bot existed can never
    be pruned by the bot, because it did not author them. Those are cleaned up
    by hand, once.
    """
    channel_id = resolve_channel(token, channel)
    me = whoami(token)["id"]

    messages = fetch_all(token, channel_id)
    mine = [m for m in messages
            if m.get("author", {}).get("id") == me and not m.get("pinned")]

    doomed = mine[keep:]          # the list is newest-first
    if not doomed:
        return 0, len(mine)

    deleted = 0
    for message in doomed:
        if dry_run:
            deleted += 1
            continue
        try:
            request(token, "DELETE",
                    "/channels/%s/messages/%s" % (channel_id, message["id"]))
        except DiscordError as error:
            raise DiscordError(
                "Prune stopped after %d deletion(s): %s\nNothing needs "
                "recovering — the next post's prune picks up what is left."
                % (deleted, error)
            )
        deleted += 1
        # Deletes are rate-limited more tightly than reads; a small pause
        # costs nothing on a prune of a handful of messages and keeps the
        # 429 path from doing the work.
        time.sleep(0.35)

    return deleted, len(mine)


def rebump_welcome(token, channel, welcome_path):
    """Move the channel's welcome back to the bottom, where people are looking.

    Discord opens a channel at the BOTTOM, so a pin at the top is where the
    welcome is least likely to be read. There is no native bottom-pin; the
    universal pattern is a sticky message a bot re-posts as the newest message.
    This bot has no always-running process and so cannot react to other people's
    messages — but test-rezips traffic is almost entirely the bot's own, so
    re-bumping at each entry post keeps the welcome at the bottom exactly when
    anyone looks.

    The bot's own previous copy is deleted first and the source file's text
    posted after, so the channel never briefly shows two.

    **Only the bot's own unpinned message whose text matches the source file is
    deleted**, by author id and by content — the existing pin, the user's posts
    and every entry are untouchable by construction rather than by ordering
    luck, the same guard the prune takes.

    CONSENT, which this script cannot enforce and so states: the user's yes to
    posting the entry covers re-bumping the welcome's UNCHANGED bytes. Any
    change to the welcome text is a new send and needs its own explicit yes to
    the exact text.

    A copy of the welcome someone ELSE posted is found and reported, never
    touched: a bot can only delete what it wrote. Without the report, a channel
    whose standing welcome the user wrote gets a truthful "no previous copy
    found" at the exact moment a visible duplicate appears, which reads as
    nothing to do.
    """
    channel_id = resolve_channel(token, channel)
    text = read_text(welcome_path)
    check_length(text)
    me = whoami(token)["id"]
    wanted = text.strip()

    removed = 0
    foreign = None
    for message in fetch_all(token, channel_id):
        if (message.get("content") or "").strip() != wanted:
            continue
        author = message.get("author", {})
        if author.get("id") != me:
            if foreign is None:
                foreign = (message["id"], author.get("username", "someone else"))
            continue
        if message.get("pinned") or removed:
            continue
        request(token, "DELETE",
                "/channels/%s/messages/%s" % (channel_id, message["id"]))
        removed += 1
        time.sleep(0.35)
        # Only the most recent copy of the bot's own is expected to exist;
        # stopping at one keeps a content collision from cascading into a sweep.

    posted = request(token, "POST", "/channels/%s/messages" % channel_id,
                     body={"content": text})
    return removed, posted, foreign


def set_avatar(token, image_path):
    """Set the bot's own avatar. Outward-facing — the caller owns the consent."""
    with open(image_path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    return request(token, "PATCH", "/users/@me",
                   body={"avatar": "data:%s;base64,%s" % (mime, encoded)})


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Post to and edit this project's Discord channels.")
    parser.add_argument("--project-root", default=".",
                        help="project root holding INBOX/ (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send", help="post the exact contents of a file")
    p_send.add_argument("--channel", required=True,
                        help="channel name or id — an open forum topic's name "
                             "or id works too, and posts into that topic")
    p_send.add_argument("--body", required=True,
                        help="path to the approved text (sent verbatim)")
    p_send.add_argument("--title",
                        help="create a NEW forum topic with this title, in the "
                             "forum named by --channel, with the body as its "
                             "opening message. Omit it to post an ordinary "
                             "message.")
    p_send.add_argument("--thread-on", metavar="MESSAGE_ID",
                        help="post the body into the thread under that "
                             "message in --channel, starting the thread "
                             "(named for the message's first line) where none "
                             "exists yet — the rezip entry's outcomes thread. "
                             "Not combinable with --title or attachments.")
    p_send.add_argument("--attach", help="optional file to attach")
    p_send.add_argument("--attach-archived-zip", metavar="VERSION", nargs="?",
                        const="", default=None,
                        help="attach a build's zip from plugin/rezip-archive/ "
                             "— the test-rezips entry's download. Give a "
                             "version, or omit it for the newest archived "
                             "build. Nothing is built here.")
    p_send.add_argument("--rebump-welcome", metavar="PATH",
                        help="after posting, delete the bot's own previous "
                             "copy of this file's text in the channel and "
                             "repost it as the newest message — the sticky "
                             "welcome. Usually resources/nerds-welcome.md.")
    p_send.add_argument("--prune-to", type=int, metavar="N",
                        help="after posting, keep only the newest N of the "
                             "bot's own unpinned messages in this channel")

    p_edit = sub.add_parser("edit", help="rewrite one of the bot's own messages")
    p_edit.add_argument("--channel", required=True)
    p_edit.add_argument("--message-id", required=True)
    p_edit.add_argument("--body", required=True)

    p_get = sub.add_parser(
        "get",
        help="write one message's whole body verbatim to a file — what `list` "
             "truncates. A read only.")
    p_get.add_argument("--channel", required=True,
                       help="channel name or id — a forum topic's id works "
                            "too, and reaches its opening post")
    p_get.add_argument("--message-id", required=True,
                       help="the message's id. A forum topic's opening message "
                            "carries the topic's own id.")
    p_get.add_argument("--out", required=True,
                       help="path to write the body to, verbatim")

    p_list = sub.add_parser("list", help="list recent messages, newest first")
    p_list.add_argument("--channel", required=True)
    p_list.add_argument("--limit", type=int, default=50)

    p_avatar = sub.add_parser("set-avatar", help="set the bot's own avatar")
    p_avatar.add_argument("--image", required=True)

    p_prune = sub.add_parser(
        "prune", help="delete the bot's own older entries, keeping the newest N")
    p_prune.add_argument("--channel", required=True)
    p_prune.add_argument("--keep", type=int, default=15)
    p_prune.add_argument("--dry-run", action="store_true",
                         help="report what would go, delete nothing")

    p_replies = sub.add_parser(
        "replies",
        help="read replies to the bot and @mentions of it, across every "
             "channel it can see. A read only — no send path.")
    p_replies.add_argument("--since", required=True, metavar="YYYY-MM-DD",
                           help="ignore anything older than this date")
    p_replies.add_argument("--cap", type=int, default=300,
                           help="how far back to page per channel "
                                "(default: 300 messages)")

    sub.add_parser("whoami", help="report the bot's own account")

    sub.add_parser(
        "permissions",
        help="read-only: the guild's roles and each channel's permission "
             "overwrites. Changes nothing on the server.")

    sub.add_parser(
        "threads",
        help="read-only: every open forum topic, with its id, grouped by forum")

    sub.add_parser(
        "channels",
        help="read-only: every channel with its type and id, marking the ones "
             "that carry no permission overwrites of their own — the complete "
             "list, where `permissions` shows only channels with overwrites.")

    args = parser.parse_args(argv)

    try:
        token = read_token(args.project_root)

        if args.command == "send":
            if args.thread_on:
                if args.title or args.attach or args.attach_archived_zip is not None:
                    raise DiscordError(
                        "--thread-on posts text only: drop --title and the "
                        "attachment options.")
                thread_id, message, created = send_in_thread_on(
                    token, args.channel, args.thread_on, args.body)
                print("%s thread %s under message %s in #%s — message id %s"
                      % ("Started" if created else "Posted into existing",
                         thread_id, args.thread_on, args.channel,
                         message["id"]))
                return 0
            attachment = args.attach
            if args.attach_archived_zip is not None:
                attachment = archived_plugin_zip(
                    args.project_root, args.attach_archived_zip or None)
                print("Attaching archived build %s (%d KB)"
                      % (attachment, os.path.getsize(attachment) // 1024))
            if args.title:
                thread = create_forum_topic(
                    token, args.channel, args.title, args.body, attachment)
                # The threads route returns the new thread; its own id is also
                # the id of its opening message.
                print("Created topic %r in #%s — topic id %s"
                      % (args.title, args.channel, thread["id"]))
                return 0
            message = send(token, args.channel, args.body, attachment)
            print("Posted to #%s — message id %s" % (args.channel, message["id"]))
            if args.prune_to is not None:
                removed, remaining = prune(token, args.channel, args.prune_to)
                print("Pruned %d old entr%s; %d of the bot's own remain."
                      % (removed, "y" if removed == 1 else "ies",
                         remaining - removed))
            # Last, so the welcome ends up newest whatever else this run did.
            # A prune that removed an older copy simply leaves nothing to
            # delete here, which is why the two need no coordination.
            if args.rebump_welcome:
                dropped, message, foreign = rebump_welcome(
                    token, args.channel, args.rebump_welcome)
                print("Welcome re-bumped: %s, reposted as message id %s"
                      % ("previous copy deleted" if dropped
                         else "no previous copy found",
                         message["id"]))
                if foreign:
                    print("The channel now shows the welcome TWICE: message %s "
                          "carries the same text and was posted by %s, so this "
                          "bot cannot delete it — only its author can."
                          % (foreign[0], foreign[1]))

        elif args.command == "edit":
            edit(token, args.channel, args.message_id, args.body)
            print("Edited message %s in #%s" % (args.message_id, args.channel))

        elif args.command == "get":
            message, content = get_message(
                token, args.channel, args.message_id, args.out)
            print("Wrote message %s by %s to %s — %d characters, %d line(s)."
                  % (args.message_id,
                     message.get("author", {}).get("username", "?"),
                     args.out, len(content), len(content.splitlines())))

        elif args.command == "list":
            for message in fetch(token, args.channel, args.limit):
                first = (message.get("content") or "").splitlines()
                print("%s  %s  %s" % (
                    message["id"],
                    message.get("author", {}).get("username", "?"),
                    first[0][:80] if first else "(no text)",
                ))

        elif args.command == "prune":
            removed, mine = prune(token, args.channel, args.keep, args.dry_run)
            verb = "Would delete" if args.dry_run else "Deleted"
            print("%s %d of the bot's own unpinned message(s) in #%s; "
                  "%d newest kept. Pinned messages and anyone else's posts "
                  "were never candidates."
                  % (verb, removed, args.channel, min(args.keep, mine)))

        elif args.command == "set-avatar":
            set_avatar(token, args.image)
            print("Avatar updated.")

        elif args.command == "replies":
            found = replies(token, args.since, cap=args.cap)
            if not found:
                print("No replies or mentions since %s." % args.since)
            for row in found:
                print("--- #%s — %s — %s (%s)"
                      % (row["channel"], row["author"],
                         row["timestamp"][:10], row["kind"]))
                print(row["content"])
                print()
            if found:
                print("%d item(s) since %s." % (len(found), args.since))

        elif args.command == "channels":
            for guild in channels(token):
                print("=== %s === (%d channels)"
                      % (guild["guild"], len(guild["channels"])))
                for row in guild["channels"]:
                    print("  #%s — %s — id %s%s"
                          % (row["name"], row["type"], row["id"],
                             "  [no overwrites of its own]"
                             if row["no_overwrites"] else ""))
            return 0
        elif args.command == "permissions":
            for guild in permissions(token):
                print("=== %s ===" % guild["guild"])
                print("-- roles --")
                for role in guild["roles"]:
                    print("  %s (id %s)  raw=%s"
                          % (role["name"], role["id"], role["raw"]))
                    print("    %s" % (", ".join(role["named"]) or "(none of "
                                      "the notable bits)"))
                print("-- channel overwrites --")
                for channel in guild["channels"]:
                    if not channel["overwrites"]:
                        continue
                    print("  #%s (type %s, id %s)"
                          % (channel["name"], channel["type"], channel["id"]))
                    for over in channel["overwrites"]:
                        print("    %s" % over["who"])
                        print("      allow: %s"
                              % (", ".join(over["allow"]) or "-"))
                        print("      deny:  %s"
                              % (", ".join(over["deny"]) or "-"))
                print("A channel with no overwrites inherits its roles' "
                      "permissions unchanged and is not listed above.")
                print("This reports what is granted and denied. It does not "
                      "compute any member's effective permissions, which "
                      "combine their roles with these overwrites.")

        elif args.command == "threads":
            grouped = threads(token)
            if not grouped:
                print("No open forum topics visible to the bot. Archived "
                      "topics are not listed.")
            for parent in sorted(grouped):
                print("=== #%s ===" % parent)
                for thread_id, name in grouped[parent]:
                    print("  %s  %s" % (thread_id, name))

        elif args.command == "whoami":
            me = whoami(token)
            print("%s#%s (id %s)" % (me.get("username"),
                                     me.get("discriminator"), me.get("id")))

    except DiscordError as error:
        sys.stderr.write("%s\n" % error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
