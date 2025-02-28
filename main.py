import gui
import controllerTest
import queue

if __name__ == "__main__":
    command_queue = queue.Queue()
    data_queue = queue.Queue()
    gui.log_queue = data_queue
    controllerTest.main(command_queue)
    gui.main()