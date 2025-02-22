import time

class MockInstrument:
    def __init__(self):
        self.params = {
            "LIST:SLOWrate": 0,
            "LIST:RANGe": 10,
            "LIST:COUNt": 100,
            "LIST:STEP": 5000,
            "LIST:LEVel": [1, 2, 3, 4, 5],
            "LIST:SLEW": [0, 1, 0, 1, 0],
            "LIST:WIDth": [10, 20, 30, 40, 50]
        }

    def query(self, command):
        if command in self.params:
            if isinstance(self.params[command], list):
                return ', '.join(map(str, self.params[command]))
            return str(self.params[command])
        return "Unknown command"

    def write(self, command):
        # Simulate writing to the instrument
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

    def get_list_params(self, txt_file_path):
        params_approved = True

        try:
            with open(txt_file_path, 'r') as file:
                for line in file:
                    words = line.split()
                    if len(words) < 2:
                        continue

                    param_name = words[0].lower()
                    param_value = int(words[1])

                    # SLOWRATE
                    if param_name == "slowrate":
                        if param_value in (0, 1):
                            self.slowRate = float(param_value)
                        else:
                            print("SLOWRATE requires: 0 (High-rate (A/us) or 1 Slew: Low-rate (A/ms)")
                            params_approved = False

                    # RANGE
                    elif param_name == "range":
                        if 0 < param_value < 85:
                            self.range = float(param_value)
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
                            self.width = float(param_value)
                        else:
                            print("WIDTH: Check Param Values")
                            params_approved = False

                    # SLEW
                    elif param_name == "slew":
                        if param_value > 0:
                            self.slew = float(param_value)
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
            print(f'Range: {self.range}')
            print(f'Count: {self.count}')
            print(f'Step: {self.step}')
            print(f'Level: {self.level}')
            print(f'Slew: {self.slew}')
            print(f'Width: {self.width}')
        else:
            print('***ERROR: One or more invalid values were provided.')

    def read_load_list(self):
        print("\n---- Session List Settings ----")
        print(f'Slow Rate: {self.controller.inst.query("LIST:SLOWrate?")}', end="")
        print(f'Range: {self.controller.inst.query("LIST:RANGe?")}', end="")
        print(f'Count: {self.controller.inst.query("LIST:COUNt?")}', end="")
        print(f'Steps: {self.controller.inst.query("LIST:STEP?")}', end="")

        for i in range(1, int(self.step) + 1):
            print(f'Step {i}: ', end="")
            print(f'Level={self.controller.inst.query(f"LIST:LEVel? {i}")}', end="\t")
            print(f'Width={self.controller.inst.query(f"LIST:WIDth? {i}")}', end="\t")
            print(f'Slew={self.controller.inst.query(f"LIST:SLEW? {i}")}', end="")

    def set_list_params(self):
        self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
        self.controller.inst.write(f"LIST:RANGe {self.range}")
        self.controller.inst.write(f"LIST:COUNt {self.count}")
        self.controller.inst.write(f"LIST:STEP {self.step}")

        for i in range(1, int(self.step) + 1):
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

    def restore_list(self, location): 
        print(f"Restoring list from location {location}...")
        self.read_load_list()

    def save_list(self, location):
        print(f"Saving list to location {location}...")

    def run_list(self):
        print("Running current Session List...")

    def error_check(self):
        print("No errors detected.")

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
    print("\n===== Debugging Options =====")
    print("1. Send direct commands")
    print("2. Read Error")
    print("3. Reset")
    print("4. Back to Main Menu")
    print("===============================")

def main():
    controller = Controller()
    controller.connect()
    list_programmer = ListProgrammer(controller)
    list_programmer.get_list_params("test_params.txt")

    while True:
        print_main_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            controller.check_connection()  

        elif choice == '2':
            while True:
                print_parameter_menu()
                param_choice = input("Select an option (1-5): ").strip()

                if param_choice == '1':
                    list_programmer.get_list_params("test_params.txt")

                elif param_choice == '2': 
                    list_programmer.set_list_params()

                elif param_choice == '3':
                    save_location = input("Select a save location (1-5): ")
                    try: 
                        save_location = int(save_location)
                        if 1 <= save_location <= 5:
                            list_programmer.save_list(save_location)
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

        elif choice == '4':
            list_programmer.read_all_load_lists()

        elif choice == '0':
            while True:
                debug_menu()
                debug_choice = input("Select an option (1-4): ").strip()
                if debug_choice == "1":
                    command = input("Type in entire command to .write: ").strip()
                    controller.inst.write(command)
                elif debug_choice == "2":
                    list_programmer.error_check()
                elif debug_choice == "3":
                    list_programmer.reset()
                elif debug_choice == "4":
                    break
                else:
                    print("Invalid input. Please try again.")

        elif choice == '5':
            controller.disconnect()
            return False

        else:
            print("Invalid input. Retry.\n")

if __name__ == "__main__":
    main()