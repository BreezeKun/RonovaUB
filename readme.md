<div align="center">

![Ronova UB Poster](https://i.ibb.co/RTzpvx9Z/x.jpg)

# Ronova

**A powerful Telegram userbot built on the latest Telegram features**

Powered by [Kurigram](https://github.com/KurimuzonAkuma/pyrogram)

![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![Kurigram](https://img.shields.io/badge/library-Kurigram-2CA5E0?logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📋 Table of Contents

- [Requirements](#-requirements)
- [User Commands](#-user-commands)
- [Bot Features](#-bot-features)
- [Command Prefixes](#-command-prefixes)

---

## ⚙️ Requirements

Set the following environment variables in your `.env` file:

| Variable | Type | Description |
|:---|:---:|:---|
| `api_id` | `int` | Your Telegram API ID |
| `api_hash` | `str` | Your Telegram API hash |
| `bot_token` | `str` | Token for the companion bot |
| `bot` | `str` | Bot username |
| `admin` | `int` | Your Telegram user ID (admin) |
| `string_session` | `str` | Userbot session string |
| `tavily_key` | `str` | Tavily API key |
| `tmdb_key` | `str` | TMDB API key |
| `gemini_key` | `str` | Google Gemini API key |
| `groq_key` | `str` | Groq API key |

---

## 🧑‍💻 User Commands

| Command | Description |
|:---|:---|
| `anisearch <name>` | Search for anime |
| `del` | Delete a replied-to message |
| `purge` | Delete all messages up to the replied-to message |
| `eval <code>` | Evaluate code |
| `googleit <text>` | A fun command |
| `logs` | Get system logs |
| `movie <name>` | Search for a movie |
| `wrdsearch` | Search for a word |
| `bash <code>` | Compile and run shell code |
| `start` | Check if the bot is up |
| `stats` | stats of userbot |
| `think <text>` / `think adv <text>` | AI-powered search |
| `wiki <text>` | Search Wikipedia |
| `afk <text>` | set user status to afk if replied to media it will send media |

---

## 🤖 Bot Features

| Feature | Description |
|:---|:---|
| `@botusername @targetusername <text>` | Send a private text to a target user |
| `@botusername rich <text>` | Send a rich message — see the [richparser](https://github.com/BreezeKun/richparser) library for formatting reference |
| `start` | Check if the bot is up |
| **DM Forwarding** | Any message sent to the bot is forwarded to you (the admin). Reply to the forwarded message to send a reply back to the original sender ( also works for private accounts )|
| **Group Guest Mode** | Sending the bot's username in a group triggers guest mode, responding similarly to the `start` command |

---

## 🔡 Command Prefixes

<table>
<tr><th>Context</th><th>Prefixes</th></tr>
<tr>
<td><b>Userbot</b></td>
<td><code>.</code> <code>@</code> <code>#</code> <code>$</code> <code>%</code> <code>^</code> <code>&</code> <code>*</code> <code>~</code> <i>(or none)</i></td>
</tr>
<tr>
<td><b>Bot</b></td>
<td><code>/</code></td>
</tr>
</table>

---
