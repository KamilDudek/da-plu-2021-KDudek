# zad1
def greetings(func):
    def inner(*args):
        return 'Hello ' + func(*args).title()

    return inner


# zad2
def find_letters_numbers(word):
    return ''.join(
        [letter for letter in word if letter.isalpha() or letter.isnumeric()])


def is_palindrome(func):
    def inner(*args):
        return_from_func = find_letters_numbers(func(*args))

        if return_from_func.lower() == return_from_func.lower()[::-1]:
            return f'{func(*args)} - is palindrome'
        else:
            return f'{func(*args)} - is not palindrome'

    return inner


# zad3
import re


def format_output(*args):
    key_words_separated = {}
    key_words_single = []
    original_long_keywords = []

    for arg in args:
        index_of_floor = [m.start() for m in re.finditer('__', arg)]
        i = 0
        counter_long_keywords = 0
        if len(index_of_floor) >= 1:
            key_words_separated[counter_long_keywords] = [
                arg[:index_of_floor[0]]]
            if len(index_of_floor) >= 2:
                while i < len(index_of_floor) - 1:
                    key_words_separated[0].append(
                        arg[index_of_floor[i] + 2:index_of_floor[i + 1]])
                    i += 1
            original_long_keywords.append(arg)
            key_words_separated[counter_long_keywords].append(
                arg[index_of_floor[len(index_of_floor) - 1] + 2:])
        else:
            key_words_single.append(arg)
        counter_long_keywords += 1

    def real_decorator(to_be_decorated):
        def inner(*args):
            new_dict = {}
            val = to_be_decorated(*args)
            j = 0

            for keys, value in key_words_separated.items():
                i = 0
                new_value_of_dict = ''
                for v in value:
                    if v in val.keys():
                        pass
                    else:
                        raise ValueError
                    for key_from_func, value_from_func in val.items():
                        if key_from_func == v:
                            new_value_of_dict += value_from_func
                            if i < len(value) - 1:
                                new_value_of_dict += ' '
                    i += 1
                new_dict[original_long_keywords[j]] = new_value_of_dict
                j += 1

            for keys in key_words_single:
                for key, value in val.items():
                    if keys in val:
                        pass
                    else:
                        raise ValueError('error')
                    if key == keys:
                        new_dict[keys] = value

            return new_dict

        return inner

    return real_decorator


# zad4
from functools import wraps


def add_class_method(cls):
    def decorator(func):
        @classmethod
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)

        return func

    return decorator


def add_instance_method(cls):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)

        return func

    return decorator
