import curses
import functools

import logging

logger = logging.getLogger()


def curses_wrapper(func):
    """Wrapper function that initializes curses and calls another function,
    restoring normal keyboard/screen behavior on error.
    The callable object 'func' is then passed the main window 'stdscr'
    as its first argument, followed by any other arguments passed to
    wrapper().
    """

    @functools.wraps(func)
    def run(*args, **kwargs):
        try:
            # State 0 means curses is not initialized
            # State 1 means curses is initialized
            state = 0

            # Initialize curses
            stdscr = curses.initscr()

            # Turn off echoing of keys, and enter cbreak mode,
            # where no buffering is performed on keyboard input
            curses.noecho()
            curses.cbreak()

            # In keypad mode, escape sequences for special keys
            # (like the cursor keys) will be interpreted and
            # a special value like curses.KEY_LEFT will be returned
            stdscr.keypad(1)

            # Start color, too.  Harmless if the terminal doesn't have
            # color; user can test with has_color() later on.  The try/catch
            # works around a minor bit of over-conscientiousness in the curses
            # module -- the error return from C start_color() is ignorable.
            try:
                curses.start_color()
                for i in range(0, curses.COLORS):
                    curses.init_pair(i + 1, i, 0)
                logger.info("Color Initialized: %i", curses.COLORS)
            except:
                logger.warn("WARN: Color not available.")
            curses.set_escdelay(15)
            state = 1
            return func(stdscr, *args, **kwargs)
        except Exception as e:
            if state == 1:
                if "stdscr" in locals():
                    stdscr.keypad(0)
                curses.echo()
                curses.nocbreak()
                curses.endwin()
                curses.set_escdelay(1000)
                state = 0
            logger.exception(e)
        except KeyboardInterrupt as e:
            pass
        finally:
            if state == 1:
                # Set everything back to normal
                if "stdscr" in locals():
                    stdscr.keypad(0)
                curses.echo()
                curses.nocbreak()
                curses.endwin()
                state == 0

    return run
