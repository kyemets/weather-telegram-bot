import os
import requests
from flask import Flask
from aiogram import Bot, Dispatcher, executor, types, executor
from aiohttp.client import request
from bot_token import TOKEN
import math
import aiogram.utils.markdown as fmt
from weather_app_token import WEATHER_APP_TOKEN 
import hashlib
from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle

app = Flask(__name__)


bot = Bot(TOKEN)
dp = Dispatcher(bot)
server = Flask(__name__)

''' Command Start '''
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    # get user/chat id
    user_id = message.from_user.id
    await bot.send_sticker(user_id, sticker='CAACAgIAAxkBAAEEeItiWG7TWqCapeRnGLmb0JhzlfO6UwACAQEAAladvQoivp8OuMLmNCME')
    await message.answer(f"Hi, {message.from_user.first_name}")
    await message.answer("List of available commands: /help  ")


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Share Position", request_location=True, resize_keyboard=True)
    keyboard.add(button)
    return keyboard

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    reply = "latitude:  {}\nlongitude: {}".format(lat, lon)
    response = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}'.format(lat, lon, WEATHER_APP_TOKEN))
    await message.answer(reply)

    json_response = response.json()

    # get current weather
    get_current_temp = json_response['current']['temp']
    # get feels like current temperature
    get_current_feels_like = json_response['current']['feels_like']
    # check current rain
    get_rain = json_response['current']['weather'][0]
    get_check_rain = get_rain['description']

    convert_to_celcius = (int(get_current_temp) - 273)
    math.ceil(convert_to_celcius)

    feels_like_convert_to_celcius = (int(get_current_feels_like) - 273)
    math.ceil(feels_like_convert_to_celcius)

    # get temperature tomorrow
    get_temp_tomorrow = json_response['daily'][1]['temp']['day']
    convert_to_celcius_temp_tomorrow = (int(get_temp_tomorrow) - 273)
    math.ceil(convert_to_celcius_temp_tomorrow)

    # the day after tomorrow
    get_temp_day_after_tomorrow = json_response['daily'][2]['temp']['day']
    convert_to_celcius_temp_after_tomorrow = (int(get_temp_day_after_tomorrow) - 273)
    math.ceil(convert_to_celcius_temp_after_tomorrow)

    


    await message.answer(
        fmt.text(
            fmt.text("☂️ Current Weather ", ),
            fmt.text("Temperature: ", fmt.hbold(convert_to_celcius), "°C"),
            fmt.text("Feels like:", fmt.hbold(feels_like_convert_to_celcius), "°C"),
            fmt.text("Description:", fmt.hbold(get_check_rain)),
            fmt.text(" "),
            fmt.text("☂️ Tomorrow:"),
            fmt.text("Temperature:", fmt.hbold(convert_to_celcius_temp_tomorrow), "°C"),
            fmt.text(" "),
            fmt.text("☂️ The day after tomorrow:"),
            fmt.text("Temperature:", fmt.hbold(convert_to_celcius_temp_after_tomorrow), "°C"),
            sep="\n"
        ), parse_mode="HTML"
    )


@dp.message_handler(commands=['location'])
async def cmd_locate_me(message: types.Message):
    reply = "Click on the the button below to share your location"
    await message.answer(reply, reply_markup=get_keyboard())


''' inline button '''
@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = inline_query.query or 'Please enter your city'
    input_content = InputTextMessageContent(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    inline_response = requests.get('https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(text, WEATHER_APP_TOKEN))
    json_response = inline_response.json()
    get_temp = json_response['main']['temp']

    convert_to_celcius = (int(get_temp) - 273)
    math.ceil(convert_to_celcius)

    item = InlineQueryResultArticle(
        id=result_id,
        title=f'{text}:  {convert_to_celcius!r} °C',
        input_message_content=input_content,
    )

    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)




''' Get Help '''
@dp.message_handler(commands="help")
async def cmd_start(message: types.Message):
    await message.answer("/location — will send your geolocation to show the weather")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    server.debug = True
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    server.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 5000)),
        url_path=TOKEN,
        webhook_url=  'https://weather-app-tgbot.herokuapp.com/'+ TOKEN
    )
    
