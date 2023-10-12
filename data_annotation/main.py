import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import yaml
import shlex
import keyboard


def verify_cfg(file_path: str, type: str) -> bool:

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

def get_entry(type:str) -> str:

    match type:
        case 'sensor':
            return cfg_file_entry.get()
        case 'camera':
            return rgb_cfg_file_entry.get()

def get_script(type:str) -> str:

    match type:
        case 'sensor':
            return "data_recording\\record_pixel_data.py"
        case 'camera':
            return "camera\\record_video_data.py"

def get_choices(file_path: str, listbox: str) -> list[str]:
    
    try:
        with open(file_path, 'r') as yaml_file:
            cfg_data = yaml.safe_load(yaml_file)

        match listbox:
            case 'include' | 'exclude':
                return [zone.get("MAC_ADDRESS") for key, zone in cfg_data.items() if key.startswith("ZONE_")]
            case 'type':
                return list(cfg_data['READING'].keys())
            case 'camera':
                [item['DEVICE_NAME'] for item in cfg_data.values() if isinstance(item, dict) and 'DEVICE_NAME' in item] 

    except Exception as e:
        pass
    return []

def get_video_device_by_device_name(file_path: str, device_name: str) -> list[int]:

    try:
        with open(file_path, "r") as yaml_file:
            cfg_data = yaml.safe_load(yaml_file)
        
        return [item['VIDEO_DEVICE'] for item in cfg_data.values() if isinstance(item, dict) and 
                'DEVICE_NAME' in item and item['DEVICE_NAME'] == device_name]
    
    except Exception as e:
        print(f"Error: {str(e)}")

def get_ip_port(file_path: str) -> tuple[str | None, str | None]:
    try:
        with open(file_path, "r") as yaml_file:
            cfg_data = yaml.safe_load(yaml_file)
        return (cfg_data['MQTT']['ADDRESS'], cfg_data['MQTT']['PORT'])
    except Exception as e:
        print(f"Error: {str(e)}")

    return None

def start_recording(type: str):

    global main_dir
    cfg_file = get_entry(type=type)
    script_path = os.path.join(main_dir, get_script(type=type))
    
    if not os.path.exists(script_path):
        messagebox.showerror("Error", "Script to execute was not found")
        return
    
    if not verify_cfg(cfg_file, type=type):
        messagebox.showerror("Error", "config.yml is invalid")
        return
    
    try:
        if type == 'sensor':
            include_choices = ' '.join([include_var.get(index) for index in include_var.curselection()])
            exclude_choices = ' '.join([exclude_var.get(index) for index in exclude_var.curselection()])
            type_choices = ' '.join([type_var.get(index) for index in type_var.curselection()]).lower()
            ip_address = ip_entry.get()
            port = port_entry.get()
            save_location = save_location_label.cget('text')

            command = fr"python {script_path} --cfg {cfg_file}"
            
            if include_choices:
                command = command + f" --include {include_choices}"
            if exclude_choices:
                command = command + f" --exclude {exclude_choices}"
            if type_choices:
                command = command + f" --type {type_choices}"
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
            
            command = command.replace("\\", "/")
            command_list = shlex.split(command)
            subprocess.Popen(command_list)
            
        if type == 'camera':

            camera_choices = [camera_var.get(index) for index in camera_var.curselection()]
            pub_hb = str(pub_hb_var.get())
            pub_data = str(pub_data_var.get())
            ip_address = ip_entry.get()
            port = port_entry.get()
            save_location = save_location_label.cget('text')
            
            for camera in camera_choices:

                video_capture_index = get_video_device_by_device_name(file_path=cfg_file, device_name=camera)
                command = fr"python {script_path} --pub_hb {pub_hb} --pub_data {pub_data} --vid_cap {video_capture_index} --ip {ip_address} --port {port} --save_loc {save_location}"

                command = command.replace("\\", "/")
                command_list = shlex.split(command)
                subprocess.Popen(command_list)

    except Exception as e:
        messagebox.showerror("Error", f"Error executing script: {str(e)}")

def stop_recording(type: str):
    types = {
        'sensor': keyboard.press_and_release('s'),
        'camera': keyboard.press_and_release('q')
    }
    types.get(type, lambda: 'invalid')

