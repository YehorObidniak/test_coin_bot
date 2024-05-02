import telebot
from telebot import types
from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from database import get_db
import time
from datetime import datetime

Base = declarative_base()

class Player(Base):
    __tablename__ = 'main_player'
    
    telegram_id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    referred_by_id = Column(BigInteger, ForeignKey('main_player.telegram_id'), nullable=True)
    multitap_level = Column(Integer, default=1)
    recharging_speed_level = Column(Integer, default=1)
    energy_limit_level = Column(Integer, default=1)
    rocket_count = Column(Integer, default=3)
    full_energy_count = Column(Integer, default=3)
    energy_balance = Column(Integer, default=1000)
    coins_balance = Column(Integer, default=0)
    total_coins_earned = Column(Integer, default=0)
    last_seen = Column(BigInteger, default=time.time())  # Adjust if specific timestamp handling is needed
    total_earned_day = Column(Integer, default=0)
    total_earned_week = Column(Integer, default=0)
    total_coins_per_hour = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=True)

    # Relationships
    referred_by = relationship("Player", remote_side=[telegram_id], backref="referrals")
    friends = relationship("Player", secondary="main_player_friends", primaryjoin="Player.telegram_id==main_player_friends.c.from_player_id", secondaryjoin="Player.telegram_id==main_player_friends.c.to_player_id")

class PlayerFriends(Base):
    __tablename__ = 'main_player_friends'
    from_player_id = Column(BigInteger, ForeignKey('main_player.telegram_id'), primary_key=True)
    to_player_id = Column(BigInteger, ForeignKey('main_player.telegram_id'), primary_key=True)

API_TOKEN = "7018093041:AAF-1Nkt9NJd8LjUvfyN2s378jv8u9W4u1A"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message:types.Message):
    db = next(get_db())
    referral_id = message.text.split()[1] if len(message.text.split()) > 1 else None
    referred_by_user = db.query(Player).filter_by(telegram_id=referral_id).first() if referral_id else None
    inline_kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text="Play!", web_app=types.WebAppInfo(f"https://testclickerversion.netlify.app")
        )
    )
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    print(referred_by_user)
    player_exists = db.query(Player).filter_by(telegram_id=telegram_id).count() > 0
    print(player_exists)
    if not player_exists:
        print("ADd")
        player = Player(name=name, telegram_id=telegram_id, referred_by=referred_by_user, created_at=datetime.now())
        db.add(player)
        db.commit()
        db.refresh(player)
        if referred_by_user:
            referred_by_user.friends.append(player)
            db.commit()

    # bot.send_message(message.from_user.id, message.from_user.id)
    bot.send_message(message.from_user.id, "Hi, player! Let's start playing today!", reply_markup=inline_kb)

@bot.message_handler(commands=["invite"])
def echo_message(message:types.Message):
    inline_kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text="Invite your friend",
            # switch_inline_query= "привет"
            url=f"https://t.me/share/url?url=https://t.me/Coin_Demo_Bot?start={message.from_user.id}",
        )
    )

    bot.send_message(message.from_user.id, "Choose friends to send your refferal link", reply_markup=inline_kb)

def send_invite_message(user_id):
    bot.send_message(user_id, f"""NIKICOIN
Your friend invites you to join the team

💸 +5K Coins for joining
🎁 +25K Coins for Joining if you have TG Premium

Your referral link: <code class="language-python">https://t.me/Coin_Demo_Bot?start={user_id}</code>""", parse_mode="html", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Invite your freind", url=f"https://t.me/share/url?text=NIKICOIN%E2%9C%95%EF%B8%8F%20Tales%20of%20Telegramia%0A%F0%9F%92%8EYour%20friend%20invites%20you%20to%20join%20the%20team%0A%F0%9F%92%B8%20%2B5K%20Coins%20for%20joining%0A%F0%9F%8E%81%20%2B25K%20Coins%20for%20Joining%20if%20you%20have%20TG%20Premium&url=https://t.me/Coin_Demo_Bot?start={user_id}")))



if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)    
    # send_invite_message(5928954497)