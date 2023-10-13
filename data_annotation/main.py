import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import yaml
import shlex
import keyboard

class App:

    def __init__(self):

        self.__include_var = None
        self.__exclude_var = None
        self.__type_var = None
        self.__camera_var = None
        self.__pub_hb_var = None
        self.__cfg_file_entry = None
        self.__rgb_cfg_file_entry = None
        self.__ip_entry = None
        self.__port_entry = None
        self.__save_location_label = None
        self.__main_dir = os.path.dirname(os.path.abspath(__file__))

        self.__root = tk.Tk()
        self.__root.title("Data Annotation")
        self.__root.configure(bg='gray20')

        self.__screen_width = self.__root.winfo_screenwidth()
        self.__screen_height = self.__root.winfo_screenheight()

        self.__window_width = self.__screen_width // 2
        self.__window_height = self.__screen_height // 2
        self.__window_position_x = (self.__screen_width - self.__window_width) // 2
        self.__window_position_y = (self.__screen_height - self.__window_height) // 2

        self.__root.geometry(f"{self.__window_width}x{self.__window_height}+{self.__window_position_x}+{self.__window_position_y}")

        self.__file_selection_frame = tk.Frame(self.__root, width=self.__window_width, height=self.__window_height//4, bg='gray20')
        self.__file_selection_frame.pack(side="top", fill="x")

        self.__sensor_selection_frame = tk.Frame(self.__file_selection_frame, bg='gray20')
        self.__sensor_selection_frame.pack(side="left", fill="both", expand=True)

        self.__video_selection_frame = tk.Frame(self.__file_selection_frame, bg='gray20')
        self.__video_selection_frame.pack(side="left", fill="both", expand=True)

        self.__ip_frame = tk.Frame(self.__root, width=self.__window_width, height=self.__window_height//8, bg='gray20')
        self.__ip_frame.pack(side="top", fill="x")

        self.__ip_container_frame = tk.Frame(self.__ip_frame, width=self.__window_width, height=self.__window_height//8, bg='gray20')
        self.__ip_container_frame.pack(side="top")

        self.__container_frame = tk.Frame(self.__root, bg='gray20')
        self.__container_frame.pack(side="top", fill="both", expand=True)

        self.__left_container_frame = tk.Frame(self.__container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__left_container_frame.pack(side="left", fill='both', expand=True)

        self.__right_container_frame = tk.Frame(self.__container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__right_container_frame.pack(side="left", fill='both', expand=True)

        self.__sensor_menu_frame = tk.Frame(self.__left_container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__sensor_menu_frame.pack(side="left", fill='both', expand=True)

        self.__video_menu_frame = tk.Frame(self.__right_container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__video_menu_frame.pack(side="right", fill='both', expand=True)

        data_recording_dir = os.path.join(self.__main_dir, "data_recording")
        cfg_file_path = os.path.join(data_recording_dir, "config.yml")
        camera_dir = os.path.join(self.__main_dir, "camera")
        rgb_cfg_path = os.path.join(camera_dir, "rgb_config.yml")

        self.render_file_selection()

        if os.path.exists(cfg_file_path):
            self.__cfg_file_entry.insert(0, cfg_file_path)
            if self.verify_cfg(cfg_file_path, type='sensor'):
                self.__cfg_valid_label = tk.Label(self.__sensor_selection_frame, text="File is valid", fg="green", bg='gray20')
                self.__cfg_valid_label.pack(pady=5)
                self.render_sensor_menu(cfg_file_path)
                self.render_ip_view()

            else:
                self.__cfg_valid_label = tk.Label(self.__sensor_selection_frame, text="File is invalid", fg="red", bg='gray20')
                self.__cfg_valid_label.pack(pady=5)

        else:
            self.__cfg_valid_label = tk.Label(self.__sensor_selection_frame, text="Please select config.yaml", fg='white', bg='gray20')
            self.__cfg_valid_label.pack(pady=5)

        if os.path.exists(rgb_cfg_path):
            self.__rgb_cfg_file_entry.insert(0, rgb_cfg_path)
            if self.verify_cfg(rgb_cfg_path, type='camera'):
                rgb_cfg_valid_label = tk.Label(self.__video_selection_frame, text="File is valid", fg="green", bg='gray20')
                rgb_cfg_valid_label.pack(pady=5)
                self.render_video_menu(rgb_cfg_path)
                self.render_ip_view()

            else:
                rgb_cfg_valid_label = tk.Label(self.__video_selection_frame, text="File is invalid", fg="red", bg='gray20')
                rgb_cfg_valid_label.pack(pady=5)

        else:
            rgb_cfg_valid_label = tk.Label(self.__video_selection_frame, text="Please select rgb_config.yaml", fg='white', bg='gray20')
            rgb_cfg_valid_label.pack(pady=5)

    def verify_cfg(self, file_path: str, type: str) -> bool:

        is_valid = False
        try:
            
            with open(file_path, 'r') as yaml_file:
                cfg_data = yaml.safe_load(yaml_file)
                if not isinstance(cfg_data, dict):
                    return False

                for key, value in cfg_data.items():
                    if key.startswith("ZONE_"):
                        for item in value:
                            if "VIDEO_DEVICE" in item and type == 'camera':
                                is_valid = True
                            if "MAC_ADDRESS" in item and type == 'sensor':
                                is_valid = True
                        return is_valid
                                
        except yaml.YAMLError as e:
            pass
        except Exception as e:
            pass
        
        return False

    def get_entry(self, type:str) -> str:

        match type:
            case 'sensor':
                return self.__cfg_file_entry.get()
            case 'camera':
                return self.__rgb_cfg_file_entry.get()

    def get_script(self, type:str) -> str:

        match type:
            case 'sensor':
                return "data_recording\\record_pixel_data.py"
            case 'camera':
                return "camera\\record_video_data.py"

    def get_choices(self, file_path: str, listbox: str) -> list[str]:
        
        try:
            with open(file_path, 'r') as yaml_file:
                cfg_data = yaml.safe_load(yaml_file)

            match listbox:
                case 'include' | 'exclude':
                    return [zone.get("MAC_ADDRESS") for key, zone in cfg_data.items() if key.startswith("ZONE_")]
                case 'type':
                    return list(cfg_data['READING'].keys())
                case 'camera':
                    return [item['DEVICE_NAME'] for item in cfg_data.values() if isinstance(item, dict) and 'DEVICE_NAME' in item] 

        except Exception as e:
            pass
        return []

    def get_video_device(self, file_path: str, device_name: str) -> int:

        try:
            with open(file_path, "r") as yaml_file:
                cfg_data = yaml.safe_load(yaml_file)
            
            video_devices = [item['VIDEO_DEVICE'] for item in cfg_data.values() if isinstance(item, dict) and 
                    'DEVICE_NAME' in item and item['DEVICE_NAME'] == device_name]
            
            if len(video_devices) > 1:
                messagebox.showerror("Error", "Camera name duplicates found")
                return

            return video_devices[0]

        except Exception as e:
            print(f"Error: {str(e)}")

    def get_uuid(self, file_path: str, device_name: str) -> str:
        try:
            with open(file_path, "r") as yaml_file:
                cfg_data = yaml.safe_load(yaml_file)
            
            uuids = [item['VIDEO_DEVICE'] for item in cfg_data.values() if isinstance(item, dict) and 
                    'DEVICE_NAME' in item and item['DEVICE_NAME'] == device_name]
            
            if len(uuids) > 1:
                messagebox.showerror("Error", "Camera name duplicates found")
                return

            return uuids[0]

        except Exception as e:
            print(f"Error: {str(e)}")

    def get_ip_port(self, file_path: str) -> tuple[str | None, str | None]:
        try:
            with open(file_path, "r") as yaml_file:
                cfg_data = yaml.safe_load(yaml_file)
            return (cfg_data['MQTT']['ADDRESS'], cfg_data['MQTT']['PORT'])
        except Exception as e:
            print(f"Error: {str(e)}")

        return None

    def start_recording(self, type: str):

        cfg_file = self.get_entry(type=type)
        script_path = os.path.join(self.__main_dir, self.get_script(type=type))
        ip_address = self.__ip_entry.get()
        port = self.__port_entry.get()
        save_location = self.__save_location_label.cget('text')
        
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "Script to execute was not found")
            return
        
        if not self.verify_cfg(cfg_file, type=type):
            messagebox.showerror("Error", "config.yml is invalid")
            return
        
        command = fr'python {script_path}'

        if ip_address:
            command = command + f" --ip {ip_address}"
        else:
            messagebox.showerror("Error", "Please insert an IP-address")
            return
        if port:
            command = command + f" --port {port}"
        else:
            messagebox.showerror("Error", "Please insert a Port")
            return
        if save_location:
            command = command + f" --save_loc {save_location}"
        else:
            messagebox.showerror("Error", "Please select a save folder")
            return
        
        try:
            if type == 'sensor':
                include_choices = ' '.join([self.__include_var.get(index) for index in self.__include_var.curselection()])
                exclude_choices = ' '.join([self.__exclude_var.get(index) for index in self.__exclude_var.curselection()])
                type_choices = ' '.join([self.__type_var.get(index) for index in self.__type_var.curselection()]).lower()
                command = command + f"--cfg {cfg_file}"

                if include_choices:
                    command = command + f" --include {include_choices}"
                if exclude_choices:
                    command = command + f" --exclude {exclude_choices}"
                if type_choices:
                    command = command + f" --type {type_choices}"
                
                command = command.replace("\\", "/")
                command_list = shlex.split(command)
                subprocess.Popen(command_list)
                
            if type == 'camera':

                camera_choices = [self.__camera_var.get(index) for index in self.__camera_var.curselection()]
                pub_hb = str(self.__pub_hb_var.get())
                ip_address = self.__ip_entry.get()
                port = self.__port_entry.get()
                save_location = self.__save_location_label.cget('text')
                command = command + fr" --pub_hb {pub_hb}"

                for camera in camera_choices:

                    video_capture_index = self.get_video_device(file_path=cfg_file, device_name=camera)
                    uuid = self.get_uuid(file_path=cfg_file, device_name=camera)
                    if video_capture_index:
                        command = command + f" --vid_cap {video_capture_index} --device {camera} --uuid {uuid}"
                    command = command.replace("\\", "/")
                    command_list = shlex.split(command)
                    subprocess.Popen(command_list)

        except Exception as e:
            messagebox.showerror("Error", f"Error executing script: {str(e)}")

    def stop_recording(self, type: str):
        types = {
            'sensor': keyboard.press_and_release('s'),
            'camera': keyboard.press_and_release('q')
        }
        types.get(type, lambda: 'invalid')

    def browse_cfg_file(self):

        file_path = filedialog.askopenfilename(filetypes=[("cfg Files", "*.yml")])
        
        if file_path:
            self.__cfg_file_entry.delete(0, tk.END)
            self.__cfg_file_entry.insert(0, file_path)
            if self.verify_cfg(file_path, type='sensor'):
                self.__cfg_valid_label.config(text="File is valid", fg="green")
                self.render_sensor_menu(file_path)
                self.render_ip_view()
            else:
                self.__sensor_menu_frame.destroy()
                self.__cfg_valid_label.config(text="File is invalid", fg="red")
                self.render_ip_view()

    def browse_rgb_cfg_file(self):
        
        file_path = filedialog.askopenfilename(filetypes=[("cfg Files", "*.yml")])
        
        if file_path:
            self.__rgb_cfg_file_entry.delete(0, tk.END)
            self.__rgb_cfg_file_entry.insert(0, file_path)

            if self.verify_cfg(file_path, type='camera'):
                self.rgb_cfg_valid_label.config(text="File is valid", fg="green")
                self.render_video_menu(file_path)
                self.render_ip_view()
            else:
                self.rgb_cfg_valid_label.config(text="File is invalid", fg="red")
                self.__video_menu_frame.destroy()
                self.render_ip_view()

    def browse_save_location(self):

        folder_path = filedialog.askdirectory()
        if folder_path:
            self.__save_location_label.config(text=folder_path)

    def render_sensor_menu(self, cfg_file_path):

        self.__sensor_menu_frame.destroy()

        self.__sensor_menu_frame = tk.Frame(self.__left_container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__sensor_menu_frame.pack(side="left", fill='both', expand=True)

        subframe0 = tk.Frame(self.__sensor_menu_frame, bg="gray20")
        subframe0.pack(side="left", fill="both", expand=True)

        subframe1 = tk.Frame(self.__sensor_menu_frame, bg="gray20")
        subframe1.pack(side="left", fill="both", expand=True)

        subframe2 = tk.Frame(self.__sensor_menu_frame, bg="gray20")
        subframe2.pack(side="left", fill="both", expand=True)

        include_choices = self.get_choices(cfg_file_path, listbox='include')
        exclude_choices = self.get_choices(cfg_file_path, listbox='exclude')
        type_choices = self.get_choices(cfg_file_path, listbox='type')

        max_choices = max((len(include_choices), len(type_choices)))

        include_label = tk.Label(subframe0, text="Include:", fg='white', bg='gray20')
        include_label.pack(pady=10)
        self.__include_var = tk.Listbox(subframe0, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
        for choice in include_choices:
            self.__include_var.insert(tk.END, choice)
        self.__include_var.pack()

        exclude_label = tk.Label(subframe1, text="Exclude:", fg='white', bg='gray20')
        exclude_label.pack(pady=10)
        self.__exclude_var = tk.Listbox(subframe1, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40',  borderwidth=5)
        for choice in exclude_choices:
            self.__exclude_var.insert(tk.END, choice)
        self.__exclude_var.pack()

        type_label = tk.Label(subframe2, text="Types:", fg='white', bg='gray20')
        type_label.pack(pady=10)
        self.__type_var = tk.Listbox(subframe2, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
        for choice in type_choices:
            self.__type_var.insert(tk.END, choice)
        self.__type_var.pack()

        run_sensor_button = tk.Button(subframe1, text="record sensor data", command=lambda: self.start_recording(type='sensor'), fg='white', bg='gray20')
        run_sensor_button.pack(pady=20)

        run_sensor_button = tk.Button(subframe1, text="stop sensor recording", command=lambda: self.stop_recording('sensor'), fg='white', bg='gray20')
        run_sensor_button.pack(pady=20)
        
    def render_video_menu(self, video_cfg_path):

        self.__video_menu_frame.destroy()

        self.__video_menu_frame = tk.Frame(self.__right_container_frame, width=self.__window_width//2, height=self.__window_height//2, bg='gray20')
        self.__video_menu_frame.pack(side="right", fill='both', expand=True)

        subframe0 = tk.Frame(self.__video_menu_frame, bg="gray20")
        subframe0.pack(side="left", fill="both", expand=True)

        subframe1 = tk.Frame(self.__video_menu_frame, bg="gray20")
        subframe1.pack(side="left", fill="both", expand=True, padx=14)

        subframe2 = tk.Frame(self.__video_menu_frame, bg="gray20")
        subframe2.pack(side="left", fill="both", expand=True, padx=63)

        camera_choices = self.get_choices(video_cfg_path, listbox='camera')
        camera_label = tk.Label(subframe0, text="Cameras:", fg='white', bg='gray20')
        camera_label.pack(pady=10)
        self.__camera_var = tk.Listbox(subframe0, selectmode=tk.MULTIPLE, height=len(camera_choices), exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
        for choice in camera_choices:
            self.__camera_var.insert(tk.END, choice)
        self.__camera_var.pack()

        pub_hb_label = tk.Label(subframe1, text="Publish heartbeat?", fg='white', bg='gray20')
        pub_hb_label.pack(pady=10)
        self.__pub_hb_var = tk.BooleanVar()
        self.__pub_hb_var.set(True)
        pub_hb_checkbutton = tk.Checkbutton(subframe1, text="Yes", variable=self.__pub_hb_var, selectcolor='gray20', fg='white', bg='gray20', activebackground="gray20", activeforeground="white")
        pub_hb_checkbutton.pack()

        run_sensor_button = tk.Button(subframe1, text="record video data", command=lambda: self.start_recording(type='camera'), fg='white', bg='gray20')
        run_sensor_button.pack(pady=15)

        run_sensor_button = tk.Button(subframe1, text="stop video recording", command=lambda: self.stop_recording('camera'), fg='white', bg='gray20')
        run_sensor_button.pack(pady=15)

    def render_file_selection(self):

        cfg_file_label = tk.Label(self.__sensor_selection_frame, text="Path to config.yml:", fg='white', bg='gray20')
        cfg_file_label.pack(pady=5)

        rgb_cfg_file_label = tk.Label(self.__video_selection_frame, text="Path to rgb_config.yml:", fg='white', bg='gray20')
        rgb_cfg_file_label.pack(pady=5)

        self.__cfg_file_entry = tk.Entry(self.__sensor_selection_frame, width=60, fg='white', bg='gray20')
        self.__cfg_file_entry.pack()

        self.__rgb_cfg_file_entry = tk.Entry(self.__video_selection_frame, width=60, fg='white', bg='gray20')
        self.__rgb_cfg_file_entry.pack()

        browse_button = tk.Button(self.__sensor_selection_frame, text="Browse", command=self.browse_cfg_file, fg='white', bg='gray20')
        browse_button.pack(pady=5)

        rgb_browse_button = tk.Button(self.__video_selection_frame, text="Browse", command=self.browse_rgb_cfg_file, fg='white', bg='gray20')
        rgb_browse_button.pack(pady=5)

    def render_ip_view(self):
        self.__ip_container_frame.destroy()

        self.__ip_container_frame = tk.Frame(self.__ip_frame, width=self.__window_width, height=self.__window_height//8, bg='gray20')
        self.__ip_container_frame.pack(side="top")

        if self.verify_cfg(self.__cfg_file_entry.get(), type='sensor') or self.verify_cfg(self.__rgb_cfg_file_entry.get(), type='camera'):

            ip_label = tk.Label(self.__ip_container_frame, text='ip-address:', fg='white', bg='gray20')
            ip_label.pack(side='left', padx=5)

            self.__ip_entry = tk.Entry(self.__ip_container_frame, fg='white', bg='gray20')
            self.__ip_entry.pack(side='left')

            pad = tk.Label(self.__ip_container_frame, bg='gray20')
            pad.pack(side='left', padx=10, pady=30)

            port_label = tk.Label(self.__ip_container_frame, text='port:', fg='white', bg='gray20')
            port_label.pack(side='left', padx=5)

            self.__port_entry = tk.Entry(self.__ip_container_frame, fg='white', bg='gray20')
            self.__port_entry.pack(side='left')

            pad2 = tk.Label(self.__ip_container_frame, bg='gray20')
            pad2.pack(side='left', padx=10)

            if self.verify_cfg(self.__cfg_file_entry.get(), type='sensor'):

                ip_address, port = self.get_ip_port(self.__cfg_file_entry.get())
                self.__ip_entry.insert(0, ip_address)
                self.__port_entry.insert(0, port)

            self.__save_location_label = tk.Label(self.__ip_container_frame, text="", fg='white', bg='gray20')

            select_button = tk.Button(self.__ip_container_frame, text="Select Save Location", command=self.browse_save_location, fg='white', bg='gray20')
            select_button.pack(side='left')

            self.__save_location_label.pack(side='left', padx=5)

    def run(self):
        self.__root.mainloop()

if __name__ == '__main__':
    app = App()
    app.run()