import controller
import queue
import dearpygui.dearpygui as dpg
from constants import *


class App:
    def __init__(self):
        self.controller = controller.Controller()
        self.controller.connect()
        self.list_programmer = controller.ListProgrammer(self.controller)
        self.running = True

        self.data_queue = queue.Queue()
        self.list_queue = queue.Queue()
        self.error_log = queue.Queue()

        self.input_range = 0
        self.input_count = 0
        self.input_step = 0
        self.input_level = 0
        self.input_slowrate = 0
        self.input_slew = 0.0
        self.input_width = 0.0

        self.list_programmer.set_list_params(self.input_range, self.input_count, self.input_step, self.input_level,
                                             self.input_slowrate, self.input_slew, self.input_width)

        # self.thread = threading.Thread(target=self.read_instrument_data, daemon=True)
        # self.thread.start()

    # Get data from continuous thread running
    # def read_instrument_data(self):
    #     while self.running:
    #         # response = self.controller.send_command("MEASure:CURRent?")  # Example SCPI command
    #         # self.data_queue.put(response)
    #         print('Read thread running')

    # When the SAVED tab is opened, update all of the lists
    def update_stored_lists(self):
        if CONNECTION:
            for i in range(1, 6):
                # ra, sr, co, st, le, wi, sl = self.list_programmer.restore_list(i) # The list parameters
                ra, sr, co, st, le, wi, sl = 0, 0, 0, 0, 0, 0, 0

                for item in dpg.get_item_children(f'saved_list_{i}', slot=1):
                    dpg.delete_item(item)

                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('SlowRate')
                    dpg.add_text(sr)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Range')
                    dpg.add_text(ra)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Count')
                    dpg.add_text(co)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Step')
                    dpg.add_text(st)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Level')
                    dpg.add_text(le)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Width')
                    dpg.add_text(wi)
                with dpg.table_row(parent=f'saved_list_{i}'):
                    dpg.add_text('Slew')
                    dpg.add_text(sl)

                for j in range(100):
                    with dpg.table_row(parent=f'saved_list_1'):
                        dpg.add_text('Slew')
                        dpg.add_text('0')

                # write

            # while not self.list_queue.empty():
            #     response = self.list_queue.get()
            # dpg.set_value("instrument_data", f"Current: {response} A")  # Update GUI

            # dpg.render_dearpygui_frame()

    # Send backend the inputted parameters to self, write to machine, then run list
    def run_list_params(self):
        if dpg.get_value('input_slowrate') == 'High-rate (A/us)':
            input_slowrate = 0
        else:
            input_slowrate = 1
        self.list_programmer.set_list_params(dpg.get_value('input_range'),
                                             dpg.get_value('input_count'),
                                             dpg.get_value('input_step'),
                                             dpg.get_value('input_level'),
                                             input_slowrate,
                                             dpg.get_value('input_slew'),
                                             dpg.get_value('input_width'))

        self.list_programmer.write_list_params()
        self.list_programmer.run_list()

    def save_list(self, location):
        if dpg.get_value('input_slowrate') == 'High-rate (A/us)':
            input_slowrate = 0
        else:
            input_slowrate = 1

        self.input_range = dpg.get_value('input_range')
        self.input_count = dpg.get_value('input_count')
        self.input_step = dpg.get_value('input_step')
        self.input_level = dpg.get_value('input_level')
        self.input_slowrate = input_slowrate
        self.input_slew = dpg.get_value('input_slew')
        self.input_width = dpg.get_value('input_width')

        self.list_programmer.set_list_params(self.input_range, self.input_count, self.input_step, self.input_level,
                                             self.input_slowrate, self.input_slew, self.input_width)

        self.list_programmer.write_list_params()
        self.list_programmer.save_list(location)

        self.update_stored_lists()

    # stop ongoing app threads
    def stop(self):
        self.running = False
        self.thread.join()