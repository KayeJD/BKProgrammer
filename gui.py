import dearpygui.dearpygui as dpg
from app import App
from callbacks import *
from constants import *


app = App()
dpg.create_context()
dpg.create_viewport(title='BK Programmer', width=900, height=700, min_width=900, min_height=600)
dpg.configure_app(manual_callback_management=True)
dpg.setup_dearpygui()

chartx = []
charty = []
chart_unit = ''


def _on_close(sender, user_data):
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
                                      tag='shape', width=-1, callback=update_manual_configs, user_data=app)

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