def browse_cfg_file():

    file_path = filedialog.askopenfilename(filetypes=[("cfg Files", "*.yml")])
    
    if file_path:
        cfg_file_entry.delete(0, tk.END)
        cfg_file_entry.insert(0, file_path)
        if verify_cfg(file_path, type='sensor'):
            cfg_valid_label.config(text="File is valid", fg="green")
            render_sensor_menu(file_path)
            render_ip_view()
        else:
            sensor_menu_frame.destroy()
            cfg_valid_label.config(text="File is invalid", fg="red")
            render_ip_view()

def browse_rgb_cfg_file():
    
    file_path = filedialog.askopenfilename(filetypes=[("cfg Files", "*.yml")])
    
    if file_path:
        rgb_cfg_file_entry.delete(0, tk.END)
        rgb_cfg_file_entry.insert(0, file_path)

        if verify_cfg(file_path, type='camera'):
            rgb_cfg_valid_label.config(text="File is valid", fg="green")
            render_video_menu(file_path)
            render_ip_view()
        else:
            rgb_cfg_valid_label.config(text="File is invalid", fg="red")
            video_menu_frame.destroy()
            render_ip_view()

def browse_save_location(save_location_label):

    folder_path = filedialog.askdirectory()
    if folder_path:
        save_location_label.config(text=folder_path)

