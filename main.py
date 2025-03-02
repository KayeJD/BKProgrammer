import gui
import controller
import queue

if __name__ == "__main__":
    data_queue = queue.Queue()
    gui.log_queue = data_queue
    controller.main()
    gui.main()