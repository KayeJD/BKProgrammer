import pyvisa as visa
import sys
import time
import queue

list_queue = None

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
        self.inst = MockInstrument()

    def connect(self):
        print("Connected to: Mock Instrument")

    def check_connection(self):
        print(f"Connected to: {self.inst.idn}")

    def disconnect(self):
        print("Disconnected from Mock Instrument")


class ListProgrammer:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.range = 0
        self.count = 0
        self.step = 0
        self.level = 0
        self.slowRate = 0
        self.slew = 0.0
        self.width = 0.0


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


    def read_load_list(self):
        print("\n---- Session List Settings ----")
        print(f'Slow Rate: {self.controller.inst.query("LIST:SLOWrate?")}', end="")
        print(f'Range: {self.controller.inst.query("LIST:RANGe?")}', end="")
        print(f'Count: {self.controller.inst.query("LIST:COUNt?")}', end="")
        print(f'Steps: {self.controller.inst.query("LIST:STEP?")}', end="")

        for i in range(1, self.step + 1):
            print(f'Step {i}: ', end="")
            print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}', end="\t")
            print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}', end="\t")
            print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")


    def write_list_params(self):
        # self.controller.inst.write(f'LIST:RCL 1')
        # print(self.controller.inst.query('STAT:QUES:COND?'))

        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        self.controller.inst.write(f"LIST:STEP {self.step}")

        for i in range(1, self.step + 1):
            level_inc = float((self.range / self.step) * i)
            self.controller.inst.write(f"LIST:LEVel {i}, {level_inc:.2f}")
            print(f"LIST:LEVel {i}, {level_inc:.2f}".replace("\n", " "), end="\t")
            self.error_check()

            self.controller.inst.write(f"LIST:SLEW {i}, {self.slew:.2f}")
            print(f"LIST:SLEW {i}, {self.slew}".replace("\n", " "), end="\t")
            self.error_check()

            self.controller.inst.write(f"LIST:WIDth {i}, {self.width}")
            print(f"LIST:WIDth {i}, {self.width}".replace("\n", " "), end="\t")
            self.error_check()

        print("\n***DONE writing list to load")
        self.controller.inst.write(f'LIST:SAV 1')


    def read_all_load_lists(self):
        for location in range(1, 6):
            print(f'\n--- MEMORY LOCATION [{location}] ---')
            print(f'Slow Rate: {self.controller.inst.query("LIST:SLOWrate?")}', end="")
            print(f'Range: {self.controller.inst.query("LIST:RANGe?")}', end="")
            print(f'Count: {self.controller.inst.query("LIST:COUNt?")}', end="")
            print(f'Steps: {self.controller.inst.query("LIST:STEP?")}', end="")

            # all steps
            for i in range(1, int(self.step) + 1):
                print(f'Step {i}: ', end='')
                print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}', end="\t")
                print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}', end="\t")
                print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")


    def restore_list(self, location):
        self.controller.inst.write(f'LIST:RCL {location}')
        self.range = self.controller.inst.query(f"LIST:RANGe?")
        self.slowRate = self.controller.inst.query(f"LIST:SLOWrate?")
        self.count = self.controller.inst.query(f"LIST:COUNt?")
        self.step = self.controller.inst.query(f"LIST:STEP?")
        self.level = self.controller.inst.query(f"LIST:LEVel? 1")
        self.width = self.controller.inst.query(f"LIST:WIDth? 1")
        self.slew = self.controller.inst.query(f"LIST:SLEW? 1")

        return self.range, self.slowRate, self.count, self.step, self.level, self.width, self.slew


    def save_list(self, location):
        self.controller.inst.write(f'LIST:SAV {location}')


    def run_list(self):
        self.controller.inst.write('FUNCtion:MODE LIST')
        print(self.controller.inst.query('FUNC:MODE?'))

        self.controller.inst.write('TRIG:SOUR BUS')
        self.controller.inst.write("INPUT ON")
        self.controller.inst.write('*TRG')
        print(self.controller.inst.query('STAT:OPER:COND?'))  # get stat bit

        self.controller.inst.write('*WAI')
        self.controller.inst.write("INPUT OFF")
        self.controller.inst.write("FUNC:MODE FIX")


    def error_check(self):
        print(self.controller.inst.query('SYSTem:ERRor?'))


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
    global list_queue


if __name__ == "__main__":
    main()