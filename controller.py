# look up commands
""" SCPI COMMANDS
========================================================================================================================
.write
    -
    -

.query
    -
    -

.read
    -
    -
========================================================================================================================
"""

import pyvisa as visa
import sys
import time

fake_inst = True
if fake_inst:
    list_queue = None
    inst_memory = {
        '1':{'ra': 0, 'sr': 0, 'co': 0, 'st': 0, 'le': 0, 'wi': 0.0, 'sl': 0.0},
        '2':{'ra': 0, 'sr': 0, 'co': 0, 'st': 0, 'le': 0, 'wi': 0.0, 'sl': 0.0},
        '3':{'ra': 0, 'sr': 0, 'co': 0, 'st': 0, 'le': 0, 'wi': 0.0, 'sl': 0.0},
        '4':{'ra': 0, 'sr': 0, 'co': 0, 'st': 0, 'le': 0, 'wi': 0.0, 'sl': 0.0},
        '5':{'ra': 0, 'sr': 0, 'co': 0, 'st': 0, 'le': 0, 'wi': 0.0, 'sl': 0.0}
    }

class MockInstrument:
    def __init__(self):
        self.idn = "Mock Instrument"

    def query(self, command):
        if 'LIST:RCL' in command:
            memory = command[-1]
            print(f'\n Recalled location {memory}')
        else:
            print(f"Mock query: {command}")

    def write(self, command):
        if 'LIST:RCL' in command:
            memory = command[-1]
            print(f'\n Recalled location {memory}')
        else:
            print(f"Mock write: {command}")

    def read(self):
        return "Mock read response"

class Controller:
    def __init__(self):
        if not fake_inst:
            self.rm = visa.ResourceManager()
            self.inst = None
            self.idn = None
        else:
            self.inst = MockInstrument()

    def connect(self):
        if not fake_inst:
            i = 1
            while True:
                try:
                    li = self.rm.list_resources()
                    for index in range(len(li)):
                        print(str(index) + " : " + li[index])
                    choice = input("Which Device?: ")
                    self.inst = self.rm.open_resource(li[int(choice)])
                    break
                except:
                    print(f"({i}) No connection Found.")
                    i += 1
                    time.sleep(2)
        else:
            print("Connected to: Mock Instrument")

    def check_connection(self):
        if not fake_inst:
            self.idn = self.inst.query("*IDN?")
            try:
                if self.idn:
                    print(f"Connected to: {self.idn}")
            except ConnectionError:
                print("Instrument could not be identified.")
        else:
            print(f"Connected to: {self.inst.idn}")

    def disconnect(self):
        if not fake_inst:
            self.inst.close()
        else:
            print("Disconnected from Mock Instrument")


class ListProgrammer:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.range = 0
        self.count = 0
        self.step = 2
        self.level = 0
        self.slowRate = 0
        self.slew = 0.0
        self.width = 0.0

        # self.range = None
        # self.slowRate = None
        # self.count = None
        # self.step = None
        # self.level = None
        # self.width = None
        # self.slew = None

    def get_list_params(self, txt_file_path):
        params_approved = True

        try:
            with open(txt_file_path, 'r') as file:
                for line in file:
                    words = line.split()
                    if len(words) < 2:
                        continue

                    param_name = words[0].lower()
                    param_value = float(words[1])

                    # SLOWRATE
                    if param_name == "slowrate":
                        if param_value in (0, 1):
                            self.slowRate = int(param_value)
                        else:
                            print("SLOWRATE requires: 0 (High-rate (A/us) or 1 Slew: Low-rate (A/ms)")
                            params_approved = False

                    # RANGE
                    elif param_name == "range":
                        if 0 < param_value < 85:
                            self.range = int(param_value)
                        else:
                            print("RANGE requires: 0 < x < 85")
                            params_approved = False

                    # COUNT
                    elif param_name == "count":
                        if 0 < param_value < 65536:
                            self.count = int(param_value)
                        else:
                            print("COUNT requires: 0 < x < 65536")
                            params_approved = False

                    # STEP
                    elif param_name == "step":
                        if 0 < param_value < 85:
                            self.step = int(param_value)
                        else:
                            print("STEP: Value needs to be 0 < x < 85")
                            params_approved = False

                    # LEVEL
                    elif param_name == "level":
                        if 0 < param_value < 85:
                            self.level = float(param_value)
                        else:
                            print("LEVEL requires: 0 < x < 85")
                            params_approved = False

                    # WIDTH
                    elif param_name == "width":
                        if param_value > 0:
                            self.width = param_value
                        else:
                            print("WIDTH: Check Param Values")
                            params_approved = False

                    # SLEW
                    elif param_name == "slew":
                        if param_value > 0:
                            self.slew = param_value
                        else:
                            print("SLEW: Check Param Values")
                            params_approved = False

        except FileNotFoundError:
            print("File not found.")
            return

        if params_approved:
            print("\n---- Retrieved .txt List Parameters ----")
            if self.slowRate == 0:
                print('Slew: High-rate (A/us)')
            else:
                print('Slew: Low-rate (A/ms)')
            print(f'Range: {self.range} \t Count: {self.count} \t Step: {self.step} \t '
                  f'Level: {self.level} \t Slew: {self.slew} \t Width: {self.width} \n')
        else:
            print('ERROR: One or more invalid values were provided.')


