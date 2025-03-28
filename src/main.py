from gui import GUI

def start_app():
    App = GUI()
    App.draw_gui()
    App.mainloop()

if __name__ == '__main__':
    # program entry point
    start_app()
