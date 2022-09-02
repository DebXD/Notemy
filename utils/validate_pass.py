import re
def validate(password):
    if len(password) < 8:
        return ("Make sure your password has at lest 8 letters")
    elif re.search('[0-9]',password) is None:
        return ("Make sure your password has a number in it")
    elif re.search('[A-Z]',password) is None: 
        return ("Make sure your password has a capital letter in it")
    else:
        return True