# FAKE_INST ************************************************************************************************************
    def set_list_params(self, input_range, count, step, level, slowRate, slew, width):
        self.range = input_range
        self.count = count
        self.step = step
        self.level = level
        self.slowRate = slowRate
        self.slew = slew # f'{slew:.2f}'
        self.width = width # f'{width:.2f}'

        print("\n---- Set List Parameters ----")
        if self.slowRate == 0:
            print('Slew: High-rate (A/us)')
        else:
            print('Slew: Low-rate (A/ms)')
        print(f'Range: {self.range} \t Count: {self.count} \t Step: {self.step} \t Level: {self.level} \t '
              f'Slew: {self.slew} \t Width: {self.width} \n')
# **********************************************************************************************************************


    def read_load_list(self):
        if not fake_inst:
            print("\n---- Session List Settings ----")
            print(f'Slow Rate: {self.controller.inst.query(f"LIST:SLOWrate?")}', end="")
            print(f'Range: {self.controller.inst.query(f"LIST:RANGe?")}', end="")
            print(f'Count: {self.controller.inst.query(f"LIST:COUNt?")}', end="")
            print(f'Steps: {self.controller.inst.query(f"LIST:STEP?")}', end="")

            for i in range(1, int(self.step) + 1):
                print(f'Step {i}: '.replace("\n", " "), end="\t")
                print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}'.replace("\n", " "), end="\t")
                print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}'.replace("\n", " "), end="\t")
                print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")


    def write_list_params(self):
        print('\n...WRITING SETTINGS TO CURRENT LIST...')
        # self.controller.inst.write(f'LIST:RCL 1')
        # print(self.controller.inst.query('STAT:QUES:COND?'))

        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        self.controller.inst.write(f"LIST:STEP {self.step}")

        for i in range(1, self.step + 1):
            print(f'Step {i}: ')
            level_inc = (self.range / self.step) * i

            self.controller.inst.write(f"LIST:LEVel {i}, {level_inc:.2f}")
            self.controller.inst.write(f"LIST:SLEW {i}, {self.slew:.2f}")
            self.controller.inst.write(f"LIST:WIDth {i}, {self.width:.2f}")
            self.controller.inst.query('*OPC?')

        self.controller.inst.write(f'LIST:SAV 1')

    def read_all_load_lists(self):
        for location in range(1, 6):
            self.controller.inst.write(f'LIST:RCL {location}')
            print(f'\n--- MEMORY LOCATION [{location}] ---')
            print(f'Slow Rate: {self.controller.inst.query(f"LIST:SLOWrate?")}', end="")
            print(f'Range: {self.controller.inst.query(f"LIST:RANGe?")}', end="")
            print(f'Count: {self.controller.inst.query(f"LIST:COUNt?")}', end="")
            print(f'Steps: {self.controller.inst.query(f"LIST:STEP?")}', end="")

            for i in range(1, int(self.step) + 1):
                print(f'Step {i}: ', end='')
                print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}'
                      .replace("\n", " "), end="\t")
                print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}'
                      .replace("\n", " "), end="\t")
                print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")

    def restore_list(self, location):
        print('\n...RESTORING LIST IN LOCATION...')
        self.controller.inst.write(f'LIST:RCL {location}')
        self.range = self.controller.inst.query(f"LIST:RANGe?")
        self.slowRate = self.controller.inst.query(f"LIST:SLOWrate?")
        self.count = self.controller.inst.query(f"LIST:COUNt?")
        self.step = self.controller.inst.query(f"LIST:STEP?")
        self.level = self.controller.inst.query(f"LIST:LEVel? 1")
        self.width = self.controller.inst.query(f"LIST:WIDth? 1")
        self.slew = self.controller.inst.query(f"LIST:SLEW? 1")

        if fake_inst:
            return self.range, self.slowRate, self.count, self.step, self.level, self.width, self.slew

    def run_list(self):
        print('\n...NOW TRIGGERING RUN LIST...')
        self.controller.inst.write('FUNCtion:MODE LIST')
        print(self.controller.inst.query('FUNC:MODE?'))
        self.controller.inst.write('TRIG:SOUR BUS')
        self.controller.inst.write("INPUT ON")
        self.controller.inst.write('*TRG')
        print(self.controller.inst.query('STAT:OPER:COND?')) # get stat bit
        self.controller.inst.write('*WAI')
        self.controller.inst.write("input off")
        self.controller.inst.write("func:mode fix")

    def error_check(self):
        print(self.controller.inst.query('SYSTem:ERRor?'))

    def save_list(self, location):
        if not fake_inst:
            self.controller.inst.write(f'LIST:SAV {location}')
        else:
            self.controller.inst.write(f'LIST:SAV {location}')

    def reset(self):
        print(self.controller.inst.query('*TST?'))
        self.error_check()
        self.controller.inst.write('*RCL 0')
        self.controller.inst.write('*CLS')
        self.error_check()


