""" SCPI COMMANDS
========================================================================================================================
.write
    -LIST:SLOWrate <0 or 1>
        - 0:High-rate(A/us)     1:Slow-rate(A/ms)
    -LIST:RANG <p>
        - p:0-max current
    -LIST:SLEW <step>, <p>
        - "slew" refers to the rate of change of current output,
        - essentially how quickly the output can transition from one level to another
        - determined by slowrate
    -LIST:COUNt <1 to 65536>
        - # of times a list will execute
        - 65536 = inf
    -LIST:STEP <2 to 83>
        - Divides the list to individual sections to differ LEVEL, SLEW, and WIDTH
        - making it to 84 will force it into fixed mode
    -LIST:LEV <1 to maxCurrRange>
        - 65536 = inf
    -LIST:WIDth <step>, <20us to 3600s>
        - length of each step.
        - unit is in seconds
.query (basically just a write and read in one. remember to print out)
    - remember to read back or else it'll throw queue interrupted error
========================================================================================================================
"""

import pyvisa as visa
import time
import threading
import os
# from pynput import keybaord
import pandas as pd

# FAKE_INST ************************************************************************************************************
fake_inst = False
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
            print(f"\n Recalled location {memory}")
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

    def close(self):
        pass
# **********************************************************************************************************************


class Controller:
    def __init__(self):
        if not fake_inst:
            self.rm = visa.ResourceManager()
            self.inst = None
            self.idn = None
            self.connection = False
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
                    self.connection = True
                    break
                except:
                    print(f"({i}) No connection Found.")
                    i += 1
                    time.sleep(2)
        else:
            print("Connected to: Mock Instrument")

    def check_connection(self):
        if not fake_inst:
            print(self.inst.query("*IDN?"))
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

        # Don't know which one of these to use yet
        self.stop_event = threading.Event()
        self.running = False

        self.range = 0
        self.count = 0
        self.step = 2
        self.level = 0.0
        self.slowRate = 0
        self.slew = 0.0
        self.width = 0.0
        self.txt_params_approved = False
        # self.list = [] # for .lists purposes

    def get_txt_list(self, txt_file_path):
        self.txt_params_approved = True

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
                            self.txt_params_approved = False

                    # RANGE
                    elif param_name == "range":
                        if 0 < param_value < 84:
                            self.range = int(param_value)
                        else:
                            print("RANGE requires: 0 < x < 84")
                            self.txt_params_approved = False

                    # COUNT
                    elif param_name == "count":
                        if 0 < param_value < 65536:
                            self.count = int(param_value)
                        else:
                            print("COUNT requires: 0 < x < 65536")
                            self.txt_params_approved = False

                    # STEP
                    elif param_name == "step":
                        if 1 < param_value < 84:
                            self.step = int(param_value)
                        else:
                            print("STEP: Value needs to be 1 < x < 84")
                            self.txt_params_approved = False

                    # LEVEL
                    elif param_name == "level":
                        if 0 < param_value < 85:
                            self.level = float(param_value)
                        else:
                            print("LEVEL requires: 0 < x < 85")
                            self.txt_params_approved = False

                    # WIDTH
                    elif param_name == "width":
                        if param_value > 0:
                            self.width = param_value
                        else:
                            print("WIDTH: Check Param Values")
                            self.txt_params_approved = False

                    # SLEW
                    elif param_name == "slew":
                        if param_value > 0:
                            self.slew = param_value
                        else:
                            print("SLEW: Check Param Values")
                            self.txt_params_approved = False

        except FileNotFoundError:
            print("File not found.")
            return

        if self.txt_params_approved:
            print("\n---- Retrieved .txt List Parameters ----")
            if self.slowRate == 0:
                print('Slew: High-rate (A/us)')
            else:
                print('Slew: Low-rate (A/ms)')
            print(f'Range: {self.range} \t Count: {self.count} \t Step: {self.step} \t '
                  f'Level: {self.level} \t Slew: {self.slew} \t Width: {self.width}s \n')
        else:
            print('ERROR: One or more invalid values were provided.')

    def get_csv_list(self, file_name):
        print('RETRIEVING CSV LIST...')
        file_path = f'lists/{file_name}.csv'

        if not os.path.exists(file_path):
            print(f"file not found: {file_path}.")
            return False

        df = pd.read_csv(file_path)
        df = df.reset_index()
        self.slowRate = df.loc[0, 'slowrate']
        self.range = df.loc[0, 'range']
        self.count = df.loc[0, 'count']
        self.step = df.loc[0, 'step']

        # SETTING TO LOAD
        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        print(f'LIST:SLOWrate {self.slowRate}')
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        print(f'LIST:RANGe {self.range}')
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        print(f'LIST:COUNt {self.count}')
        self.controller.inst.write(f"LIST:STEP {self.step}")
        print(f'LIST:STEP {self.step}')

        for index, row in df.iterrows():
            step = int(str(index)) + 1
            print(f'Step: {step}', end='\t') # Will be step

            print(f"LIST:LEVel {step}, {row['level']:.2f}", end='\t')
            print(f"LIST:SLEW {step}, {row['slew']:.2f}", end='\t')
            print(f"LIST:WIDth {step}, {row['width']:.5f}")
            level = f"{row['level']:.2f}"
            slew = f"{row['slew']:.2f}"
            width = f"{row['width']:.5f}"

            self.controller.inst.write(f"LIST:LEVel {step}, {level}")
            self.controller.inst.write(f"LIST:SLEW {step}, {slew}")
            self.controller.inst.write(f"LIST:WIDth {step}, {width}")
            self.controller.inst.write('*WAI')

        self.controller.inst.write(f'LIST:SAV 1')
        return True



