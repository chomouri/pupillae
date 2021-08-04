# MVP
import os, sys

import psycopg2
import dearpygui.dearpygui as dpg
from PIL import Image

from conf import config
import fons_pg
import fons_img

# pregenerate ids
photo_window = dpg.generate_uuid()

# Global variables, config.py params, postgres details
gui_params = config.config(section="fons_gui")
logs = {}
log_template = {"insert": "alpha format"}
comm_id_dict = {}
win_id_dict = {}
pupillae = {}
img_dict = {"status": "setup_req"}
img_dict.update(gui_params)

# Get postgreSQL tables and headers/details for each table, compose dictionary
# Use a composite class for this in the future(?).
# ^^^ ref: https://realpython.com/inheritance-composition-python/
# ^^^ ref: https://docs.python.org/3/tutorial/classes.html
fons = fons_pg.connect("fons_pg")
conn = psycopg2.connect(**fons)


def display_scaled_image(sender, app_data, user_data):
    print("Scaling image...")
    global img_dict
    img_dict["selected_image"] = os.path.join(
        app_data['current_path'], app_data['file_name_buffer'])
    img_dict["status"] = "scaled_req"
    img_dict = fons_img.process_photo(img_dict)

    if img_dict["status"] == "Image Scaled...":
        width, height, channels, data = dpg.load_image(img_dict["scaled_image"])
        if comm_id_dict.get("selected_image_window"):
            dpg.delete_item(comm_id_dict["selected_image_window"])
        with dpg.texture_registry():
            texture_id = dpg.add_static_texture(width, height, data)
            with dpg.window(label="Selected Image", pos=[0,260]):
                comm_id_dict["selected_image_window"] = dpg.last_item()
                dpg.add_image(texture_id)
    dpg.set_item_label(
        comm_id_dict.get("image_status"), img_dict["status"])

def compose_p_sql(sender, app_data, user_data):
    global img_dict
    print("Composing SQL query...")
    query_dict = {}
    submit_requested = False
    photo_submitted = False
    for table, value in win_id_dict.items():
        if dpg.get_value(value["Submit"]):
            print(f"Composing query for {table}...")
            query_dict[table] = {}
            submit_requested = True
            for column, id in value["fields"].items():
                query_dict[table][column] = dpg.get_value(id)
            if query_dict[table].get("photo") == "(selected)":
                photo_submitted = True
                print("Photo Submission is Linked")

    if submit_requested:
        print("Submitting query...")
        pg_response = fons_pg.submit_p_sql(conn, query_dict, fkey_dict, logs["insert"])
# Show Submitted SQL:
        for submission, response in pg_response.items():
            dpg.set_value(comm_id_dict.get(f"{submission} response:"), response)
# Ideally, get the PK-FK values from the fk_dict for the image file name.
            if all(isinstance(i, int) for i in response[0:2]):
                img_dict["table_pk_fk"] = response[0:2]
                if photo_submitted:
                    print(f"Processing image using ID: {img_dict['table_pk_fk']}...")
                    img_dict["status"] = "save_req"
                    img_dict = fons_img.process_photo(img_dict)

    dpg.set_item_label(comm_id_dict.get("image_status"), img_dict["status"])
    dpg.set_item_label(comm_id_dict.get("query_status"), "Select Image...")

print("Initialising directory structure...")
config.initialise_dirs(gui_params)
print("Initialising logs...")
print(gui_params["log_dir"], log_template)
logs = config.initialise_logs(gui_params["log_dir"], log_template)


# As luck would have it, the default tables are best sorted alphabetically
print("Building GUI dictionaries from database...")
tables = sorted(fons_pg.get_tables(conn))
fkey_dict = fons_pg.get_fk_details(conn)

for table in tables:
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
for row in fkey_dict.values():
    for table in pupillae.keys():
        if row["fk_column"] in pupillae[table].keys() and row["foreign_table"] == table:
            pupillae[table][row["fk_column"]]["default_value"] = "FK"
            print("FK found in:", table, "->", row["fk_column"])

print("Initialising Image Dictionary...")
img_dict = fons_img.process_photo(img_dict)
print(img_dict["status"])

print("Assembling Windows and Widgets..")
with dpg.file_dialog(
    label="Photo Selector", width=400, height=400, directory_selector=False, show=False, callback=display_scaled_image, default_path=gui_params["photo_path_dir"]) as file_dialog_id:
    dpg.add_file_extension(".*", color=(255, 255, 255, 255))
    dpg.add_file_extension(".png", color=(255, 255, 0, 255))
    dpg.add_file_extension(".cr2", color=(255, 0, 0, 255))
    dpg.add_file_extension(".jpg", color=(0, 255, 0, 255))

with dpg.window(label="Photo", id=photo_window, width=410, height=260):
    dpg.add_button(label="SUBMIT", width=410, height=50, callback=compose_p_sql)
    comm_id_dict["SUBMIT"] = dpg.last_item()
    dpg.add_button(label="Select Image...", width=410, height=50,
        callback=lambda: dpg.show_item(file_dialog_id))
    comm_id_dict["query_status"] = dpg.last_item()
    dpg.add_button(label="IMAGE UNDOCUMENTED", width=410, height=50)
    comm_id_dict["image_status"] = dpg.last_item()

# Show PG Insert Tables:
prev_win_height = 0
for table, columns in pupillae.items():
    default_coord = (410, 0)
    column_counter = 0
    max_display_col = 2
    win_height = 80+(30*len(columns)/2)
    win_width = 890
    with dpg.window(label=table, width=win_width, height=win_height, pos=[default_coord[0], prev_win_height]):
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
            dpg.add_text(f"{column}", wrap=win_width-10)
            dpg.add_same_line()
            if col_details['type'] == "bool":
                dpg.add_checkbox(label="")
            if col_details['type'] == "int4":
                if col_details.get('default_value') != None and col_details.get('default_value').endswith("_seq'::regclass)"):
                    dpg.add_input_text(label="", default_value="(Primary Key)", readonly=True, width=100)
                elif pupillae[table] != None and col_details.get('default_value') == "FK":
                    dpg.add_input_text(label="(Foreign Key)", default_value="(auto)", width=100)
                else:
                    dpg.add_input_int(label="", step=0, width=85)
            if col_details['type'] == "varchar":
# This block will cause problems with other default values.
                if pupillae[table] != None and col_details.get('default_value') == "'(selected)'::character varying":
                    dpg.add_input_text(label="(save to path...)", default_value="(selected)", width=250)
                else:
                    dpg.add_input_text(label="", width=250)
            win_id_dict[table]["fields"][column] = dpg.last_item()
            if column_counter % max_display_col:
                dpg.add_same_line()
# Assuming max_display_col == 2:
        dpg.add_dummy()
        dpg.add_text("", label="Line_Break")
        dpg.add_text(f" {table} INSERT:  ", wrap=win_width-10)
        dpg.add_same_line()
        dpg.add_text(f"WAITING...", wrap=win_width-10)
        comm_id_dict[f"{table} response:"] = dpg.last_item()

# Viewport parameters.
dpg.setup_viewport()
dpg.set_viewport_title("Fons: PostgreSQL")
dpg.set_viewport_width(1300)
dpg.set_viewport_height(700)
try:
    print("Starting GUI...")
    dpg.start_dearpygui()
except (Exception, psycopg2.DatabaseError, psycopg2.Error) as e:
    print(e)
finally:
    if conn is not None:
        conn.close()
        print("Database connection closed.")
