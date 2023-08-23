import telebot
from telebot import types
import json
import pandas as pd

bot = telebot.TeleBot('5825458914:AAHxvx1LzxoN1PRqotd54Tp8kfnSN14cq3A'); # токен бота

name = '' # переменная для Имя
surname = '' # переменная для Фамилия
nickname = '' # переменная для никнейма
age = 0 # переменная для возраста
reglist_name = [] # список для хранения имён
reglist_surname = [] # список для хранения фамилий
reglist_age = [] # список для хранения возрастов
reglist_nickname = [] # список для хранения никнеймов

# xg = expected score (по аналогии с футболом)
def calculate_elo_rating(player1_rating, player2_rating, result, k_factor): # функция подсчета эло
    xg_player1 = 1 / (1 + 10 ** ((player2_rating - player1_rating) / 400))
    xg_player2 = 1 - xg_player1

    if result == 1: # выиграл игрок 1
        player1_new_rating = player1_rating + k_factor * (1 - xg_player1)
        player2_new_rating = player2_rating + k_factor * (0 - xg_player2)
        if player2_new_rating < 0:
            player2_new_rating = 0
    elif result == 2:# выиграл игрок 2
        player1_new_rating = player1_rating + k_factor * (0 - xg_player1)
        player2_new_rating = player2_rating + k_factor * (1 - xg_player2)
        if player1_new_rating < 0:
            player1_new_rating = 0
    else: # ничья
        player1_new_rating = player1_rating
        player2_new_rating = player2_rating

    return player1_new_rating, player2_new_rating

player1_rating = 0
player2_rating = 0
k_factor = 40

#@bot.message_handler(content_types = ['text', 'document', 'audio']) - не работает
@bot.message_handler(commands = ['reg', 'result'])

def start(message): 
    if message.text == '/reg': # команда для регистрации
        bot.send_message(message.from_user.id, "Как тебя зовут?");
        bot.register_next_step_handler(message, get_name);
    if message.text == '/result': # команда для внесения результата матча
        bot.send_message(message.from_user.id, "Какой у тебя никнейм?");
        bot.register_next_step_handler(message, check_nickname);
    ##else:
    ##    bot.send_message(message.from_user.id, "Такой команды нет."); # лишняя строка 
        
def get_name(message): ## имя
    global name;
    name = message.text;
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?');
    bot.register_next_step_handler(message, get_surname);
    

def get_surname(message): ## фамилия
    global surname;
    surname = message.text;
    bot.send_message(message.from_user.id,'Придумай никнейм:');
    bot.register_next_step_handler(message, get_nickname);
    
def get_nickname(message): ## ник
    global nickname;
    nickname = message.text;
           
    
    if nickname in reglist_nickname: # проверка на уникальность выбранного никнейма
        bot.send_message(message.from_user.id, 'Другой игрок уже взял такой ник, попробуй что-то другое:');
        bot.register_next_step_handler(message, get_nickname);
    else:
        dfnick = pd.read_excel('table.xlsx') # в файле "table": 
        # 2 столбца: никнейм и рейтинг, в первый записывается введенный ник, во второй - ноль
        ws = {
        'nickname' : nickname,
        'rating' : "0"
        }
        dfnick =  pd.concat([dfnick,pd.DataFrame([ws])],axis=0)
        dfnick.to_excel('table.xlsx', index = False)     
        
        bot.send_message(message.from_user.id, 'Сколько тебе лет?');
        bot.register_next_step_handler(message, get_age);

def get_age(message): ## возраст
    global age;
    age = message.text;
    
    keyboard = types.InlineKeyboardMarkup(); # клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes'); # кнопка да
    keyboard.add(key_yes); # добавляем кнопку в клавиатуру
    key_no= types.InlineKeyboardButton(text='Нет', callback_data='no'); # кнопка нет
    keyboard.add(key_no);
    question = 'Тебе '+str(age)+', тебя зовут '+name+' '+surname+ ', твой ник - '+nickname+'?';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    
def check_nickname(message): ## проверка ника для внесения результата матча (ввод своего)
    global checknickname;
    checknickname = message.text;
    bot.send_message(message.from_user.id,'Какой ник у твоего соперника?');
    bot.register_next_step_handler(message, get_rivalnickname);

