from tabulate import tabulate
import time

def print_users(query):
    if isinstance(query, list):
        users = query
    else:
        users = [query]
    table = []
    for user in users:
        table.append([
            user.id,
            user.socket_id,
            user.user_name,
            user.waiting,
            user.gender,
            user.age,
            user.gender_pref,
            user.min_age_pref,
            user.max_age_pref,
        ])
    headers = [
        'ID',
        'Socket ID',
        'User Name',
        'Waiting',
        'Gender',
        'Age',
        'Gender Pref',
        'Min Age Pref',
        'Max Age Pref',
    ]
    print(tabulate(table, headers=headers, tablefmt='grid'))
    
def timer_wrapper(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        func(*args, **kwargs)
        t2 = time.time()
        print(f"Function {func.__name__} took {t2-t1 : .4f} seconds")
    return wrapper