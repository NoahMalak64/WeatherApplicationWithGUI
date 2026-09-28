import tkinter as tk

def _create_widget(parent, widget_type, **options):
        return widget_type(parent, **options)

class WindowSwitcher:
    def __init__():
        pass
    
    @staticmethod
    def clear_window(tk_window: tk.Tk) -> None: # declares type of tk and returns None. 
        """
        Destroys all objects in the window

        Args: window (tk.Tk)
        """
        for widget in tk_window.winfo_children():
            widget.destroy()
        
    @staticmethod
    def show_dashboard(tk_window: tk.Tk):
        tk_window.geometry("800x500")
        # create general grid for the dashboard
        tk_window.grid_columnconfigure(0, weight = 1)
        tk_window.grid_columnconfigure(1, weight= 3)
        tk_window.grid_rowconfigure(0, weight= 2)
        tk_window.grid_rowconfigure(1, weight= 1)

        # create frames to populate with content later
        nav_frame = _create_widget(tk_window, tk.Frame, bg='darkgray')
        trend_frame = _create_widget(tk_window, tk.Frame, bg= 'indianred1')
        description_frame = _create_widget(tk_window, tk.Frame, bg='grey')

        # assign frames to grid
        nav_frame.grid(row=0, column=0, rowspan=2, sticky= 'nsew')
        trend_frame.grid(row=0, column=1, sticky= 'nsew')
        description_frame.grid(row=1, column=1, sticky= 'nsew')

    @staticmethod
    def switch_to_dashboard(tk_window: tk.Tk):
        WindowSwitcher.clear_window(tk_window)
        WindowSwitcher.show_dashboard(tk_window)
