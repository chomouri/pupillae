# MVP
import os, sys

import psycopg2
import dearpygui.dearpygui as dpg
from PIL import Image

from conf import config
import fons_pg

# pregenerate ids
scale_button = dpg.generate_uuid()
photo_window = dpg.generate_uuid()

# Global variables, config.py params, postgres details
selected_image = ""
display_image_button = 0
scale_image_button = 0
scale_size = (400, 400)
fons_params = config.config(section="fons_gui")

# Get postgreSQL tables and headers/details for each table, compose dictionary
# Use a composite class for this in the future.
# ^^^ ref: https://realpython.com/inheritance-composition-python/
# ^^^ ref: https://docs.python.org/3/tutorial/classes.html
fons = fons_pg.connect("fons_pg")
conn = psycopg2.connect(**fons)

# As luck would have it, the default tables are best sorted alphabetically
TABLES = sorted(fons_pg.get_tables(conn))
FOREIGN_KEYS = fons_pg.get_fk_details(conn)
pupillae = {}
for table in TABLES:
    col_details = map(list, fons_pg.get_col_details(conn, table))

    table_name = [table]
    table_values = {}
    for detail in col_details:
        col_name = [detail.pop(0)]
        col_keys = ('type', 'len', 'default_value')
        col_values = [dict(list(map(tuple, zip(col_keys, detail))))]
        table_values.update(zip(col_name, col_values))
    table_values = [table_values]
    pupillae.update(zip(table_name, table_values))
# print("full dict:", pupillae)
for row in FOREIGN_KEYS.values():
    for table in pupillae.keys():
        if row["fk_column"] in pupillae[table].keys() and row["foreign_table"] == table:
            pupillae[table][row["fk_column"]]["default_value"] = "FK"
            print("FK found in:", table, "->", row["fk_column"])

if conn is not None:
    conn.close()
    print("Database connection closed.")

# This should use the comm_id_dict and the IDs stored for the SUBMIT/REFRESH button.
def delete_image_buttons():
    if display_image_button:
        dpg.delete_item(display_image_button)
    if scale_image_button:
        dpg.delete_item(scale_image_button)

def scale_image(sender):
    global selected_image
    infile = selected_image
    outfile = os.path.split(selected_image)[0] + "/sm/sm_" + os.path.split(selected_image)[1]
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                im.thumbnail(scale_size)
                im.save(outfile, "JPEG")
                selected_image = outfile
        except OSError:
            print("cannot create thumbnail for", infile)
    # Use a proper arg for this function or fix it so it recieves the file as user_data="file"
    print(sender)
    display_photo(31)

def display_photo(sender):
    width, height, channels, data = dpg.load_image(selected_image)
    with dpg.texture_registry():
        texture_id = dpg.add_static_texture(width, height, data)
    with dpg.window(label="Selected Image", pos=[0,260]):
        dpg.add_image(texture_id)

def add_selected_image_buttons():
    global display_image_button, scale_image_button
    display_image_button = dpg.add_button(label="Display Image", callback=display_photo, parent=photo_window, user_data=selected_image)
    scale_image_button = dpg.add_button(label="Scale Image", callback=scale_image, parent=photo_window)

def select_image(sender, app_data, user_data):
    global selected_image
    file = os.path.join(app_data['current_path'], app_data['file_name_buffer'])
    selected_image = file
    add_selected_image_buttons()
    return

def submit_psql(sender, app_data, user_data):
    query_dict = {}
    for table, value in win_id_dict.items():
        query_dict[table] = {}
        # print("TABLE =", table, "ID =", value["id"])
        for column, id in value["fields"].items():
            query_dict[table][column] = dpg.get_value(id)
            # print("COLUMN =", column, "ID = ", id)
            # print("VALUE =", dpg.get_value(id))
    pg_response = fons_pg.compose_psql(query_dict)
    print(pg_response)
    dpg.set_item_label(comm_id_dict.get("READY"), "SUCCESS")
    delete_image_buttons()

def refresh_psql(sender, app_data, user_data):
    dpg.set_item_label(comm_id_dict.get("READY"), "READY")

with dpg.file_dialog(
    label="Photo Selector", width=400, height=400, directory_selector=False, show=False, callback=select_image, default_path=fons_params["photo_path"]) as file_dialog_id:
    dpg.add_file_extension(".*", color=(255, 255, 255, 255))
    dpg.add_file_extension(".png", color=(255, 255, 0, 255))
    dpg.add_file_extension(".cr2", color=(255, 0, 0, 255))
    dpg.add_file_extension(".jpg", color=(0, 255, 0, 255))

comm_id_dict = {}
with dpg.window(label="Photo", id=photo_window, width=410, height=260):
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Find...", callback=lambda: dpg.show_item(file_dialog_id))
    dpg.add_button(label="SUBMIT", width=410, height=50, callback=submit_psql)
    comm_id_dict["SUBMIT"] = dpg.last_item()
    dpg.add_button(label="READY", width=410, height=50)
    comm_id_dict["READY"] = dpg.last_item()
    dpg.add_button(label="REFRESH", width=410, height=50, callback=refresh_psql)
    comm_id_dict["REFRESH"] = dpg.last_item()

# Show PG Insert Tables:
win_id_dict = {}
prev_win_height = 0
for table, columns in pupillae.items():
    default_coord = (410, 0)
    column_counter = 0
    max_display_col = 2
    win_height = 50+(30*len(columns)/2)
    with dpg.window(label=table, width=890, height=win_height, pos=[default_coord[0], prev_win_height]):
        prev_win_height += win_height
        win_id_dict[table] = {}
        win_id_dict[table]["id"] = dpg.last_item()
        dpg.add_checkbox(label="Persist", default_value=True)
        win_id_dict[table]["Persist"] = dpg.last_item()
        dpg.add_same_line()
        dpg.add_checkbox(label="Submit", default_value=False)
        win_id_dict[table]["Submit"] = dpg.last_item()
        win_id_dict[table]["fields"] = {}
        for column, col_details in columns.items():
            column_counter += 1
            dpg.add_text(f"{column}", wrap=800)
            dpg.add_same_line()
            if col_details['type'] == "bool":
                dpg.add_checkbox(label="")
            if col_details['type'] == "int4":
                if col_details.get('default_value') != None and col_details.get('default_value').endswith("_seq'::regclass)"):
                    dpg.add_input_text(label="", hint="(Primary Key)", readonly=True, width=100)
                elif pupillae[table] != None and col_details.get('default_value') == "FK":
                    dpg.add_input_text(label="(Foreign Key)", hint="(auto)", width=100)
                else:
                    dpg.add_input_int(label="", step=0, width=85)
            if col_details['type'] == "varchar":
                dpg.add_input_text(label="", width=250)
            win_id_dict[table]["fields"][column] = dpg.last_item()
            if column_counter % max_display_col:
                dpg.add_same_line()

# print(dpg.get_item_children(33))
# test_list = dpg.get_item_children(33)[1]
# for i in test_list:
#     print(dpg.get_item_configuration(i))

#print(win_id_dict)
# print(pupillae)

# Viewport parameters.
dpg.setup_viewport()
dpg.set_viewport_title("Fons: PostgreSQL")
dpg.set_viewport_width(1300)
dpg.set_viewport_height(700)
dpg.start_dearpygui()
