import time
from threading import Thread

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
}

def task():
    print('download html')
    time.sleep(1)

if __name__ == '__main__':
    start_time = time.time()
    thread = []
    for i in range(5):
        th = Thread(target=task)
        th.start()
        thread.append(th)

    for th in thread:
        th.join()

    print('总耗时：{}'.format(time.time() - start_time))
