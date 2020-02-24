import time
import multiprocessing

def do_something(seconds):
    print("starting")
    time.sleep(seconds)
    print("done")


start = time.time()
processes = []


# if __name__ == "__main__":
#     for _ in range(100):
#         p = multiprocessing.Process(target=do_something, args=[1.5])
#         p.start()
#         processes.append(p)

#     for process in processes:
#         process.join()

#     finish = time.time()
#     print(finish-start)