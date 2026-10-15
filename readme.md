<div align="center">

Ronova
A powerful Telegram userbot built on the latest Telegram features

Maintainer note: This repository is not actively maintained due to personal commitments. Contributions and pull requests are welcome!

Ronova UB Poster

Powered by Kurigram

!Python !Kurigram !License

</div>

📋 Table of Contents
Requirements
Userbot Commands
Bot Features
Command Prefixes
Contributing
⚙️ Requirements

Ronova requires Python 3.11 or later and the following environment variables configured in your .env file.

Variable	Type	Description
api_id	int	Your Telegram API ID
api_hash	str	Your Telegram API hash
bot_token	str	Token for the companion bot
bot	str	Companion bot's username
admin	int	Telegram user ID of the administrator
string_session	str	Telegram userbot session string
tavily_key	str	Tavily API key
tmdb_key	str	TMDB API key
gemini_key	str	Google Gemini API key
groq_key	str	Groq API key

Note: Keep your .env file and session string private. Never commit API credentials, bot tokens, or session strings to version control.

🧑‍💻 Userbot Commands

Ronova provides a variety of commands for moderation, utilities, search, and AI-powered features.

Command	Description
anisearch <name>	Search for anime
del	Delete the replied-to message
purge	Delete messages up to the replied-to message
eval <code>	Evaluate Python code
googleit <text>	Run a fun Google-related command
logs	Retrieve system logs
movie <name>	Search for movies
wrdsearch <word>	Search for a word
bash <code>	Execute shell commands
start	Check whether the bot is running
stats	Display userbot statistics
think <text>	Perform an AI-powered search
think adv <text>	Perform an advanced AI-powered search
wiki <text>	Search Wikipedia
q <text>	Generate a quote, or quote a replied-to message
afk <text>	Set your AFK status; supports replying to media
ban <uid> <uptil> <reason>	Ban a user
cban <uid> <uptil> <reason>	Ban a user and revoke their messages and reactions
dban <uid> <uptil> <reason>	Ban a user and delete the replied-to message
sban <uid> <uptil> <reason>	Silently ban a user
unban <uid>	Unban a user; the UID can be omitted when replying to their message
⏱️ Ban Duration Format

The uptil argument specifies how long a ban should last.

Minimum duration: 30 seconds
Maximum duration: 366 days
Unit	Meaning	Example
s	Seconds	30s
m	Minutes	10m
h	Hours	2h
d	Days	7d
w	Weeks	2w

Examples:

ban 123456789 10m Spamming
ban 123456789 7d Repeated abuse
unban 123456789

Replace the example user IDs, durations, and reasons with the appropriate values.

🤖 Bot Features

The companion bot provides the following functionality.

Feature	Description
Private Messaging	Send a private message to a target user using @botusername @targetusername <text>
Rich Messages	Send formatted messages using @botusername rich <text>. See the richparser library for formatting syntax
Status Check	Use /start to check whether the bot is running
DM Forwarding	Messages sent to the bot are forwarded to the administrator. Reply to a forwarded message to respond to the original sender, including private accounts where supported
Group Guest Mode	Mention the bot's username in a group to trigger guest mode, which responds similarly to the /start command
🔡 Command Prefixes

Ronova supports multiple prefixes for userbot commands, while the companion bot uses /.

Context	Supported Prefixes
Userbot	., @, #, $, %, ^, &, *, ~, or no prefix
Companion Bot	/

Examples:

.anisearch Naruto
.movie Interstellar
/wiki Python
/start


Use the prefix appropriate to the command and execution context.

🤝 Contributing

Ronova is not actively maintained due to personal commitments, but contributions are welcome!

If you want to improve the project:

Fork the repository.
Create a branch for your changes.
Implement your feature or fix.
Test your changes thoroughly.
Submit a pull request with a clear description of what you changed and why.

Bug fixes, new features, performance improvements, documentation updates, and code cleanup are all welcome.

Please keep pull requests focused and ensure that sensitive credentials are never included in commits.

📄 License

Ronova is distributed under the MIT License. See the repository's LICENSE file for the full license text.
