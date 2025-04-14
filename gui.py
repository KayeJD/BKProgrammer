import sys
import dearpygui.dearpygui as dpg
import queue
import time
import os
import pandas as pd
import numpy as np
import threading
import controller
from datetime import datetime as dt
from math import sin, cos

DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')
CONNECTION = False
LIST_STATE = 'MANUAL'  # CSV, MANUAL...

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


app = App()
dpg.create_context()
dpg.create_viewport(title='BK Programmer', width=900, height=700, min_width=900, min_height=600)
dpg.configure_app(manual_callback_management=True)
dpg.setup_dearpygui()

running = False
paused = False
progress = 0

chartx = []
charty = []
chart_unit = ''


def run_task():
    global running
    global paused
    global progress
    print("Running...")

    for i in range(1, 101):
        while paused:
            time.sleep(0.1)
        if not running:
            return
        progress = i
        print(i)
        dpg.set_value(progress_bar, 1 / 100 * (i))
        dpg.configure_item(progress_bar, overlay=f"{i}%")
        time.sleep(0.05)

    print("Finished")
    running = False


def reset_callback():
    global running
    global paused
    global progress
    running = False
    paused = False
    progress = 0
    dpg.set_value(progress_bar, 0)
    dpg.configure_item(progress_bar, overlay="0%")


def save_file(sender, app_data, user_data):
    print("=== Save File button Clicked ===")
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data} \n")
    #
    # dicts = bms_data.dict_list
    #
    # print('DICTS LIST', dicts)
    # file_path_name = app_data['file_path_name']
    #
    # # Save the file here
    # if not os.path.exists(LOG_RECORDS_DIR):
    #     os.makedirs(LOG_RECORDS_DIR)
    #
    # with open(f'{file_path_name}', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     header_row = list(dicts[1].keys())  # Using the Keys as header titles
    #     writer.writerow(header_row)
    #     for key, value in dicts.items():
    #         data_row = list(value.values())
    #         writer.writerow(data_row)


def download_file(sender, app_data, user_data):
    default_filename = dt.now().strftime("%m-%d-%Y__%H_%M_%S")

    if dpg.does_item_exist("file_dialog_id"):
        print("File dialog is already open")
        dpg.configure_item("file_dialog_id", show=True)
        return

    with dpg.file_dialog(directory_selector=False, modal=True, callback=save_file, id="file_dialog_id",
                         default_filename=default_filename, default_path=DOWNLOADS_DIR, width=800, height=400):
        dpg.add_file_extension(".csv")
        dpg.add_file_extension(".txt")


def update_chart(chartx, charty, source_name):
    dpg.set_value('series_list', [chartx, charty])
    dpg.set_item_label('series_list', source_name)
    dpg.fit_axis_data('x_axis')
    dpg.fit_axis_data('y_axis')


def update_csv_table(data):
    for item in dpg.get_item_children('csv_table', slot=1):
        dpg.delete_item(item)

    for index, row in data.iterrows():
        with dpg.table_row(parent="csv_table"):
            with dpg.table_cell(): # step
                dpg.add_text(str(index + 1))
            for value in row.iloc[:3]:
                with dpg.table_cell():
                    dpg.add_text(str(value) if pd.notna(value) else "")


def create_csv_chart_data(sender, app_data):
    global chartx, charty, chart_unit
    chartx = []
    charty = []

    data = pd.read_csv(app_data['file_path_name'])
    update_csv_table(data)

    if int(data.at[0, 'slowrate']) == 1:
        chart_unit = '(ms)'
    else:
        chart_unit = '(us)'
    print(data)

    current_time = 0.0
    total_steps = int(data.at[0, 'step'])
    count = int(data.at[0, 'count'])

    for repeat in range(count):  # Repeat full step sequence
        for i in range(total_steps):
            level = float(data.at[i, 'level'])
            width = float(data.at[i, 'width'])
            slew = float(data.at[i, 'slew'])

            # Start of level
            chartx.append(current_time)
            charty.append(level)

            # End of level (pulse width)
            current_time += width
            chartx.append(current_time)
            charty.append(level)

            if i + 1 < total_steps:
                next_level = float(data.at[i + 1, 'level'])
                current_time += slew
                chartx.append(current_time)
                charty.append(next_level)

            # # Slew to next level if not last step
            # if i + 1 < total_steps:
            #     next_level = float(data.at[i + 1, 'level'])
            #     delta_I = abs(next_level - level)
            #
            #     if slew != 0:
            #         transition_time = delta_I / slew
            #     else:
            #         transition_time = 0.0
            #
            #     current_time += transition_time
            #     chartx.append(current_time)
            #     charty.append(next_level)

    print(chartx)
    print(charty)
    update_chart(chartx, charty, app_data['file_name'])


