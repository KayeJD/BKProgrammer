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
        self.data_queue = queue.Queue()
        self.list_queue = queue.Queue()

    def update_stored_lists(self):
        for i in range(1, 6):
            self.list_programmer.restore_list(i)

    def send_list_params(self):
        if (dpg.get_value('input_slowrate') == 'High-rate (A/us)'):
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


def main():
    app = App()
    dpg.create_context()
    dpg.create_viewport(title='BK Programmer', width=900, height=700, min_width=900, min_height=600)
    dpg.configure_app(manual_callback_management=True)
    dpg.setup_dearpygui()


    def _on_close(sender):
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
                with dpg.group(horizontal=True):
                    dpg.add_text('SlowRate: ')
                    dpg.add_combo(("High-rate (A/us)", "Low-rate (A/ms)"), tag='input_slowrate')
                with dpg.group(horizontal=True):
                    dpg.add_text('Range: ')
                    dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, max_clamped=True, tag='input_range')
                with dpg.group(horizontal=True):
                    dpg.add_text('Count: ')
                    dpg.add_input_int(min_value=0, max_value=65536, min_clamped=True, max_clamped=True, tag='input_count')
                with dpg.group(horizontal=True):
                    dpg.add_text('Step: ')
                    dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, max_clamped=True, tag='input_step')
                with dpg.group(horizontal=True):
                    dpg.add_text('Level: ')
                    dpg.add_input_int(min_value=0, max_value=84, min_clamped=True, max_clamped=True, tag='input_level')
                with dpg.group(horizontal=True):
                    dpg.add_text('Width(s): ')
                    dpg.add_input_float(before='(s)', min_value=0, min_clamped=True, tag='input_width')
                with dpg.group(horizontal=True):
                    dpg.add_text('Slew: ')
                    dpg.add_input_int(tag='input_slew')
                with dpg.group(horizontal=True):
                    dpg.add_button(tag='run_list', label='Run',
                                   callback=app.send_list_params)
                    dpg.add_button(tag='save_list', label='Save', callback=app.list_programmer.save_list)
                    # dpg.add_button(tag='retrieve_list', label='Restore', callback=app.restore_list)
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

                        with dpg.table(header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True) as saved_list_1:
                            dpg.add_table_column(label="List 1")
                            dpg.add_table_column(label="Value")
                            with dpg.table_row():
                                dpg.add_text('SlowRate')
                                # dpg.add_text(f'{self.controller.inst.query("LIST:SLOWrate?")}')
                            with dpg.table_row():
                                dpg.add_text('Range')
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Count')
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Step')
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Level')
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Width')
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Slew')
                                dpg.add_text('SlowRate')

                        with dpg.table(header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True) as saved_list_2:
                            dpg.add_table_column(label="List 2")
                            dpg.add_table_column(label="Value")
                            with dpg.table_row():
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Range')
                            with dpg.table_row():
                                dpg.add_text('Count')
                            with dpg.table_row():
                                dpg.add_text('Step')
                            with dpg.table_row():
                                dpg.add_text('Level')
                            with dpg.table_row():
                                dpg.add_text('Width')
                            with dpg.table_row():
                                dpg.add_text('Slew')

                        with dpg.table(header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True) as saved_list_3:
                            dpg.add_table_column(label="List 3")
                            dpg.add_table_column(label="Value")
                            with dpg.table_row():
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Range')
                            with dpg.table_row():
                                dpg.add_text('Count')
                            with dpg.table_row():
                                dpg.add_text('Step')
                            with dpg.table_row():
                                dpg.add_text('Level')
                            with dpg.table_row():
                                dpg.add_text('Width')
                            with dpg.table_row():
                                dpg.add_text('Slew')

                        with dpg.table(header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True) as saved_list_4:
                            dpg.add_table_column(label="List 4")
                            dpg.add_table_column(label="Value")
                            with dpg.table_row():
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Range')
                            with dpg.table_row():
                                dpg.add_text('Count')
                            with dpg.table_row():
                                dpg.add_text('Step')
                            with dpg.table_row():
                                dpg.add_text('Level')
                            with dpg.table_row():
                                dpg.add_text('Width')
                            with dpg.table_row():
                                dpg.add_text('Slew')

                        with dpg.table(header_row=True, row_background=True,
                                       borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                       borders_outerV=True, delay_search=True) as saved_list_5:
                            dpg.add_table_column(label="List 5")
                            dpg.add_table_column(label="Value")
                            with dpg.table_row():
                                dpg.add_text('SlowRate')
                            with dpg.table_row():
                                dpg.add_text('Range')
                            with dpg.table_row():
                                dpg.add_text('Count')
                            with dpg.table_row():
                                dpg.add_text('Step')
                            with dpg.table_row():
                                dpg.add_text('Level')
                            with dpg.table_row():
                                dpg.add_text('Width')
                            with dpg.table_row():
                                dpg.add_text('Slew')

        # with dpg.popup(dpg.last_item(), tag='error_modal', modal=True,
        #                mousebutton=dpg.mvMouseButton_Left):
        #     with dpg.group():
        #         dpg.add_text('this is an error')
        #         dpg.add_spacer()
        #         dpg.add_button(label="OK", width=75,
        #                        callback=lambda: dpg.configure_item("error_modal",
        #                                                                show=False))

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