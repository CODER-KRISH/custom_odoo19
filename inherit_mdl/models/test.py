import datetime

current_time = datetime.datetime.now()
print(current_time)

exact_time = current_time.strftime("%H:%M")
print(exact_time)

def check_name():
    return print("New Method")

def prepare_vals():

    vals = {
        'name': "Hello",
        'age': "Age",
        'email': 0,
    }

    return vals

def check_vals():

    vals = prepare_vals()

    if vals.get('email'):

        vals.update({
            'email': "Krish"
        })

    return vals

print(check_vals())