# FAKE_INST ************************************************************************************************************
    def set_list_params(self, input_range, count, step, level, slowRate, slew, width):
        self.range = input_range
        self.count = count
        self.step = step
        self.level = level
        self.slowRate = slowRate
        self.slew = slew # f'{slew:.2f}'
        self.width = width # f'{width:.5f}'

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
            print("\n---------- Session List Settings ----------")
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
        print('\nWRITING SETTINGS TO CURRENT LIST...')
        # self.error_check()

        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        print(f'LIST:SLOWrate {self.slowRate}')
        # self.error_check()
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        print(f'LIST:RANGe {self.range}')
        # self.error_check()
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        print(f'LIST:COUNt {self.count}')
        # self.error_check()
        self.controller.inst.write(f"LIST:STEP {self.step}")
        print(f'LIST:STEP {self.step}')
        # self.error_check()

        for i in range(1, self.step + 1):
            print(f'Step {i}: ', end='\t')
            level_inc = (self.range / self.step) * i

            self.controller.inst.write(f"LIST:LEVel {i}, {self.level:.2f}")
            print(f'LIST:LEVel {i}, {self.level:.2f}', end='\t')
            self.controller.inst.write(f"LIST:SLEW {i}, {self.slew:.2f}")
            print(f"LIST:SLEW {i}, {self.slew:.2f}", end='\t')
            self.controller.inst.write(f"LIST:WIDth {i}, {self.width:.5f}")
            print(f"LIST:WIDth {i}, {self.width:.5f}")
            self.controller.inst.write('*WAI')
            # self.controller.inst.query('*OPC?')

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

        self.controller.inst.write(f"LIST:RANGe?")
        self.range = self.controller.inst.read()

        self.controller.inst.write(f"LIST:SLOW?")
        self.slowRate = self.controller.inst.read()

        self.controller.inst.write(f"LIST:COUNt?")
        self.count = self.controller.inst.read()

        self.controller.inst.write(f"LIST:STEP?")
        self.step = self.controller.inst.read()

        self.controller.inst.write(f"LIST:LEVel? 1")
        self.level = self.controller.inst.read()

        self.controller.inst.write(f"LIST:WIDth? 1")
        self.width = self.controller.inst.read()

        self.controller.inst.write(f"LIST:SLEW? 1")
        self.slew = self.controller.inst.read()

        print(self.slowRate, self.range, self.count, self.step, self.level, self.width, self.slew)

        if fake_inst:
            return self.range, self.slowRate, self.count, self.step, self.level, self.width, self.slew


    def save_to_csv(self, name):
        file_path = f'lists/{name}.csv'
        print('\nSAVING LIST TO CSV FILE...')

        if not os.path.exists(file_path):
            columns = ['level','slew','width','slowrate','range','count','step']
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)
            print(f"File '{file_path}' created.")
        else:
            f = open(file_path, "w+")
            f.close()
            columns = ['level', 'slew', 'width', 'slowrate', 'range', 'count', 'step']
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)

        df = pd.read_csv(file_path)
        df.loc[2, 'slowrate'] = self.slowRate
        df.loc[2, 'range'] = self.range
        df.loc[2, 'count'] = self.count
        df.loc[2, 'step'] = self.step
        for i in range(1, self.step + 1):
            df.loc[i, 'level'] = f'{self.level:.2f}'
            df.loc[i, 'slew'] = f'{self.slew:.2f}'
            df.loc[i, 'width'] = f'{self.width:.5f}'
        df.to_csv(file_path, index=False)

        print('\n.CSV FILE SAVED')


    def listen_for_input(self):
        while self.running:
            choice = input("Enter [0] to end: ").strip()
            if choice == '0':
                self.controller.inst.write('*CLS') # Clears instrument event register
                print("FINISHING PROCESS...")
                self.running = False
                self.stop_event.set()


    def run_list(self):
        self.controller.inst.write("list:rcl 1")

        print("\n---------- Session List Settings ----------")
        print(f'Slow Rate: {self.controller.inst.query(f"LIST:SLOWrate?")}', end="")
        print(f'Range: {self.controller.inst.query(f"LIST:RANGe?")}', end="")
        print(f'Count: {self.controller.inst.query(f"LIST:COUNt?")}', end="")
        print(f'Steps: {self.controller.inst.query(f"LIST:STEP?")}', end="")

        for i in range(1, int(self.step) + 1):
            print(f'Step {i}: '.replace("\n", " "), end="\t")
            print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}'.replace("\n", " "), end="\t")
            print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}'.replace("\n", " "), end="\t")
            print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")


        self.controller.inst.write("func:mode list")
        self.controller.inst.write('*WAI')
        print('Load now in following mode: ', end='')
        print(self.controller.inst.query('FUNC:MODE?'))

        print('\nNOW TRIGGERING RUN LIST...')
        self.controller.inst.write('TRIG:SOUR BUS')
        print(self.controller.inst.query('TRIGGER:SOURCE?'))
        self.controller.inst.write("INPUT ON")
        self.controller.inst.write('*WAI')
        self.controller.inst.write('*TRG')

        self.running = True
        input_thread = threading.Thread(target=self.listen_for_input, daemon=True)
        input_thread.start()

        execution_time = self.width * self.step * self.count
        # print(f'Runtime: {execution_time}s')
        # time.sleep(execution_time) # UNCOMMENT if disabling input_thread.

        self.controller.inst.write('*WAI')
        self.stop_event.set()
        self.running = False
        input_thread.join()

        self.controller.inst.write('*WAI')
        self.controller.inst.write("INPUT OFF")
        self.controller.inst.write("func:mode fix")
        print(self.controller.inst.query('*OPC?'))
        self.txt_params_approved = False
        print('DONE running list.')

        # try:
        #     execution_time = self.width * self.step * self.count
        #     print(execution_time)
        #     for i in range(math.ceil(execution_time)):
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     print('PROCESS INTERRUPTED...')
        # finally:
        #     self.controller.inst.write('*WAI')
        #     self.controller.inst.write("INPUT OFF")
        #     self.controller.inst.write("func:mode fix")
        #     print(self.controller.inst.query('*OPC?'))
        #     print('DONE running list.')


    def error_check(self):
        print(f"Self-test result: {self.controller.inst.query('*TST?')}", end='')
        self.controller.inst.write('*WAI')
        print(f"Error: {self.controller.inst.query('SYSTem:ERRor?')}")
        self.controller.inst.write('*WAI')


    def save_list(self, location):
        if 1 <= location <= 5:
            self.controller.inst.write(f'LIST:SAV {location}')
        else:
            print('Invalid input')


    def reset(self):
        self.error_check()
        self.controller.inst.write('*RCL 0')
        # self.controller.inst.write('*WAI')
        # self.controller.inst.write("*RST")
        # self.controller.inst.write('*WAI')
        self.controller.inst.write("*CLS")
        # self.controller.inst.write('*WAI')
        # self.controller.inst.write("*SRE 0")
        # self.controller.inst.write('*WAI')
        # self.controller.inst.write("*ESE 0")
        # self.controller.inst.write('*WAI')
        # self.error_check()


