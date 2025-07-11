import json
import sys

# Constants
USAGE_ERROR_MESSAGE = "Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>"
ENIGMA_ERROR_MESSAGE = "The enigma script has encountered an error"
NEWLINE = "\n"

# Enigma settings
WHEEL_MAX = 8
WHEEL_STEP_2_EVEN_MULTIPLIER = 2
WHEEL_STEP_2_ODD_DECREMENT = 1
WHEEL_STEP_3_DIV_10_RESET = 10
WHEEL_STEP_3_DIV_3_RESET = 5
WHEEL_STEP_3_DEFAULT = 0
ALPHABET_LENGTH = 26
STEP_2_DEFAULT_INCREMENT = 1

class JSONFileException(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_first_key_by_value(map, value):
    try:
        return [k for k, v in map.items() if v == value][0]
    except Exception as e:
        raise e


class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = wheels
        self.reflector_map = reflector_map

    def encrypt_letter(self, c):
        if c not in self.hash_map:
            return c, False

        i = self.hash_map[c]
        remainder = ((2 * self.wheels[0]) - self.wheels[1] + self.wheels[2]) % ALPHABET_LENGTH
        i += remainder if remainder != 0 else STEP_2_DEFAULT_INCREMENT
        i %= ALPHABET_LENGTH
        
        c1 = get_first_key_by_value(self.hash_map, i)
        c2 = self.reflector_map[c1]
        i = self.hash_map[c2]
        i -= remainder if remainder != 0 else STEP_2_DEFAULT_INCREMENT
        i %= ALPHABET_LENGTH
        
        return get_first_key_by_value(self.hash_map, i), True

    def forward_wheels(self, encrypted_count):
        self.wheels[0] += 1
        if self.wheels[0] > WHEEL_MAX:
            self.wheels[0] = 1

        if encrypted_count % 2 == 0:
            self.wheels[1] *= WHEEL_STEP_2_EVEN_MULTIPLIER
        else:
            self.wheels[1] -= WHEEL_STEP_2_ODD_DECREMENT

        if encrypted_count % 10 == 0:
            self.wheels[2] = WHEEL_STEP_3_DIV_10_RESET
        elif encrypted_count % 3 == 0:
            self.wheels[2] = WHEEL_STEP_3_DIV_3_RESET
        else:
            self.wheels[2] = WHEEL_STEP_3_DEFAULT

    def encrypt(self, message):
        if not message:
            return ""
        original_wheels = self.wheels.copy()
        encrypted_word = ''
        encrypted_count = 0
        for c in message:
            new_letter, if_encrypted = self.encrypt_letter(c)
            if if_encrypted:
                encrypted_count += 1
            encrypted_word += new_letter
            self.forward_wheels(encrypted_count)
        
        self.wheels = original_wheels
        return encrypted_word


def load_enigma_from_path(path):
    try:
        with open(path, 'r') as file:
            data = json.load(file)
        return Enigma(data["hash_map"], data["wheels"], data["reflector_map"])
    except Exception as e:
        raise JSONFileException("Failed to load file")


def exit_with_message(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def get_args():
    args = sys.argv
    config_path, input_path, output_path = None, None, None
    for i in range(1, len(args), 2):
        if args[i] not in {'-i', '-o', '-c'}:
            exit_with_message(USAGE_ERROR_MESSAGE)
        if i + 1 >= len(args):
            exit_with_message(USAGE_ERROR_MESSAGE)
        
        flag, path = args[i], args[i + 1]
        if flag == '-c':
            config_path = path
        if flag == '-i':
            input_path = path
        if flag == '-o':
            output_path = path
    
    if not config_path or not input_path:
        exit_with_message(USAGE_ERROR_MESSAGE)
    
    return config_path, input_path, output_path


def main():
    config_path, input_path, output_path = get_args()
    try:
        enigma = load_enigma_from_path(config_path)
        output_file_content = ""
        with open(input_path, "r") as file:
            for line in file:
                clean_line = line.rstrip('\n')
                output_file_content += enigma.encrypt(clean_line)
                output_file_content += NEWLINE
        
        if output_path:
            with open(output_path, "w") as file:
                file.write(output_file_content)
        else:
            print(output_file_content)
    except Exception as e:
        exit_with_message(ENIGMA_ERROR_MESSAGE)


if __name__ == "__main__":
    main()