def print_main_menu():
    print("\n=========== BK Precision 8625 ============")
    print("Please select an option from the menu below:")
    print("1. Check connection")
    print("2. Parameter Configuration")
    print("3. Execution Options")
    print("4. See all saved Lists")
    print("5. Exit")
    print("0. DEBUGGING")
    print("============================================")


def print_parameter_menu():
    print("\n===== Parameter Configuration =====")
    print("1. Load Parameters from File")
    print("2. Set Parameters to Session")
    print("3. Save Parameters to Memory")
    print("4. Restore Parameters from Memory")
    print("5. Back to Main Menu")
    print("===================================")


def print_execution_menu():
    print("\n===== Execution Options =====")
    print("1. Run Current Session List")
    print("2. Read Current Settings")
    print("3. Back to Main Menu")
    print("===============================")


def debug_menu():
    print("\n===== Execution Options =====")
    print("1. Send direct commands")
    print("2. Read Error")
    print("3. Reset")
    print("4. Back to Main Menu")
    print("===============================")


def main():
    if not fake_inst:
        controller = Controller()
        controller.connect()
        list_programmer = ListProgrammer(controller)
        list_programmer.get_list_params("test_params.txt")

        while True:
            print_main_menu()
            choice = input("Select an option (1-5): ").strip()

            if choice == '1':
                try:
                    controller.check_connection()
                except Exception as e:
                    print(f"Disconnected. Unplug and plug again. {e}")
                    controller.disconnect()
                    controller.connect()

            elif choice == '2':
                while True:
                    print_parameter_menu()
                    param_choice = input("Select an option (1-5): ").strip()

                    if param_choice == '1':
                        list_programmer.get_list_params("test_params.txt")
                    elif param_choice == '2':
                        list_programmer.write_list_params()
                    elif param_choice == '3':
                        save_location = input("Select a save location (1-5): ")
                        try:
                            save_location = int(save_location)
                            if 1 <= save_location <= 5:
                                list_programmer.save_list(save_location)
                                print("***DONE writing list to load")
                            else:
                                print("Invalid memory location. Retry.\n")
                        except:
                            print("Invalid memory location. Retry.\n")
                    elif param_choice == '4':
                        retrieval_location = input("Select a location to retrieve (1-5): ")
                        try:
                            retrieval_location = int(retrieval_location)
                            if 1 <= retrieval_location <= 5:
                                list_programmer.restore_list(retrieval_location)
                            else:
                                print("Invalid memory location. Retry.\n")
                        except:
                            print("Invalid memory location. Retry.\n")
                    elif param_choice == '5':
                        break
                    else:
                        print("Invalid input. Please try again.")

            elif choice == '3':
                while True:
                    print_execution_menu()
                    exec_choice = input("Select an option (1-3): ").strip()
                    if exec_choice == '1':
                        list_programmer.run_list()
                    elif exec_choice == '2':
                        list_programmer.read_load_list()
                    elif exec_choice == '3':
                        break
                    else:
                        print("Invalid input. Please try again.")

            elif choice == '4':  # TODO: save the current session details bc it might bet overwritten
                list_programmer.read_all_load_lists()

            elif choice == '0':
                while True:
                    debug_menu()
                    choice = input("Select an option (1-4): ").strip()
                    if choice == "1":
                        print("1. Write \t 2.Read \t 3. Query \t 4. Back")
                        choice = input("Select an option (1-3): ").strip()
                        if choice == '1':
                            command = input("Type in entire command to .write: ").strip()
                            print(controller.inst.write(command))
                        elif choice == '2':
                            print(controller.inst.read())
                        elif choice == '3':
                            command = input("Type in entire command to .query: ").strip()
                            print(controller.inst.query(command))
                        elif choice == '4':
                            break
                        else:
                            print("Invalid input. Please try again.")
                    elif choice == "2":
                        list_programmer.error_check()
                    elif choice == "3":
                        list_programmer.reset()
                    else:
                        break

            elif choice == '5':
                controller.disconnect()
                return False

            else:
                print("Invalid input. Retry.\n")


if __name__ == "__main__":
    main()
