import telebot
import requests
import time
# main-values
BOT_TOKEN =input('Enter BotTOK : ') #Your Bot TOK.
API_KEY = input('Enter Your APIKey : ')# api_KEY, You get from the official Site (AllSports) .
API_URL = "https://allsportsapi.com/api/football/"
bot = telebot.TeleBot(BOT_TOKEN)

subscribed_users = {}
def get_live_matches():
    url = f"{API_URL}?met=Livescore&APIkey={API_KEY}"
    response = requests.get(url)
    try:
        data = response.json()
        return data.get("result", [])
    except requests.exceptions.JSONDecodeError:
        print("Cannot decode Json,TextValue:", response.text)
        return []
def get_match_details(match_id):
    response = requests.get(f"{API_URL}?met=Livescore&matchId={match_id}&APIkey={API_KEY}")
    data = response.json()
    return data.get("result", [])[0] if data.get("result") else None
def send_match_list(chat_id):
    matches = get_live_matches()
    if not matches:
        bot.send_message(chat_id, "‹ لاتوجد مباريات حاليا ›.")
        return
    keyboard = telebot.types.InlineKeyboardMarkup()
    for match in matches:
        btn = telebot.types.InlineKeyboardButton(
            text=f"⟨ {match['event_home_team']} ضد {match['event_away_team']} ⟩.",
            callback_data=f"subscribe_{match['event_key']}"
        )
        keyboard.add(btn)
    bot.send_message(chat_id, "⟨ إختر مباراة⟩", reply_markup=keyboard)
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "مرحبا، انا بوت مبرمج لاظهار اخر المباريات واحداث المباريات، ارسل /matches لرؤية اخر المباريات.")
@bot.message_handler(commands=["matches"])
def list_matches(message):
    send_match_list(message.chat.id)
@bot.callback_query_handler(func=lambda call: call.data.startswith("subscribe_"))
def subscribe_to_match(call):
    match_id = call.data.split("_")[1]
    subscribed_users[call.message.chat.id] = match_id
    bot.answer_callback_query(call.id, "⟨ ستصلك ٱخر اخبار هذه المباراة ⟩")
    bot.send_message(call.message.chat.id, "‹ ستتلقى الإشعارات المهمة ›.")
def monitor_matches():
    last_events = {}
    while True:
        for user_id, match_id in subscribed_users.items():
            match = get_match_details(match_id)
            if match:
                events = match.get("goalscorers", []) + match.get("cards", [])
                for event in events:
                    event_key = f"{match_id}_{event['time']}_{event['home_scorer'] or event['away_scorer']}"
                    if event_key not in last_events:
                        event_text = f"⟨ ⚽ {event['home_scorer'] or event['away_scorer']} سجل هدف بدقيقة {event['time']} ⟩." if "home_scorer" in event else f"⟨ 🟨 بطاقة {event['card']} ⟩."
                        bot.send_message(user_id, event_text)
                        last_events[event_key] = True
        time.sleep(10)  #يحدث كل 10 ثوانيي.

#يشغل البوت..
import threading
monitor_thread = threading.Thread(target=monitor_matches, daemon=True)
monitor_thread.start()
print("Bot ON.")
bot.polling()