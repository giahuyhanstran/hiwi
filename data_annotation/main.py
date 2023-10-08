import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import yaml
import shlex

def validate_config_file(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            config_data = yaml.safe_load(yaml_file)
            if all(key in config_data for key in ["SUBTOPIC", "READING"]) and any(key.startswith("ZONE_") for key in config_data.keys()):
                for key, zone in config_data.items():
                    if key.startswith("ZONE_") and "MAC_ADDRESS" in zone:
                        return True
    except Exception as e:
        pass
    return False

def get_type_choices(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            config_data = yaml.safe_load(yaml_file)
            return list(config_data['READING'].keys())
    except Exception as e:
        pass
    return []

def get_include_exclude_choices(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            config_data = yaml.safe_load(yaml_file)
            mac_addresses = [zone.get("MAC_ADDRESS") for key, zone in config_data.items() if key.startswith("ZONE_")]
            return mac_addresses
    except Exception as e:
        pass
    return []

def run_script():
    # Get the path to the config.yml file
    config_file = config_file_entry.get()

    # Get the directory where the main.py script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Set the path to record_pixel_data.py and record_video_data.py
    script_path = os.path.join(script_directory, "data_recording\\record_pixel_data.py")
    script_path_video = os.path.join(script_directory, "camera\\record_video_data.py")
    
    if not os.path.exists(script_path):
        messagebox.showerror("Error", "record_pixel_data.py not found in the same directory.")
        return
    
    if validate_config_file(config_file):
        config_valid_label.config(text="File is valid", fg="green")
    else:
        config_valid_label.config(text="File is invalid", fg="red")
        return
    
    # Run Python script as a subprocess
    try:
        include_choices = ' '.join([include_var.get(index) for index in include_var.curselection()])
        exclude_choices = ' '.join([exclude_var.get(index) for index in exclude_var.curselection()])
        type_choices = ' '.join([type_var.get(index) for index in type_var.curselection()]).lower()
        command = fr"python {script_path} --cfg {config_file}"
        

        if include_choices:
            command = command + f" --include {include_choices}"
        if exclude_choices:
            command = command + f" --exclude {exclude_choices}"
        if type_choices:
            command = command + f" --type {type_choices}"

        pub_hb = str(pub_hb_var.get())
        pub_data = str(pub_data_var.get())
        
        # pub_data = 
        command2 = fr"python {script_path_video} --pub_hb {pub_hb} --pub_data {pub_data}"

        command = command.replace("\\", "/")
        command2 = command2.replace("\\", "/")
        command_list = shlex.split(command)
        command_list2 = shlex.split(command2)

        subprocess.Popen(command_list)
        subprocess.Popen(command_list2)

    except Exception as e:
        messagebox.showerror("Error", f"Error executing script: {str(e)}")

def browse_config_file():
    # Open a file dialog to select the config.yml file
    file_path = filedialog.askopenfilename(filetypes=[("Config Files", "*.yml")])
    
    if file_path:
        config_file_entry.delete(0, tk.END)  # Clear any existing text
        config_file_entry.insert(0, file_path)
        if validate_config_file(file_path):
            config_valid_label.config(text="File is valid", fg="green")
            render_menu(file_path)
        else:
            config_valid_label.config(text="File is invalid", fg="red")
            render_file_selection()

def render_menu(config_file_path):
        
    global include_var
    global exclude_var
    global type_var
    global center
    global menu_frame
    global pub_hb_var
    global pub_data_var

    menu_frame = tk.Frame(root)
    menu_frame.configure(bg='gray20')
    menu_frame.pack()

    separator_frame = tk.Frame(menu_frame, height=2, bg="white")
    separator_frame.grid(row=center+7, column=0, columnspan=10, sticky="ew", pady=30)

    # Create the include dropdown menu based on config.yml
    include_choices = get_include_exclude_choices(config_file_path)
    exclude_choices = include_choices
    type_choices = get_type_choices(config_file_path)

    max_choices = max((len(include_choices), len(type_choices)))

    include_label = tk.Label(menu_frame, text="Include:", fg='white', bg='gray20')
    include_label.grid(row=center+4, column=center-1)
    include_var = tk.Listbox(menu_frame, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
    for choice in include_choices:
        include_var.insert(tk.END, choice)
    include_var.grid(row=center+5, column=center-1, padx=20)

    exclude_label = tk.Label(menu_frame, text="Exclude:", fg='white', bg='gray20')
    exclude_label.grid(row=center+4, column=center)
    exclude_var = tk.Listbox(menu_frame, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40',  borderwidth=5)
    for choice in exclude_choices:
        exclude_var.insert(tk.END, choice)
    exclude_var.grid(row=center+5, column=center, padx=20)

    type_label = tk.Label(menu_frame, text="Types:", fg='white', bg='gray20')
    type_label.grid(row=center+4, column=center+1)
    type_var = tk.Listbox(menu_frame, selectmode=tk.MULTIPLE, height=max_choices, exportselection=0, fg='white', bg='gray20', highlightbackground='gray40', borderwidth=5)
    for choice in type_choices:
        type_var.insert(tk.END, choice)
    type_var.grid(row=center+5, column=center+1, padx=20)

    # Create options for video recording
    pub_hb_label = tk.Label(menu_frame, text="Publish heartbeat?", fg='white', bg='gray20')
    pub_hb_label.grid(row=center+8, column=center+1)
    pub_hb_var = tk.BooleanVar()
    pub_hb_var.set(True)
    pub_hb_checkbutton = tk.Checkbutton(menu_frame, text="Yes", variable=pub_hb_var, selectcolor='gray20', fg='white', bg='gray20', activebackground="gray20", activeforeground="white")
    pub_hb_checkbutton.grid(row=center+9, column=center+1)


    pub_data_label = tk.Label(menu_frame, text="Publish video data?", fg='white', bg='gray20')
    pub_data_label.grid(row=center+8, column=center-1)
    pub_data_var = tk.BooleanVar()
    pub_data_checkbutton = tk.Checkbutton(menu_frame, text="Yes", variable=pub_data_var, selectcolor='gray20', fg='white', bg='gray20', activebackground="gray20", activeforeground="white")
    pub_data_checkbutton.grid(row=center+9, column=center-1)

    # Button to run scripts
    run_button = tk.Button(menu_frame, text="Start annotation", command=run_script, fg='white', bg='gray20')
    run_button.grid(row=center+10, column=center)

def render_file_selection():

    global config_file_entry
    global center
    global menu_frame

    menu_frame.destroy()

    padding_next_to_valid_label = tk.Label(file_selection_frame, text="", bg='gray20')
    padding_next_to_valid_label.grid(row=center-1, column=center-1, padx=27)

    padding_below_valid_label = tk.Label(file_selection_frame, text="", bg='gray20')
    padding_below_valid_label.grid(row=center+2, column=center, pady=10)

    padding_above_file_label = tk.Label(file_selection_frame, text="", bg='gray20')
    padding_above_file_label.grid(row=center-2, column=center, pady=20)

    config_file_label = tk.Label(file_selection_frame, text="Config File Path:", fg='white', bg='gray20')
    config_file_label.grid(row=center-1, column=center)

    config_file_entry = tk.Entry(file_selection_frame, width=60, fg='white', bg='gray20')
    config_file_entry.grid(row=center, column=center)

    browse_button = tk.Button(file_selection_frame, text="Browse", command=browse_config_file, fg='white', bg='gray20')
    browse_button.grid(row=center, column=center+1, padx=5)

if __name__ == '__main__':

    center = 5
    include_var = None
    exclude_var = None
    type_var = None
    pub_hb_var = None
    pub_data_var = None
    config_file_entry = None

    # Create the main window
    root = tk.Tk()
    root.title("Data Annotation")
    root.configure(bg='gray20')

    # Determine the screen width and height for dynamic sizing
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size to approximately half of the screen size
    window_width = screen_width // 2
    window_height = screen_height // 2
    window_position_x = (screen_width - window_width) // 2
    window_position_y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

    # Create frames to organize widgets
    menu_frame = tk.Frame(root)
    menu_frame.configure(bg='gray20')
    menu_frame.pack()
    file_selection_frame = tk.Frame(root)
    file_selection_frame.configure(bg='gray20')
    file_selection_frame.pack()

    render_file_selection()

    # Get the directory where the config.yaml script is located
    main_dir = os.path.dirname(os.path.abspath(__file__))
    data_recording_dir = os.path.join(main_dir, "data_recording")
    
    # Check if a config.yml file exists in the same directory
    config_file_path = os.path.join(data_recording_dir, "config.yml")
        
    if os.path.exists(config_file_path):
        config_file_entry.insert(0, config_file_path)
        if validate_config_file(config_file_path):
            config_valid_label = tk.Label(file_selection_frame, text="File is valid", fg="green", bg='gray20')
            config_valid_label.grid(row=center+1, column=center)
            render_menu(config_file_path)

        else:
            config_valid_label = tk.Label(file_selection_frame, text="File is invalid", fg="red", bg='gray20')
            config_valid_label.grid(row=center+1, column=center)

    else:
        config_valid_label = tk.Label(file_selection_frame, text="Please select config.yml", fg='white', bg='gray20')
        config_valid_label.grid(row=center+1, column=center)

    root.mainloop()
