# tg_bot_for_english

The bot gets your english phrases and then remind them.

# Installation

 - `git clone https://github.com/DimaWoic/tg_bot_for_english.git`
 - `cd /your_path/tg_bot_for_eng`
 - `docker build -f build/Dockerfile -t eng_bot .`
 - `docker run -d -v /home/$USER:/home/bot/sqlite  -e TOKEN="BOT's_TOKEN" eng_bot`