def create_manual_chart_data(steps, level, width, slew):
    global chartx, charty, chart_unit
    chartx = []
    charty = []

    # current_time = 0.0
    # print(steps, level, width, slew)
    # # for i in range(steps):
    # # level = float(level)
    # # width = float(width)
    # # slew = float(slew)
    #
    # for i in range(steps):
    #     chartx.append(current_time)
    #     charty.append(level)
    #
    #     # end of pulse
    #     current_time += width
    #     chartx.append(current_time)
    #     charty.append(level)
    #
    #     if i + 1 < steps:
    #         next_level = float(level)
    #         current_time += slew
    #         chartx.append(current_time)
    #         charty.append(next_level)
    #
    # update_chart(chartx, charty,'Manual Entry')


def generate_sine_dataframe(params):
    amp = params["amplitude"]
    offset = params["offset"]
    freq = params["frequency"]
    duration = params["duration"]
    slew = params["slew"]
    slowrate = params["slowrate"]
    rng = params["range"]
    count = params["count"]
    step_count = params["step_count"]

    time_steps = np.linspace(0, duration, step_count)
    levels = amp * np.sin(2 * np.pi * freq * time_steps) + offset
    widths = np.diff(time_steps, append=duration)  # width per step

    df = pd.DataFrame({
        "level": np.round(levels, 3),
        "slew": slew,
        "width": np.round(widths, 6),
    })

    # Add control parameters only to the first row
    df.loc[0, "slowrate"] = slowrate
    df.loc[0, "range"] = rng
    df.loc[0, "count"] = count
    df.loc[0, "step"] = step_count

    print(df)


def update_manual_configs(sender, app_data, user_data):
    print(app_data)
    for item in dpg.get_item_children('manual_configs', slot=1):
        print(item)
        dpg.delete_item(item)

    print("")
    dpg.render_dearpygui_frame()

    match app_data:
        case 'Square':
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Amplitude: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_level', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('High-level time: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_highwidth', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Low-level time: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_lowwidth', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Slew: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True,  default_value=app.input_level,
                                  max_clamped=True, tag='input_slew', width=-1)
        case 'Sin':
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Amplitude: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_level', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Offset: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_offset', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Frequency: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_frequency', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Duration: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_duration', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Count: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True, default_value=app.input_level,
                                      max_clamped=True, tag='input_count', width=-1)
        case 'Custom':
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Range: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=0, min_clamped=True, default_value=app.input_range,
                                  max_clamped=True, tag='input_range', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Count: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, max_value=65536, min_clamped=True,
                                  default_value=app.input_count,
                                  max_clamped=True, tag='input_count', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Step: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=2, max_value=83, min_clamped=True, default_value=app.input_step,
                                  max_clamped=True, tag='input_step', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Level: ')
                with dpg.table_cell():
                    dpg.add_input_int(min_value=1, min_clamped=True,
                                                    default_value=app.input_level,
                                                    max_clamped=True, tag='input_level', width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Width(s): ')
                with dpg.table_cell():
                    dpg.add_input_float(min_value=0, min_clamped=True, tag='input_width',
                                                      default_value=app.input_width, width=-1)
            with dpg.table_row(parent='manual_configs'):
                with dpg.table_cell():
                    dpg.add_text('Slew: ')
                with dpg.table_cell():
                    dpg.add_input_float(tag='input_slew', default_value=app.input_slew,
                                                     width=-1)


def _on_close(sender):
    app.stop()
    dpg.delete_item(sender, children_only=True)
    dpg.delete_item(sender)


with dpg.theme() as no_connection_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 1, 1), category=dpg.mvThemeCat_Core)

