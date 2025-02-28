import pyvisa as visa
import sys
import time
import queue

list_queue = None

class MockInstrument:
    def __init__(self):
        self.params = {
            "LIST:SLOWrate": 0,
            "LIST:RANGe": 10,
            "LIST:COUNt": 100,
            "LIST:STEP": 5000,
            "LIST:LEVel": 4,
            "LIST:SLEW": 1,
            "LIST:WIDth": 50
        }

    def query(self, command):
        if command in self.params:
            if isinstance(self.params[command], list):
                return ', '.join(map(str, self.params[command]))
            return str(self.params[command])
        return "Unknown command"

    def write(self, command):
        print(f"Mock write: {command}")

    def read(self):
        return "Mock read response"

class Controller:
    def __init__(self):
        self.inst = MockInstrument()
        self.idn = "Mock Instrument"

    def connect(self):
        print("Connected to: Mock Instrument")

    def check_connection(self):
        print(f"Connected to: {self.idn}")

    def disconnect(self):
        print("Disconnected from Mock Instrument")

class ListProgrammer:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.range = None
        self.count = None
        self.step = None
        self.level = None
        self.slowRate = None
        self.slew = None
        self.width = None

    def set_list_params(self, input_range, count, step, level, slowRate, slew, width):
        self.range = input_range
        self.count = count
        self.step = step
        self.level = level
        self.slowRate = slowRate
        self.slew = slew
        self.width = width

        print("\n---- Set List Parameters ----")
        if self.slowRate == 0:
            print('Slew: High-rate (A/us)')
        else:
            print('Slew: Low-rate (A/ms)')
        print(f'Range: {self.range}')
        print(f'Count: {self.count}')
        print(f'Step: {self.step}')
        print(f'Level: {self.level}')
        print(f'Slew: {self.slew}')
        print(f'Width: {self.width}')

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
        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        self.controller.inst.write(f"LIST:STEP {self.step}")

        for i in range(1, self.step + 1):
            level_inc = float((self.range / self.step) * i)
            self.controller.inst.write(f"LIST:LEVel {i}, {level_inc}")
            self.controller.inst.write(f"LIST:SLEW {i}, {self.slew}")
            self.controller.inst.write(f"LIST:WIDth {i}, {self.width}")
            # print(f"LIST:LEVel {i}, {level_inc:.1f}")

        print("\n***DONE writing list to load")

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

        for location in range(1, 6):
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

        list_queue.put(self.controller.inst.query(f"LIST:RANGe?"))
        # self.read_load_list(location)

    def save_list(self, location):
        self.controller.inst.write(f'LIST:SAV {location}')

    def run_list(self):
        self.controller.inst.write('FUNCtion:MODE LIST')
        self.controller.inst.write('TRIG:SOUR BUS')
        self.controller.inst.write('*TRG')

    def error_check(self):
        print(self.controller.inst.query('SYSTem:ERRor?'))

    def reset(self):
        print(self.controller.inst.query('*TST?'))

    def reset(self):
        print("Resetting the instrument...")


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
    # controller = Controller()
    # controller.connect()
    # list_programmer = ListProgrammer(controller)
    # list_programmer.controller.inst.write("List:Func 1")
    # list_programmer.get_list_params("test_params.txt")

    # while True:
    #     print_main_menu()
    #     choice = input("Select an option (1-5): ").strip()

        # if choice == '1':
        #     try:
        #         controller.check_connection()
        #     except Exception as e:
        #         print(f"Disconnected. Unplug and plug again. {e}")
        #         controller.disconnect()
        #         controller.connect()
        #
        # elif choice == '2':
        #     while True:
        #         print_parameter_menu()
        #         param_choice = input("Select an option (1-5): ").strip()
        #
        #         if param_choice == '1':
        #             list_programmer.get_list_params("test_params.txt")
        #         elif param_choice == '2':
        #             list_programmer.set_list_params()
        #         elif param_choice == '3':
        #             save_location = input("Select a save location (1-5): ")
        #             try:
        #                 save_location = int(save_location)
        #                 if 1 <= save_location and save_location <= 5:
        #                     list_programmer.save_list(save_location)
        #                     print("***DONE writing list to load")
        #                 else:
        #                     print("Invalid memory location. Retry.\n")
        #             except:
        #                 print("Invalid memory location. Retry.\n")
        #         elif param_choice == '4':
        #             retrieval_location = input("Select a location to retrieve (1-5): ")
        #             try:
        #                 retrieval_location = int(retrieval_location)
        #                 if 1 <= retrieval_location and retrieval_location <= 5:
        #                     list_programmer.restore_list(retrieval_location)
        #                 else:
        #                     print("Invalid memory location. Retry.\n")
        #             except:
        #                 print("Invalid memory location. Retry.\n")
        #         elif param_choice == '5':
        #             break
        #         else:
        #             print("Invalid input. Please try again.")
        #
        # elif choice == '3':
        #     while True:
        #         print_execution_menu()
        #         exec_choice = input("Select an option (1-3): ").strip()
        #         if exec_choice == '1':
        #             list_programmer.run_list()
        #         elif exec_choice == '2':
        #             list_programmer.read_load_list()
        #         elif exec_choice == '3':
        #             break
        #         else:
        #             print("Invalid input. Please try again.")
        #
        # elif choice == '4':  # TODO: save the current session details bc it might bet overwritten
        #     list_programmer.read_all_load_lists()
        #
        # elif choice == '0':
        #     while True:
        #         debug_menu()
        #         choice = input("Select an option (1-4): ").strip()
        #         if choice == "1":
        #             print("1. Write \t 2.Read \t 3. Query \t 4. Back")
        #             choice = input("Select an option (1-3): ").strip()
        #             if choice == '1':
        #                 command = input("Type in entire command to .write: ").strip()
        #                 print(controller.inst.write(command))
        #             elif choice == '2':
        #                 print(controller.inst.read())
        #             elif choice == '3':
        #                 command = input("Type in entire command to .query: ").strip()
        #                 print(controller.inst.query(command))
        #             elif choice == '4':
        #                 break
        #             else:
        #                 print("Invalid input. Please try again.")
        #         elif choice == "2":
        #             list_programmer.error_check()
        #         elif choice == "3":
        #             list_programmer.reset()
        #         else:
        #             break
        #
        # elif choice == '5':
        #     controller.disconnect()
        #     return False
        #
        # else:
        #     print("Invalid input. Retry.\n")

if __name__ == "__main__":
    main()