import dearpygui.dearpygui as dpg

def create_geometry(parent):
    with dpg.child_window(
            tag = "geometry_container", 
            parent = parent
        ) as container:
            dpg.add_button(label = "Add case", callback = Case.create(container))
            with dpg.group(horizontal = True):
                dpg.add_text("Cases")
                dpg.add_separator()
        
    return container

class Case:
    case_list = []

    def __init__(self, parent):
        self.parent = parent
        self.uuid = dpg.generate_uuid()
        self.values = {}
        Case.case_list.append(self)
        

    def __str__(self):
        return f"<Case: { self.uuid }, type: geometry>"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def create(parent):
        def create_callback():
            case = Case(parent)

            with dpg.collapsing_header(label = f"g-case-{ case.uuid }", parent = case.parent) as case._case:
                with dpg.child_window(height = 300) as case.child_window:
                    with dpg.group(horizontal = True):
                        case._source = dpg.add_combo(["", "from file", "periodic"], label = "Source")
                        
                        dpg.add_button(label = "Remove", callback = case.remove_case)
                        dpg.add_button(label = "Edit", callback = case.edit_case)

                    case.create_stats()

            case.create_params_file()
            case.create_params_periodic()
        
        return create_callback
    
    def remove_case(self):
        dpg.delete_item(self._case)
        Case.case_list.remove(self)

    def edit_case(self):
        source_val = dpg.get_value(self._source)

        if source_val == "from file":
            dpg.show_item(self._file_params)
        
        elif source_val == "periodic":
            dpg.show_item(self._periodic_params)
    
    def create_stats(self):
        with dpg.table(header_row = True, parent = self.child_window) as self._case_stats:
            dpg.add_table_column(label = "Parameters")
            dpg.add_table_column(label = "")

            for k, v in self.values.items():
                with dpg.table_row():
                    dpg.add_text(k)
                    dpg.add_text(v)

    def update_stats(self):
        dpg.delete_item(self._case_stats)
        self.create_stats()

    def create_params_file(self):
        with dpg.window(show = False, modal = True, height = 600, width = 400) as self._file_params:
            with dpg.group(horizontal = True):
                self._file_input = dpg.add_input_text(label = "File")
                dpg.add_button(label = "..", callback = lambda: dpg.show_item(self._file_dialog))

                with dpg.file_dialog(
                    directory_selector = False, 
                    show = False, 
                    modal = True, 
                    callback = lambda s, d: dpg.set_value(self._file_input, d['file_path_name']), 
                    height = 400, 
                    width = 600
                ) as self._file_dialog:
                    dpg.add_file_extension(".geo")

            dpg.add_button(label = "Save", width = -1)

    def create_params_periodic(self):
        def alpha_type_cb(s, d):
            type_val = dpg.get_value(self._alpha_type)

            if type_val == "float":
                dpg.show_item(self._alpha_float)
                dpg.hide_item(self._alpha_range)

            elif type_val == "range":
                dpg.hide_item(self._alpha_float)
                dpg.show_item(self._alpha_range)

        with dpg.window(show = False, modal = True, height = 600, width = 400) as self._periodic_params:
            self._label_str = dpg.add_input_text(label = "label")

            with dpg.group(horizontal = True):
                self._alpha_type = dpg.add_combo(["float", "range"], default_value = "float", width = 100, callback = alpha_type_cb)
                self._alpha_float = dpg.add_input_float(label = "alpha")
                self._alpha_range = dpg.add_input_floatx(label = "alpha", size = 3, show = False)

            self._r0_float = dpg.add_input_float(label = "r_0")

            dpg.add_separator()
            dpg.add_button(label = "Save", width = -1, callback = self.save_params)
    
    def save_params(self):
        source_val = dpg.get_value(self._source)

        if source_val == "from file":
            self.values.update(
                filepath = dpg.get_value(self._file_input)
            )

        elif source_val == "periodic":
            self.values.update(
                label = dpg.get_value(self._label_str),
                alpha = dpg.get_value(self._alpha_range) if dpg.get_value(self._alpha_type) == "range" else dpg.get_value(self._alpha_float),
                r0 = dpg.get_value(self._r0_float),
            )
        
        self.update_stats()
        dpg.hide_item(self._periodic_params)