with dpg.file_dialog(directory_selector=False, show=False, callback=create_csv_chart_data, tag="file_dialog_tag", width=700,
                     height=400):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255))
    dpg.add_file_extension("")

with dpg.window(tag='dashboard_window', menubar=True, on_close=_on_close):
    with dpg.menu_bar():
        with dpg.menu(label="Connect to Device"):
            dpg.add_menu_item(tag='return_to_menu_button', label='Connect')
        dpg.add_separator()
        dpg.add_text('Status:')

    with dpg.group(horizontal=True, width=0):
        with dpg.child_window(tag='left_container', width=250):
            dpg.add_separator(label="LIST CONFIGURATION")
            with dpg.tab_bar():
                with dpg.tab(label="MANUAL mode"):
                    dpg.add_text("General Settings:")
                    with dpg.group(horizontal=True):
                        dpg.add_text('SlowRate: ')
                        dpg.add_combo(("High-rate (A/us)", "Low-rate (A/ms)"), default_value="Low-rate (A/ms)",
                                      tag='input_slowrate', width=-1)
                    with dpg.group(horizontal=True):
                        dpg.add_text('Shape: ')
                        dpg.add_combo(("Square", "Sin", "Custom"), default_value="",
                                      tag='shape', width=-1, callback=update_manual_configs)

                    dpg.add_separator()

                    with dpg.table(tag='manual_configs', header_row=False, row_background=False,
                                   borders_innerH=False, borders_outerH=False, borders_innerV=False,
                                   borders_outerV=False, delay_search=True):
                        dpg.add_table_column(width_fixed=True)
                        dpg.add_table_column()

                        with dpg.table_row():
                            dpg.add_text('Filler text')
                            dpg.add_combo(("1", "2"), width=-1)


                    dpg.add_button(label='Update Plot', width=-1,
                                   callback=create_manual_chart_data(app.input_step, app.input_level, app.input_width,
                                                              app.input_slew))

                # CSV table
                with dpg.tab(label="CSV mode"):
                    dpg.add_button(label='Select a .csv file', width=-1, callback=lambda:dpg.show_item("file_dialog_tag"))
                    dpg.add_separator()
                    dpg.add_text('Segments:')
                    with dpg.table(tag='csv_table', header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                                   borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True,
                                   scrollY=True, freeze_rows=1, height=300):
                        dpg.add_table_column(label='Step')
                        dpg.add_table_column(label='Level')
                        dpg.add_table_column(label='Slew')
                        dpg.add_table_column(label='Width')

            with dpg.group(horizontal=True, width=0):
                dpg.add_button(tag='run_list', label='Run', width=40)  # , callback=app.run_list_params)
                progress_bar = dpg.add_progress_bar(default_value=0, width=-1, overlay="0%")

            dpg.add_separator()

            dpg.add_text('SAVE LIST (?)')
            with dpg.tooltip(dpg.last_item()):
                dpg.add_text("Save Current Load Profile to Electronic Load")
            with dpg.group(horizontal=True):
                dpg.add_text('Slot:')
                dpg.add_combo(("1", "2", "3", "4", "5"), width=145, tag='')
                dpg.add_button(tag='save_list', label='Save', callback=app.save_list)
                # dpg.add_button(tag='error', label='Error', callback=lambda: dpg.configure_item("error_modal", show=True))

        with dpg.child_window(tag='right_container', autosize_x=True):
            dpg.add_separator(label="DATA")

            # sindatax = []
            # sindatay = []
            # cosdatay = []
            # for i in range(100):
            #     sindatax.append(i / 100)
            #     sindatay.append(0.5 + 0.5 * sin(50 * i / 100))
            #     cosdatay.append(0.5 + 0.75 * cos(50 * i / 100))
            with dpg.tab_bar():
                with dpg.tab(label="SELECTED LIST"):
                    # dpg.add_text('Charts: ')

                    def query(sender, app_data, user_data):
                        dpg.set_axis_limits("xaxis_tag2", app_data[0], app_data[1])
                        dpg.set_axis_limits("yaxis_tag2", app_data[2], app_data[3])

                    with dpg.plot(label="Full Load Profile", callback=query, query=True, height=250, width=-1):
                        dpg.add_plot_legend()

                        dpg.add_plot_axis(dpg.mvXAxis, label=f"Time {chart_unit}", tag='x_axis')  # TODO: UPDATE THE UNIT
                        dpg.add_plot_axis(dpg.mvYAxis, label="Current (A)", tag='y_axis')
                        dpg.add_line_series(chartx, charty, label=LIST_STATE, parent=dpg.last_item(), tag="series_list")
                        # dpg.add_stair_series(sindatax, sindatay, tag="stair_series", label="0.5 + 0.5 * sin(x)")

                    dpg.add_text('Information:')

                with dpg.tab(label="SAVED LISTS"):
                    if not CONNECTION:
                        c1 = dpg.add_text('NO MACHINE CONNECTION')
                        dpg.bind_item_theme(c1, no_connection_theme)
                    else:
                        with dpg.group(horizontal=True):
                            dpg.add_text('Retrieve stored list: ')
                            dpg.add_combo(("1", "2", "3", "4", "5"), width=50, tag='restore_location')
                            dpg.add_button(tag='retrieve_list', label='Restore', enabled=CONNECTION,
                                           callback=lambda: app.list_programmer.restore_list(
                                               dpg.get_value('restore_location')))

                        dpg.add_separator(label="LIST 1")
                        with dpg.group():
                            if not CONNECTION:
                                retrieval_availability = dpg.add_text('NO MACHINE CONNECTION')
                                dpg.bind_item_theme(retrieval_availability, no_connection_theme)
                            # dpg.add_button(label='Open .lists')
                            with dpg.table(tag='saved_list_1', header_row=False, row_background=False,
                                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                           borders_outerV=True, delay_search=True, scrollY=True, height=150):
                                dpg.add_table_column(label="List 1")
                                dpg.add_table_column(label="Value")

                        dpg.add_separator(label="LIST 2")
                        with dpg.group():
                            if not CONNECTION:
                                retrieval_availability = dpg.add_text('NO MACHINE CONNECTION')
                                dpg.bind_item_theme(retrieval_availability, no_connection_theme)
                            # dpg.add_button(label='Open .lists')
                            with dpg.table(tag='saved_list_2', header_row=False, row_background=False,
                                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                           borders_outerV=True, delay_search=True, scrollY=True, height=150):
                                dpg.add_table_column(label="List 2")
                                dpg.add_table_column(label="Value")

                        dpg.add_separator(label="LIST 3")
                        with dpg.group():
                            if not CONNECTION:
                                retrieval_availability = dpg.add_text('NO MACHINE CONNECTION')
                                dpg.bind_item_theme(retrieval_availability, no_connection_theme)
                            # dpg.add_button(label='Open .lists')
                            with dpg.table(tag='saved_list_3', header_row=False, row_background=False,
                                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                           borders_outerV=True, delay_search=True, scrollY=True, height=150):
                                dpg.add_table_column(label="List 3")
                                dpg.add_table_column(label="Value")

                        dpg.add_separator(label="LIST 4")
                        with dpg.group():
                            if not CONNECTION:
                                retrieval_availability = dpg.add_text('NO MACHINE CONNECTION')
                                dpg.bind_item_theme(retrieval_availability, no_connection_theme)
                            # dpg.add_button(label='Open .lists')
                            with dpg.table(tag='saved_list_4', header_row=False, row_background=False,
                                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                           borders_outerV=True, delay_search=True, scrollY=True, height=150):
                                dpg.add_table_column(label="List 4")
                                dpg.add_table_column(label="Value")

                        dpg.add_separator(label="LIST 5")
                        with dpg.group():
                            if not CONNECTION:
                                retrieval_availability = dpg.add_text('NO MACHINE CONNECTION')
                                dpg.bind_item_theme(retrieval_availability, no_connection_theme)
                            # dpg.add_button(label='Open .lists')
                            with dpg.table(tag='saved_list_5', header_row=False, row_background=False,
                                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                           borders_outerV=True, delay_search=True, scrollY=True, height=150):
                                dpg.add_table_column(label="List 5")
                                dpg.add_table_column(label="Value")

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
