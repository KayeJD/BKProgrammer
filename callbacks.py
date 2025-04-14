import dearpygui.dearpygui as dpg
import time
import pandas as pd
import numpy as np
from datetime import datetime as dt
from constants import *


# def run_task():
#     global running
#     global paused
#     global progress
#     print("Running...")
#
#     for i in range(1, 101):
#         while paused:
#             time.sleep(0.1)
#         if not running:
#             return
#         progress = i
#         print(i)
#         dpg.set_value(progress_bar, 1 / 100 * (i))
#         dpg.configure_item(progress_bar, overlay=f"{i}%")
#         time.sleep(0.05)
#
#     print("Finished")
#     running = False
#
#
# def reset_callback():
#     global running
#     global paused
#     global progress
#     running = False
#     paused = False
#     progress = 0
#     dpg.set_value(progress_bar, 0)
#     dpg.configure_item(progress_bar, overlay="0%")


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
    app = user_data

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