def print_main_menu():
    print("\n============ BK Precision 8625 =============")
    print("Please select an option from the menu below:")
    print("1. Check connection")
    print("2. Saving/Retrieving")
    print("3. Execution Options")
    print("4. See all saved Lists")
    print("5. Exit")
    print("0. DEBUGGING")
    print("============================================")


def print_parameter_menu():
    print("\n======= Saving/Retrieving =======")
    print("1. Save Current list to Load Memory")
    print("2. Save to a .csv file")
    print("3. Restore List from Load Memory")
    print("4. Back to Main Menu")
    print("=======================================")


def print_execution_menu():
    print("\n======== Execution Options ========")
    print("1. Run from test_params.txt file")
    print("2. Run from .csv file")
    print("3. Read Current Settings")
    print("4. Back to Main Menu")
    print("===================================")


def debug_menu():
    print("\n====== Execution Options ======")
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
        list_programmer.get_txt_list("test_params.txt")

        while True:
            print_main_menu()
            choice = input("Select an option (1-7): ").strip()

            # CHECK CONNECTION
            if choice == '1':
                try:
                    controller.check_connection()
                except Exception as e:
                    print(f"Disconnected. Unplug and plug again. {e}")
                    controller.disconnect()
                    controller.connect()

            # PARAMETER CONFIGURATION
            elif choice == '2':
                while True:
                    print_parameter_menu()
                    param_choice = input("Select an option (1-8): ").strip()

                    if param_choice == '1':
                        save_location = int(input("Select a save location (1-5): "))
                        if 1 <= save_location <= 5:
                            list_programmer.save_list(save_location)
                            print("***DONE writing list to load")
                        else:
                            print("Invalid memory location. Retry.\n")
                    elif param_choice == '2':
                        name = input("Name the .csv file: ")
                        list_programmer.save_to_csv(name)
                    elif param_choice == '3':
                        retrieval_location = int(input("Select a location to retrieve (1-5): "))
                        if 1 <= retrieval_location <= 5:
                            list_programmer.restore_list(retrieval_location)
                        else:
                            print("Invalid memory location. Retry.\n")
                    elif param_choice == '4':
                        break
                    else:
                        print("Invalid input. Please try again.")

            # EXECUTE LIST
            elif choice == '3':
                while True:
                    print_execution_menu()
                    exec_choice = input("Select an option (1-3): ").strip()
                    if exec_choice == '1':
                        list_programmer.get_txt_list("test_params.txt")
                        if list_programmer.txt_params_approved:
                            list_programmer.write_list_params()
                            list_programmer.run_list()
                        else:
                            print("Invalid parameters. Please try again.")
                    elif exec_choice == '2':
                        name = input("Type filename (exclude .csv): ")
                        exists = list_programmer.get_csv_list(name)
                        if exists:
                            list_programmer.run_list()
                    elif exec_choice == '3':
                        list_programmer.read_load_list()
                    elif exec_choice == '4':
                        break
                    else:
                        print("Invalid input. Please try again.")

            # READ ALL STORED LISTS
            elif choice == '4':
                list_programmer.read_all_load_lists()
                list_programmer.controller.inst.write(f'LIST:RCL 1')

            # DEBUGGING
            elif choice == '0':
                while True:
                    debug_menu()
                    choice = input("Select an option (1-4): ").strip()
                    if choice == "1":
                        while True:
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
                # list_programmer.reset()
                controller.disconnect()
                return False

            else:
                print("Invalid input. Retry.\n")


if __name__ == "__main__":
    main()
