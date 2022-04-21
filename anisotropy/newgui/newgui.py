import dearpygui.dearpygui as dpg
import pathlib

import geometry


gui_path = pathlib.Path(__file__).resolve().parent
dpg.create_context()


with dpg.font_registry():
    print(gui_path)
    default_font = dpg.add_font(gui_path / "fonts/NotoSansMono-Regular-Nerd-Font-Complete.ttf", 20)



with dpg.window(tag = "Primary") as primary:
    dpg.bind_font(default_font)

    with dpg.menu_bar(tag = "m1"):
        with dpg.menu(label = "File"):
            dpg.add_menu_item(label = "Preferences", callback = lambda: dpg.configure_item("preferences", show = True))
            dpg.add_menu_item(label = "Exit", callback = lambda: dpg.destroy_context())

        with dpg.menu(label = "Tools"):
            dpg.add_menu_item(label = "Geometry", callback = lambda: dpg.show_item("geometry"))
            dpg.add_menu_item(label = "Mesh", callback = lambda: dpg.show_item("mesh"))
            dpg.add_menu_item(label = "Solver", callback = lambda: dpg.show_item("solver"))
            dpg.add_menu_item(label = "Runner", callback = lambda: dpg.show_item("runner"))
            dpg.add_separator()
            dpg.add_menu_item(label = "Database", callback = lambda: dpg.show_item("database"))
            dpg.add_menu_item(label = "Post-processing", callback = lambda: dpg.show_item("post-processing"))

    with dpg.child_window(tag = "Test22", border = False, height = -40):
        
        with dpg.child_window(tag = "Test", border = False):
            with dpg.tab_bar(label = "tabbar"):
                with dpg.tab(label = "Geometry", tag = "geometry", closable = True, show = False):
                    geometry.create_geometry("geometry")

                with dpg.item_handler_registry(tag="widget handler"):
                    dpg.add_item_edited_handler(callback = lambda: dpg.delete_item("mesh") if not dpg.is_item_shown("mesh") else None)

                with dpg.tab(label = "Mesh", tag = "mesh", closable = True, show = False):
                    with dpg.child_window(tag = "mesh_container", border = True):
                        dpg.add_text("")
                
                # bind item handler registry to item
                dpg.bind_item_handler_registry("mesh", "widget handler")

                with dpg.tab(label = "Solver", tag = "solver", closable = True, show = False):
                    with dpg.child_window(tag = "solver_container", border = True):
                        dpg.add_text("")
                
                with dpg.tab(label = "Runner", tag = "runner", closable = True, show = False):
                    with dpg.child_window(tag = "runner_container", border = True):
                        dpg.add_text("")
                
                with dpg.tab(label = "Database", tag = "database", closable = True, show = False):
                    with dpg.child_window(tag = "database_container", border = True):
                        dpg.add_text("")

                with dpg.tab(label = "Post-processing", tag = "post-processing", closable = True, show = False):
                    with dpg.child_window(tag = "post-processing_container", border = True):
                        dpg.add_text("")
    
    dpg.add_separator()
    with dpg.table(tag = "statusbar", header_row = False):
        dpg.add_table_column(label = "")
        dpg.add_table_column(label = "")

        with dpg.table_row():
            dpg.add_button(label = "Debug", callback = lambda: print(dpg.get_value("mesh")))
            dpg.add_text("status")

with dpg.window(label = "Preferences", tag = "preferences", modal = True, show = False, width = 400, height = 600):
    with dpg.collapsing_header(label = "General"):
        with dpg.group(horizontal = True):
            dpg.add_text("Font")
            dpg.add_text(dpg.get_item_font("Primary"))

dpg.create_viewport(title = "New GUI", width = 1000, height = 800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary", True)
dpg.start_dearpygui()

dpg.destroy_context()
