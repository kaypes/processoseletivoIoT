import uasyncio

from hal import FeedbackController
from display_driver import DisplayDriver
from fsm import FSM
from async_queue import Queue
from input_handler import ButtonMatrix

print("Teste")


async def main():
    event_queue = Queue(maxsize=16)

    feedback = FeedbackController()
    display = DisplayDriver()
    _ = ButtonMatrix(event_queue=event_queue)

    fsm = FSM(event_queue=event_queue, feedback=feedback, display=display)

    await fsm.run()


uasyncio.run(main())
