
import cProfile as profile
import time


def speedtest():
    for _ in range(10):
        time.sleep(0.5)



if __name__ == "__main__":
    # Create a profile object
    pr = profile.Profile()
    # Start profiling
    pr.enable()
    # Run the function
    speedtest()
    # Stop profiling
    pr.disable()
    # Print the results
    pr.print_stats(sort='cumulative')