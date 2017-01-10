import random
import string


def rand_code_generator(size=18, chars=string.ascii_letters + string.digits,
                        start_text='default'):
    """
    Generators a random code using letters and numbers with an optional
    initial text value.
    """
    return '{}_{}'.format(start_text,
                          ''.join(random.choice(chars) for _ in range(size)))