def render_sensor_menu(cfg_file_path):
        
    global include_var
    global exclude_var
    global type_var
    global sensor_menu_frame

    sensor_menu_frame.destroy()

    sensor_menu_frame = tk.Frame(left_container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    sensor_menu_frame.pack(side="left", fill='both', expand=True)

    subframe0 = tk.Frame(sensor_menu_frame, bg="gray20")
    subframe0.pack(side="left", fill="both", expand=True)

    subframe1 = tk.Frame(sensor_menu_frame, bg="gray20")
    subframe1.pack(side="left", fill="both", expand=True)

    subframe2 = tk.Frame(sensor_menu_frame, bg="gray20")
    subframe2.pack(side="left", fill="both", expand=True)

    include_choices = get_choices(cfg_file_path, listbox='include')
    exclude_choices = get_choices(cfg_file_path, listbox='exclude')
    type_choices = get_choices(cfg_file_path, listbox='type')

    max_choices = max((len(include_choices), len(type_choices)))

    include_label = tk.Label(subframe0, text="Include:", fg='white', bg='gray20')
    include_label.pack(pady=10)
    include_var = tk.Listbox(subframe0, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
    for choice in include_choices:
        include_var.insert(tk.END, choice)
    include_var.pack()

    exclude_label = tk.Label(subframe1, text="Exclude:", fg='white', bg='gray20')
    exclude_label.pack(pady=10)
    exclude_var = tk.Listbox(subframe1, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40',  borderwidth=5)
    for choice in exclude_choices:
        exclude_var.insert(tk.END, choice)
    exclude_var.pack()

    type_label = tk.Label(subframe2, text="Types:", fg='white', bg='gray20')
    type_label.pack(pady=10)
    type_var = tk.Listbox(subframe2, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
    for choice in type_choices:
        type_var.insert(tk.END, choice)
    type_var.pack()

    run_sensor_button = tk.Button(subframe1, text="record sensor data", command=lambda: start_recording(type='sensor'), fg='white', bg='gray20')
    run_sensor_button.pack(pady=20)

    run_sensor_button = tk.Button(subframe1, text="stop sensor recording", command=lambda: stop_recording('sensor'), fg='white', bg='gray20')
    run_sensor_button.pack(pady=20)
    
def render_video_menu(video_cfg_path):
    
    global video_menu_frame
    global pub_hb_var
    global pub_data_var
    global camera_var

    video_menu_frame.destroy()

    video_menu_frame = tk.Frame(right_container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    video_menu_frame.pack(side="right", fill='both', expand=True)

    subframe0 = tk.Frame(video_menu_frame, bg="gray20")
    subframe0.pack(side="left", fill="both", expand=True)

    subframe1 = tk.Frame(video_menu_frame, bg="gray20")
    subframe1.pack(side="left", fill="both", expand=True, padx=14)

    subframe2 = tk.Frame(video_menu_frame, bg="gray20")
    subframe2.pack(side="left", fill="both", expand=True, padx=63)

    camera_choices = get_choices(video_cfg_path, listbox='camera')
    camera_label = tk.Label(subframe0, text="Cameras:", fg='white', bg='gray20')
    camera_label.pack(pady=10)
    camera_var = tk.Listbox(subframe0, selectmode=tk.MULTIPLE, height=len(camera_choices), exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
    for choice in camera_choices:
        camera_var.insert(tk.END, choice)
    camera_var.pack()

    pub_hb_label = tk.Label(subframe1, text="Publish heartbeat?", fg='white', bg='gray20')
    pub_hb_label.pack(pady=10)
    pub_hb_var = tk.BooleanVar()
    pub_hb_var.set(True)
    pub_hb_checkbutton = tk.Checkbutton(subframe1, text="Yes", variable=pub_hb_var, selectcolor='gray20', fg='white', bg='gray20', activebackground="gray20", activeforeground="white")
    pub_hb_checkbutton.pack()

    pub_data_label = tk.Label(subframe1, text="Publish video data?", fg='white', bg='gray20')
    pub_data_label.pack(pady=10)
    pub_data_var = tk.BooleanVar()
    pub_data_checkbutton = tk.Checkbutton(subframe1, text="Yes", variable=pub_data_var, selectcolor='gray20', fg='white', bg='gray20', activebackground="gray20", activeforeground="white")
    pub_data_checkbutton.pack()

    run_sensor_button = tk.Button(subframe1, text="record video data", command=lambda: start_recording(type='camera'), fg='white', bg='gray20')
    run_sensor_button.pack(pady=15)

    run_sensor_button = tk.Button(subframe1, text="stop video recording", command=lambda: stop_recording('camera'), fg='white', bg='gray20')
    run_sensor_button.pack(pady=15)

def render_file_selection():

    global cfg_file_entry
    global rgb_cfg_file_entry
    global file_selection_frame
    global sensor_selection_frame
    global video_selection_frame

    cfg_file_label = tk.Label(sensor_selection_frame, text="Path to config.yml:", fg='white', bg='gray20')
    cfg_file_label.pack(pady=5)

    rgb_cfg_file_label = tk.Label(video_selection_frame, text="Path to rgb_config.yml:", fg='white', bg='gray20')
    rgb_cfg_file_label.pack(pady=5)

    cfg_file_entry = tk.Entry(sensor_selection_frame, width=60, fg='white', bg='gray20')
    cfg_file_entry.pack()

    rgb_cfg_file_entry = tk.Entry(video_selection_frame, width=60, fg='white', bg='gray20')
    rgb_cfg_file_entry.pack()

    browse_button = tk.Button(sensor_selection_frame, text="Browse", command=browse_cfg_file, fg='white', bg='gray20')
    browse_button.pack(pady=5)

    rgb_browse_button = tk.Button(video_selection_frame, text="Browse", command=browse_rgb_cfg_file, fg='white', bg='gray20')
    rgb_browse_button.pack(pady=5)

def render_ip_view():

    global ip_container_frame
    global ip_frame
    global ip_entry
    global port_entry
    global save_location_label

    ip_container_frame.destroy()

    ip_container_frame = tk.Frame(ip_frame, width=window_width, height=window_height//8, bg='gray20')
    ip_container_frame.pack(side="top")

    if verify_cfg(cfg_file_entry.get(), type='sensor') or verify_cfg(rgb_cfg_file_entry.get(), type='camera'):

        ip_label = tk.Label(ip_container_frame, text='ip-address:', fg='white', bg='gray20')
        ip_label.pack(side='left', padx=5)

        ip_entry = tk.Entry(ip_container_frame, fg='white', bg='gray20')
        ip_entry.pack(side='left')

        pad = tk.Label(ip_container_frame, bg='gray20')
        pad.pack(side='left', padx=10, pady=30)

        port_label = tk.Label(ip_container_frame, text='port:', fg='white', bg='gray20')
        port_label.pack(side='left', padx=5)

        port_entry = tk.Entry(ip_container_frame, fg='white', bg='gray20')
        port_entry.pack(side='left')

        pad2 = tk.Label(ip_container_frame, bg='gray20')
        pad2.pack(side='left', padx=10)

        if verify_cfg(cfg_file_entry.get(), type='sensor'):

            ip_address, port = get_ip_port(cfg_file_entry.get())
            ip_entry.insert(0, ip_address)
            port_entry.insert(0, port)

        save_location_label = tk.Label(ip_container_frame, text="", fg='white', bg='gray20')

        select_button = tk.Button(ip_container_frame, text="Select Save Location", command=lambda: browse_save_location(save_location_label), fg='white', bg='gray20')
        select_button.pack(side='left')

        save_location_label.pack(side='left', padx=5)

if __name__ == '__main__':

    include_var = None
    exclude_var = None
    type_var = None
    camera_var = None
    pub_hb_var = None
    pub_data_var = None
    cfg_file_entry = None
    rgb_cfg_file_entry = None
    ip_entry = None
    port_entry = None
    save_location_label = None

    main_dir = script_directory = os.path.dirname(os.path.abspath(__file__))

    root = tk.Tk()
    root.title("Data Annotation")
    root.configure(bg='gray20')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = screen_width // 2
    window_height = screen_height // 2
    window_position_x = (screen_width - window_width) // 2
    window_position_y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

    file_selection_frame = tk.Frame(root, width=window_width, height=window_height//4, bg='gray20')
    file_selection_frame.pack(side="top", fill="x")

    sensor_selection_frame = tk.Frame(file_selection_frame, bg='gray20')
    sensor_selection_frame.pack(side="left", fill="both", expand=True)

    video_selection_frame = tk.Frame(file_selection_frame, bg='gray20')
    video_selection_frame.pack(side="left", fill="both", expand=True)

    ip_frame = tk.Frame(root, width=window_width, height=window_height//8, bg='gray20')
    ip_frame.pack(side="top", fill="x")

    ip_container_frame = tk.Frame(ip_frame, width=window_width, height=window_height//8, bg='gray20')
    ip_container_frame.pack(side="top")

    container_frame = tk.Frame(root, bg='gray20')
    container_frame.pack(side="top", fill="both", expand=True)

    left_container_frame = tk.Frame(container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    left_container_frame.pack(side="left", fill='both', expand=True)

    right_container_frame = tk.Frame(container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    right_container_frame.pack(side="left", fill='both', expand=True)

    sensor_menu_frame = tk.Frame(left_container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    sensor_menu_frame.pack(side="left", fill='both', expand=True)

    video_menu_frame = tk.Frame(right_container_frame, width=window_width//2, height=window_height//2, bg='gray20')
    video_menu_frame.pack(side="right", fill='both', expand=True)

    render_file_selection()

    main_dir = os.path.dirname(os.path.abspath(__file__))
    data_recording_dir = os.path.join(main_dir, "data_recording")
    cfg_file_path = os.path.join(data_recording_dir, "config.yml")
    camera_dir = os.path.join(main_dir, "camera")
    rgb_cfg_path = os.path.join(camera_dir, "rgb_config.yml")
        
    if os.path.exists(cfg_file_path):
        cfg_file_entry.insert(0, cfg_file_path)
        if verify_cfg(cfg_file_path, type='sensor'):
            cfg_valid_label = tk.Label(sensor_selection_frame, text="File is valid", fg="green", bg='gray20')
            cfg_valid_label.pack(pady=5)
            render_sensor_menu(cfg_file_path)
            render_ip_view()

        else:
            cfg_valid_label = tk.Label(sensor_selection_frame, text="File is invalid", fg="red", bg='gray20')
            cfg_valid_label.pack(pady=5)

    else:
        cfg_valid_label = tk.Label(sensor_selection_frame, text="Please select config.yaml", fg='white', bg='gray20')
        cfg_valid_label.pack(pady=5)

    if os.path.exists(rgb_cfg_path):
        rgb_cfg_file_entry.insert(0, rgb_cfg_path)
        if verify_cfg(rgb_cfg_path, type='camera'):
            rgb_cfg_valid_label = tk.Label(video_selection_frame, text="File is valid", fg="green", bg='gray20')
            rgb_cfg_valid_label.pack(pady=5)
            render_video_menu(rgb_cfg_path)
            render_ip_view()

        else:
            rgb_cfg_valid_label = tk.Label(video_selection_frame, text="File is invalid", fg="red", bg='gray20')
            rgb_cfg_valid_label.pack(pady=5)

    else:
        rgb_cfg_valid_label = tk.Label(video_selection_frame, text="Please select rgb_config.yaml", fg='white', bg='gray20')
        rgb_cfg_valid_label.pack(pady=5)

    root.mainloop()
