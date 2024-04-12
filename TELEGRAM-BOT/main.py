import logging
import re
import json
import bot_secrets as secret

from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def help(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    '''
    Выводит последовательность действий для общения с ботом

    Args: 
        update (Update)

    Await:
        Выводит сообщение в чат с ботом

    '''
    await update.message.reply_text("Help!")


async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    '''
    Самая первая команда для начала общения с ботом

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Start_executed'] дает значение True,
        чтобы дать доступ для выполнения следующей команде - /bill

    '''
    secret.executed_handlers['is_Start_executed'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет-привет! Чтобы начать, выбери команду /bill ")


async def bill(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Выводит сообщение пользователю о необходимости ввода информации для чека

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        bill_name (None): Выводит сообщение с просьбой ввести название блюда. 
    
    '''
    if secret.executed_handlers['is_Start_executed']:
        await bill_name(update, context)


async def stop(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Прекращает процесс заполнения чека

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Bill_executed'] дает значение True,
        чтобы дать доступ для выполнения следующей команде - /names
    
    '''
    secret.executed_handlers['is_Bill_executed'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Хорошо, чтобы продолжить выбери команду /names')


async def names(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        )-> str:
    '''
    Выводит сообщение пользователю о необходимости написания списка имён

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Names_executed'] дает значение True,
        чтобы дать доступ для выполнения функции get_names

    '''
    if secret.executed_handlers['is_Bill_executed']:
        secret.executed_handlers['is_Names_executed'] = True
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Теперь напиши список имен через запятую')


async def split(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Команда, чтобы начать распределение чека по именам

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент
            
    Await:
        secret.rest (int): количество блюд в чеке, которые надо распределить по именам
        buyer_ask (str): выводит сообщение в чат с ботом о том, кто и в каком количестве взял данное блюдо

    '''
    if secret.executed_handlers['is_Get_Names_executed']:
        with open("./bill.json", "r+", encoding="utf-8") as bill:
            bill = json.load(bill)
        secret.rest = bill[0]["Count"]
        await buyer_ask(update, context, bill)
        

async def get_price_of_dish(
        dish_of_buyer:dict
        ) -> int:
    ''' Получает цену за одно заказанное блюдо

    Args:
        dish_of_buyer (dict): блюдо, которое было заказано

    Await:
        secret.bill_sum (int): Сумма, которую нужно оплатить покупателю за все блюда, что он заказал

    '''
    for i in range(len(secret.bill_copy)):
        if dish_of_buyer["Name"] == secret.bill_copy[i]["Name"]:
            secret.price = dish_of_buyer['Price'] * dish_of_buyer['Count'] 
            secret.bill_sum += secret.price


async def result(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    ''' Подсчет суммы чека
    
    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        Выводит весь результат в чат с ботом

    '''
    for buyer_name in secret.split_bill.keys():
        secret.bill_sum = 0
        
        for dish_of_buyer in secret.split_bill[buyer_name]:            
            await get_price_of_dish(dish_of_buyer)

        secret.all_results_of_buyers += str(f'{buyer_name} оплачивает: {int(secret.bill_sum)} рублей\n')
    
    # Вывод результатов в терминал для САМОпроверки 
    print(f'secret.split_bill = {secret.split_bill}')
    print(secret.all_results_of_buyers)
   
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=secret.all_results_of_buyers)


async def switcher_of_input_data(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    ''' Переключатель по введенной информации. 
    Следит за тем, чтобы команды для обработки ввода пользователя выполнялись последовательно, по порядку
    
    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        how_much (None): В каком количестве было заказано данное блюдо?
        who_buy (None): Кто взял данное блюдо?
        get_names (None): Получает список имен
        get_bill_count (None): Получает количество блюд. Добавляет значения в чек bill
        get_bill_price (None): Получает цену за блюдо
        get_bill_name (None): Получает название блюда и выводит сообщение 

    '''
    if secret.executed_handlers['is_Who_buy_executed']: 
        await how_much(update, context)

    elif secret.executed_handlers['is_buyer_executed']: 
        await who_buy(update, context)

    elif secret.executed_handlers['is_Names_executed']: 
        await get_names(update, context)
    
    elif secret.executed_handlers['is_Get_bill_price_executed']:
        await get_bill_count(update, context)

    elif secret.executed_handlers['is_Get_bill_name_executed']:
        await get_bill_price(update, context)
    
    elif secret.executed_handlers['is_Bill_name_executed']:
        await get_bill_name(update, context)



async def zero(
        update : Update, 
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    '''Срабатывает при вводе нуля
    
    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        Выводит сообщение в чат с ботом о неправильном вводе числа

    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text = f"Число не может быть нулевым! Набери ещё раз!")


async def negative_number(
        update : Update, 
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    '''Срабатывает при вводе отрицательного числа

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        Выводит сообщение в чат с ботом о неправильном вводе числа

    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Число не может быть отрицательным! Набери ещё раз!")
 

async def too_much(
        update : Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> str:
    '''Срабатывает, когда введенное число превышает количество блюд в чеке

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        Выводит сообщение в чат с ботом о неправильном вводе числа

    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"{secret.buyer} видно очень голодный(-ая)! Превышено кол-во доступных блюд!")


async def text_of_result(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> str:
    '''Выводит сообщение пользователю об успешном распределении чека

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент 

    Await:
        Выводит сообщение в чат с ботом

    '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Хорошо, теперь, чтобы получить результат, выбери команду /result")


async def buyer_ask(
        update : Update, 
        context: ContextTypes.DEFAULT_TYPE,
        bill: json
        ) -> str:
    ''' Выясняет (одного человека) кто купил данное блюдо и в каком количестве
    
    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент
        bill (json): Чек, который нужно распределить по именам

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_buyer_executed'] дает значение True,
        чтобы дать доступ для выполнения функции who_buy

    '''
    reply_markup = InlineKeyboardMarkup(secret.keyboard)

    secret.executed_handlers['is_buyer_executed'] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Кто взял: \"{bill[0]['Name']}\"? (Остаток от блюда: {secret.rest} шт)\n", reply_markup=reply_markup)


async def how_much(
        update : Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Распределяет чек по именам в зависимости от введенного числа 

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        text_of_result (str): Вывод сообщения пользователю об успешном распределении чека 
    '''

    with open("./bill.json", "r", encoding="utf-8") as file:
        bill = json.load(file)
    try:
        secret.count = int(update.message.text)
        if (secret.count <= secret.rest) and (secret.count > 0):
            
            secret.split_bill[secret.buyer] += [{
                "Name":  bill[0]['Name'],
                "Price": int(bill[0]['Price'] / bill[0]['Count']),
                "Count": secret.count, }]
            print(f'после добавления: {secret.split_bill}')
            secret.rest -= secret.count

            if secret.rest != 0:
                await buyer_ask(update, context, bill)
                secret.executed_handlers['is_Who_buy_executed'] = False
            
            elif secret.rest == 0:
                del bill[0]
                with open("./bill.json", 'w', encoding="utf-8") as file:
                    file.write(json.dumps(bill,  indent=4, ensure_ascii=False))
                if bill == []:
                    await text_of_result(update, context)
                else:
                    secret.executed_handlers['is_Who_buy_executed'] = False
                    secret.rest = bill[0]["Count"]
                    await buyer_ask(update, context, bill)

        elif  secret.count == 0:
            await zero(update,context)

        elif  secret.count < 0:
            await negative_number(update,context)

        elif secret.count > secret.rest:
            await too_much(update,context)

    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = f'Это не число!!! Набери ещё раз!!!')
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = f'Сколько?')

            
async def who_buy(
        update : Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    ''' Определяет кто заказал данное блюдо

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Вывод сообщения "Сколько?" в чат с ботом. Переключателю secret.executed_handlers['is_Who_buy_executed'] дает значение True,
        чтобы дать доступ для выполнения функции how_much

    '''
    secret.executed_handlers['is_Who_buy_executed'] = True

    with open("./bill.json", "r", encoding="utf-8") as file:
        bill = json.load(file)

    # Срабатывает только один раз
    if (not secret.is_get_names_AND_bill_copy):
        #* Резервный чек, чтобы использовать его для подсчета суммы чека
        secret.bill_copy = bill.copy()

        names = secret.names
        for name in names:
            secret.split_bill[name] = []
        secret.is_get_names_AND_bill_copy = True
    
    query = update.callback_query
    await query.answer()
    
    secret.buyer = query.data

    if (secret.buyer == 'Все'):   
        for name in secret.names:
            secret.split_bill[name] += [{
                "Name": bill[0]['Name'],
                "Price": int(bill[0]['Price'] / len(secret.names)),
                "Count": 1, }]
        del bill[0]
        with open("./bill.json", 'w', encoding="utf-8") as file:
            file.write(json.dumps(bill,  indent=4, ensure_ascii=False))
        
        if (bill == []):
            await text_of_result(update, context)
        else:
            secret.executed_handlers['is_Who_buy_executed'] = False
            secret.rest = bill[0]["Count"]
            await buyer_ask(update, context, bill)
        
    elif (secret.buyer != 'Все'):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='Сколько?')


async def get_names(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Принимает список имён, введённый пользователем

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Вывод сообщения в чат с ботом. Переключателю secret.executed_handlers['is_Get_Names_executed'] дает значение True,
        чтобы дать доступ для выполнения следующей команде - /split

    '''
    
    secret.executed_handlers['is_Get_Names_executed'] = True
    message = (update.message.text)
    secret.names = re.split(", |,", message)

    for name in secret.names:
        secret.keyboard.append(
        [
            InlineKeyboardButton(name, callback_data = name),
        ])
    secret.keyboard.append(
        [
            InlineKeyboardButton('Все', callback_data = 'Все'),
        ])
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Чтобы начать распределение чека по именам, выбери команду /split')


async def bill_name(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Выводит сообщение с просьбой ввести название блюда

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Bill_name_executed'] дает значение True,
        чтобы дать доступ для выполнения функции get_bill_name
    
    '''
    secret.executed_handlers['is_Bill_name_executed'] = True

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f'Блюдо №{secret.number_dish}: Как называется {secret.number_dish}-е блюдо?')


async def get_bill_name(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Получает название блюда и выводит сообщение 

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Get_bill_name_executed'] дает значение True,
        чтобы дать доступ для выполнения функции get_bill_price
    
    '''
    secret.executed_handlers['is_Get_bill_name_executed'] = True
    secret.dish_name = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text= f"Сколько стоит {secret.dish_name}?") 


async def get_bill_price(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Получает цену за блюдо

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом. Переключателю secret.executed_handlers['is_Get_bill_price_executed'] дает значение True,
        чтобы дать доступ для выполнения функции get_bill_count
    
    '''
    try:
        secret.dish_price = int(update.message.text)

        if secret.dish_price > 0:
            secret.executed_handlers['is_Get_bill_price_executed'] = True
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text= "Сколько будет блюд?")
        
        elif  secret.dish_price == 0:
            await zero(update,context)

        elif  secret.dish_price < 0:
            await negative_number(update,context)
           
        
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = f'Это не число!!! Набери ещё раз!!!')
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = f'Сколько стоит {secret.dish_name}?')


async def get_bill_count(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
        ) -> None:
    '''Получает количество блюд. Добавляет значения в чек bill

    Args:
        update (Update): Первый аргумент
        context (ContextTypes.DEFAULT_TYPE): Второй аргумент

    Await:
        Выводит сообщение в чат с ботом.
        bill_name (None): Выводит сообщение с просьбой ввести название блюда
        
    '''
    try:
        secret.dish_count = int(update.message.text)
        if secret.dish_count > 0:
           
            with open("./bill.json", "r", encoding="utf-8") as file:
                bill = list(json.load(file))

            bill.append({
                'Name': secret.dish_name, 
                'Price': secret.dish_price, 
                'Count': secret.dish_count
                })

            with open("./bill.json", 'w', encoding="utf-8") as file:
                file.write(json.dumps(bill,  indent=4, ensure_ascii=False))
            
            secret.executed_handlers['is_Bill_name_executed'] = False
            secret.executed_handlers['is_Get_bill_name_executed'] = False
            secret.executed_handlers['is_Get_bill_price_executed'] = False
            
            secret.number_dish += 1

            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f'Чтобы закончить заполнение чека, выбери команду /stop')
            
            await bill_name(update, context)
        
        elif  secret.dish_count == 0:
            await zero(update,context)

        elif  secret.dish_count < 0:
            await negative_number(update,context)
    
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = f'Это не число!!! Набери ещё раз!!!')
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text = 'Сколько будет блюд?')



if __name__ == '__main__':
    application = ApplicationBuilder().token(secret.TOKEN).build()

    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    stop_handler = CommandHandler('stop', stop)
    bill_handler = CommandHandler('bill', bill)
    names_handler = CommandHandler('names', names)
    split_handler = CommandHandler('split', split)
    result_handler = CommandHandler('result', result)
    
    switcher_of_input_data_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, switcher_of_input_data)

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(bill_handler)
    application.add_handler(names_handler)
    application.add_handler(split_handler)
    application.add_handler(result_handler)

    application.add_handler(CallbackQueryHandler(who_buy))

    application.add_handler(switcher_of_input_data_handler, group=0)
    
    application.run_polling()