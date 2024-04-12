'''
Данный файл является своего рода базой данных,
где хранятся различные переменные и их значения
'''
TOKEN = '6808821591:AAH3ZVqDUu5FRGKKYR1fZjSoioktgk9U5cc'

dish_name = None
dish_price = None
dish_count = None

names = None
buyer = None
result_for_buyer = None
result = None


split_bill = {}
bill_copy = []
keyboard =  []
all_results_of_buyers = ""

number_dish = 1

count = 0
rest = 0
bill_sum = 0
price = 0


is_get_names_AND_bill_copy = False
is_get_bill = False

# переключатель, который контролирует последовательность выполнения команд
executed_handlers = {
    'is_Start_executed': False,
    
    'is_Bill_name_executed': False,

    'is_Get_bill_name_executed': False,

    'is_Get_bill_price_executed': False,

    'is_Bill_executed': False,

    'is_Names_executed': False,

    'is_Get_Names_executed': False,

    'is_buyer_executed': False,

    'is_Who_buy_executed': False 
}