def get_rivalnickname(message): ## ввод ника соперника 
    global rivalnickname;
    rivalnickname = message.text;

    keyboard = types.InlineKeyboardMarkup(); # клавиатура
    key_win = types.InlineKeyboardButton(text='Победа', callback_data='win'); #кнопка победа
    keyboard.add(key_win); #добавляем кнопку победы в клавиатуру
    key_lose= types.InlineKeyboardButton(text='Поражение', callback_data='lose'); #кнопка поражение
    keyboard.add(key_lose); #добавляем кнопку луза в клавиатуру
    question = 'Какой был результат вашего матча:';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)

def callback_worker(call): 
    # обновление таблицы с именем, фамилией, возрстом и никнеймом
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        df1 = pd.read_excel('registration.xlsx')
        print(df1)
        reglist_name.append(name)
        reglist_surname.append(surname)
        reglist_age.append(age)
        reglist_nickname.append(nickname)
              
        bot.send_message(call.message.chat.id, 'Ок, запомню :)');
        
        ws = {
            'name': name,
            'surname':surname,
            'age': age,
            'nickname': nickname
        }
        
        print(pd.DataFrame([ws]))
        df1 =  pd.concat([df1,pd.DataFrame([ws])],axis=0)
        print(df1)
        df1.to_excel('registration.xlsx', index = False)
        print(reglist_name)
        print(reglist_surname)
        print(reglist_age)
        print(reglist_nickname)
    
    # обновление таблицы с никнеймом и эло в случае вина
    elif call.data == "win": 
        result = 1
        dfnick = pd.read_excel('table.xlsx')
       # 2 цикла по столбцу никнейма в поисках своего ника и ника соперника, поттом замена переменных на значения ячейки в соседнем столбце
        # циклы не работают
        if checknickname in dfnick:
            for i in dfnick.iloc[i]['checknickname']:
                
                player1_rating = dfnick.iloc[i]['rating']
        
        if rivalnickname in dfnick:
            for i in dfnick.iloc[i]['rivalnickname']:
                
                player2_rating = dfnick.iloc[i]['rating']
    
       
        player1_new_rating, player2_new_rating = calculate_elo_rating(player1_rating, player2_rating, result, k_factor)
        
        dfnick = pd.read_excel('table.xlsx')
        ws1 = {
            'nickname': checknickname,
            'raiting': player1_new_rating
        }
        ws2 = {
            'nickname': rivalnickname,
            'raiting': player2_new_rating
        }
        #dfnick.sort_values("raiting", ascending = False) #сортировка крашила программу 
        
        dfnick =  pd.concat([dfnick,pd.DataFrame([ws1, ws2])],axis=0)
        dfnick.to_excel('table.xlsx', index = False)
 
    # обновление таблицы с никнеймом и эло в случае луза
    elif call.data == "lose":
        result = 2
        dfnick = pd.read_excel('table.xlsx')
       # 2 цикла по столбцу никнейма в поисках своего ника и ника соперника, поттом замена переменных на значения ячейки в соседнем столбце
        # циклы не работают
        if checknickname in dfnick:
            for i in dfnick.iloc[i]['checknickname']:
                
                player2_rating = dfnick.iloc[i]['rating']
        
        if rivalnickname in dfnick:
            for i in dfnick.iloc[i]['rivalnickname']:
                
                player1_rating = dfnick.iloc[i]['rating']
    
       
        player1_new_rating, player2_new_rating = calculate_elo_rating(player1_rating, player2_rating, result, k_factor)
        
        dfnick = pd.read_excel('table.xlsx')
        ws1 = {
            'nickname': checknickname,
            'raiting': player1_new_rating
        }
        ws2 = {
            'nickname': rivalnickname,
            'raiting': player2_new_rating
        }
        #dfnick.sort_values("raiting", ascending = False) #сортировка крашила программу 
        
        dfnick =  pd.concat([dfnick,pd.DataFrame([ws1, ws2])],axis=0)
        dfnick.to_excel('table.xlsx', index = False)
        
        
    elif call.data == "no": ...  
    
    
        
bot.polling(none_stop = True, interval = 0)