import sys
import dearpygui.dearpygui as dpg
import queue
import threading

import controllerTest # controllerTest: fake controller

class App:
    def __init__(self):
        self.controller = controllerTest.Controller()
        self.controller.connect()
        self.list_programmer = controllerTest.ListProgrammer(self.controller)
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

        # self.thread = threading.Thread(target=self.read_instrument_data, daemon=True)
        # self.thread.start()
        
        # TODO: update stored lists 1-5

    # Get data from continuous thread running
    # def read_instrument_data(self):
    #     while self.running:
    #         # response = self.controller.send_command("MEASure:CURRent?")  # Example SCPI command
    #         # self.data_queue.put(response)
    #         print('Read thread running')

    # When the SAVED tab is opened, update all of the lists
    def update_stored_lists(self):
        for i in range(1, 6):
            ra, sl, co, st, le, wi, sl = self.list_programmer.restore_list(i) # The list parameters

            # for item in dpg.get_item_children(f'saved_list_{i}', slot=1):
            #     dpg.delete_item(item)
            #
            with dpg.table_row(parent=f'saved_list_{i}'):
                dpg.add_text('SlowRate')
                dpg.add_text(sl)
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
            #write

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

    # stop ongoing app threads
    def stop(self):
        self.running = False
        self.thread.join()


def main():
    app = App()
    dpg.create_context()
    dpg.create_viewport(title='BK Programmer', width=900, height=700, min_width=900, min_height=600)
    dpg.configure_app(manual_callback_management=True)
    dpg.setup_dearpygui()

    def _on_close(sender):
        app.stop()
        dpg.delete_item(sender, children_only=True)
        dpg.delete_item(sender)

    with dpg.window(tag='dashboard_window', menubar=True, on_close=_on_close):
        with dpg.menu_bar():
            with dpg.menu(label="Connect to Device"):
                dpg.add_menu_item(tag='return_to_menu_button', label='Connect')

            dpg.add_separator()

            dpg.add_text('Status:')
            # dpg.add_text(tag='extraction_status')

        with dpg.group(horizontal=True, width=0):
            with dpg.child_window(tag='left_container', width=250):
                dpg.add_text('CURRENT WORKING LIST')
                with dpg.table(header_row=False, row_background=False,
                               borders_innerH=False, borders_outerH=False, borders_innerV=False,
                               borders_outerV=False, delay_search=True) as saved_list_1:
                    dpg.add_table_column(width_fixed=True)
                    dpg.add_table_column()
                    with dpg.table_row():
                        dpg.add_text('SlowRate: ')
                        dpg.add_combo(("High-rate (A/us)", "Low-rate (A/ms)"), default_value="Low-rate (A/ms)",
                                      tag='input_slowrate')
                    with dpg.table_row():
                        dpg.add_text('Range: ')
                        dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, default_value=app.input_range,
                                          max_clamped=True, tag='input_range')
                    with dpg.table_row():
                        dpg.add_text('Count: ')
                        dpg.add_input_int(min_value=0, max_value=65536, min_clamped=True, default_value=app.input_count,
                                          max_clamped=True, tag='input_count')
                    with dpg.table_row():
                        dpg.add_text('Step: ')
                        dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, default_value=app.input_step,
                                          max_clamped=True, tag='input_step')
                    with dpg.table_row():
                        dpg.add_text('Level: ')
                        dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, default_value=app.input_level,
                                          max_clamped=True, tag='input_level')
                    with dpg.table_row():
                        dpg.add_text('Width(s): ')
                        dpg.add_input_float(min_value=0, min_clamped=True, tag='input_width', default_value=app.input_width)
                    with dpg.table_row():
                        dpg.add_text('Slew: ')
                        dpg.add_input_float(tag='input_slew', default_value=app.input_slew)
                with dpg.group(horizontal=True):
                    dpg.add_button(tag='run_list', label='Run',
                                   callback=app.run_list_params)
                    dpg.add_button(tag='save_list', label='Save', callback=app.list_programmer.save_list)
                    # dpg.add_button(tag='error', label='Error', callback=lambda: dpg.configure_item("error_modal", show=True))

            with dpg.child_window(tag='right_container', autosize_x=True):
                with dpg.tab_bar():
                    with dpg.tab(label="DATA"):
                        dpg.add_text('Charts: ')
                    with dpg.tab(label="SAVED LISTS"):
                        with dpg.group(horizontal=True):
                            dpg.add_text('Retrieve stored list: ')
                            dpg.add_combo(("1", "2", "3", "4", "5"), width=50, tag='restore_location')
                            dpg.add_button(tag='retrieve_list', label='Restore',
                                           callback=lambda: app.list_programmer.restore_list(
                                               dpg.get_value('restore_location')))

                        with dpg.table(tag='saved_list_1', header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True):
                            dpg.add_table_column(label="List 1")
                            dpg.add_table_column(label="Value")

                        with dpg.table(tag='saved_list_2', header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True):
                            dpg.add_table_column(label="List 2")
                            dpg.add_table_column(label="Value")

                        with dpg.table(tag='saved_list_3',header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True):
                            dpg.add_table_column(label="List 3")
                            dpg.add_table_column(label="Value")

                        with dpg.table(tag='saved_list_4',header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True):
                            dpg.add_table_column(label="List 4")
                            dpg.add_table_column(label="Value")

                        with dpg.table(tag='saved_list_5',header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True):
                            dpg.add_table_column(label="List 5")
                            dpg.add_table_column(label="Value")


        # with dpg.popup(dpg.last_item(), tag='error_modal', modal=True,
        #                mousebutton=dpg.mvMouseButton_Left):
        #     with dpg.group():
        #         dpg.add_text('this is an error')
        #         dpg.add_spacer()
        #         dpg.add_button(label="OK", width=75,
        #                        callback=lambda: dpg.configure_item("error_modal",
        #                                                                show=False))

    app.update_stored_lists()
    dpg.show_viewport()
    dpg.set_primary_window('dashboard_window', True)
    # dpg.set_viewport_resize_callback(resize_update_position)

    while dpg.is_dearpygui_running():
        jobs = dpg.get_callback_queue()  # retrieves and clears queue
        dpg.run_callbacks(jobs)
        dpg.render_dearpygui_frame()

    try:
        dpg.start_dearpygui()
    except KeyboardInterrupt:
        pass
    finally:
        dpg.stop_dearpygui()
        dpg.destroy_context()

if __name__ == '__main__':
    main()