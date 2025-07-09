
import json
import sys

# ----------------------Consts-------------------------#
CORRECT_CONFIG_FILE_CONTENTS = ["hash_map", "wheels", "reflector_map"]
HASHMAP, WHEELS, REFLECTOR = CORRECT_CONFIG_FILE_CONTENTS
ADD = "add"
SUBTRACT = "sub"
EMPTY = ""
CONFIG_FLAG = "-c"
INPUT_FLAG = "-i"
OUTPUT_FLAG = "-o"
W1_RESET_VALUE = 1
W2_CHECK = 2
W3_CHECK_ONE = 10
W3_CHECK_TWO = 3
FIRST_W3_VALUE = 10
SECOND_W3_VALUE = 5
THIRD_W3_VALUE = 0
W1_COEFFICIENT = 2
W2_MULTIPLIER = 2
MOD_VALUE = 26
W1_UPPER_LIMIT = 8
GENERAL_ERROR_MESSAGE = "The enigma script has encountered an error"
USAGE_ERROR_MESSAGE = "Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>"

# -------------------- exceptions -------------------- #
class JSONFileException (IOError):
    pass

# ---------------------- class ---------------------- #
class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = wheels
        self.reflector_map = reflector_map
        self.reverse_hash = {value : key for key, value in self.hash_map.items()}


    def encrypt(self, message):
        encrypted_message = EMPTY
        counter = 0
        wheels_copy = self.wheels.copy()
        for c in message:
            encrypted_char = encrypt_char(c, self.hash_map, wheels_copy, self.reflector_map, self.reverse_hash)
            if encrypted_char != c:
                counter = counter + 1
            encrypted_message = encrypted_message + encrypted_char
            change_wheels(wheels_copy, counter)
        return encrypted_message

# -------------------- functions -------------------- #
def load_enigma_from_path(path):
    try:
        with open(path, "r") as inputFile:
            data = json.load(inputFile)
            for name in CORRECT_CONFIG_FILE_CONTENTS:
                if name not in data:
                    raise JSONFileException
            return Enigma(data[HASHMAP], data[WHEELS], data[REFLECTOR])
    except (IOError, ValueError):
        raise JSONFileException

def get_new_i(wheels, i, operation = ADD):
    w1, w2, w3 = wheels
    if operation == SUBTRACT:
        op = -1
    else:
        op = 1
    check = ((W1_COEFFICIENT * w1) - w2 + w3) % MOD_VALUE
    if check !=  0:
        i = i + op * check
    else:
        i = i + op * 1
    return mod_i(i)

def mod_i(i):
    return i % MOD_VALUE

def change_wheels(wheels, counter):
    w1, w2, w3 = wheels
    w1 = w1 + 1
    if w1 > W1_UPPER_LIMIT:
        w1 = W1_RESET_VALUE
    if counter % W2_CHECK == 0:
        w2 = w2 * W2_MULTIPLIER
    else:
        w2 = w2 - 1
    if counter % W3_CHECK_ONE == 0:
        w3 = FIRST_W3_VALUE
    elif counter % W3_CHECK_TWO == 0:
        w3 = SECOND_W3_VALUE
    else:
        w3 = THIRD_W3_VALUE

    wheels[:] = [w1, w2, w3]

def encrypt_char(c, hash_map, wheels, reflector_map, reverse_hash):
    if c.isalpha() and c.islower():
        i = hash_map[c] # 1
        i = get_new_i(wheels, i, ADD) # 2 + 3
        c1 = reverse_hash[i] # 4
        c2 = reflector_map[c1] # 5
        i = hash_map[c2] # 6
        i = get_new_i(wheels, i, SUBTRACT) # 7 + 8
        c3 = reverse_hash[i] # 9
        return c3
    else:
        return c

def main(config_file, input_file, output_file = None):
    try:
        enigma = load_enigma_from_path(config_file)
        with open(input_file, 'r') as f:
            lines = f.readlines()
        if output_file is not None:
            with open(output_file, 'w') as output:
                for line in lines:
                    output.write(enigma.encrypt(line))
        else:
            for line in lines:
                print(enigma.encrypt(line), end=EMPTY)
    except (IOError, JSONFileException):
        print_error_message_and_exit()

def print_error_message_and_exit():
    print(GENERAL_ERROR_MESSAGE)
    exit(1)

def print_usage_message_into_stderr():
    print(USAGE_ERROR_MESSAGE, file = sys.stderr)

# ------------------ run as script only ------------------ #
if __name__ == "__main__": # here I just write my script
    # python3 enigma.py -c <config_file> -i <input_file> -o <output_file>
    if len(sys.argv) > 7:
        print_usage_message_into_stderr()
        exit(1)
    try:
        config_file_index = sys.argv.index(CONFIG_FLAG) + 1
        input_file_index = sys.argv.index(INPUT_FLAG) + 1
    except ValueError:
        print_usage_message_into_stderr()
        exit(1)

    if OUTPUT_FLAG in sys.argv:
        output_file_index = sys.argv.index(OUTPUT_FLAG) + 1
        main(sys.argv[config_file_index], sys.argv[input_file_index], sys.argv[output_file_index])
    else:
        main(sys.argv[config_file_index], sys.argv[input_file_index])
