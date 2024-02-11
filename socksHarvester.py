#!/usr/bin/python

from rich.console import Console
from rich.panel import Panel
import socket
import threading
import struct
import argparse
from urllib.request import Request, urlopen
import queue 
import re
import os
import logging



# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

console = Console()

def show_panel():
    panel = Panel("[bold cyan]SocksHarvester[/bold cyan]\nCheck For Valid SOCKS Proxy", subtitle="[yellow]Author: Ömer ŞAYAK[/yellow]")
    console.print(panel)

socksProxies = queue.Queue()
checkQueue = queue.Queue()

class ThreadChecker(threading.Thread):
    def __init__(self, queue, timeout):
        super().__init__()
        self.timeout = timeout
        self.q = queue
        self.daemon = True

    def isSocks4(self, host, port, soc):
        try:
            ipaddr = socket.inet_aton(host)
            port_pack = struct.pack(">H", port)
            packet4 = b"\x04\x01" + port_pack + ipaddr + b"\x00"
            soc.sendall(packet4)
            data = soc.recv(8)
            return len(data) == 8 and data[0] == 0x00 and data[1] == 0x5A
        except socket.error as e:
            logging.debug(f'SOCKS4 test failed for {host}:{port}, Error: {e}')
            return False

    def isSocks5(self, host, port, soc):
        try:
            soc.sendall(b"\x05\x01\x00")
            data = soc.recv(2)
            return len(data) == 2 and data[0] == 0x05 and data[1] == 0x00
        except socket.error as e:
            logging.debug(f'SOCKS5 test failed for {host}:{port}, Error: {e}')
            return False

    def getSocksVersion(self, proxy):
        host, port = proxy.split(":")
        port = int(port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(self.timeout)
            try:
                s.connect((host, port))
                if self.isSocks4(host, port, s):
                    return 4
                elif self.isSocks5(host, port, s):
                    return 5
            except (socket.timeout, socket.error) as e:
                logging.debug(f'Connection failed for {host}:{port}, Error: {e}')
        return 0

    def run(self):
        while True:
            proxy = self.q.get()
            version = self.getSocksVersion(proxy)
            if version in [4, 5]:
                logging.info(f'Working: {proxy}')
                socksProxies.put(proxy)
            self.q.task_done()

def get_proxies(source):
    pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}"
    data = ""
    try:
        with open(source) as file:
            data += file.read()
        logging.info(f'Processed: {source}')
    except Exception as e:
        logging.error(f'Error: Could not process {source}, Error: {e}')
    return re.findall(pattern, data)

def start_socker(proxies, outputPath, threads, timeout):
    logging.info(f'Loaded {len(proxies)} proxies.')
    for proxy in proxies:
        checkQueue.put(proxy)

    for _ in range(threads):
        ThreadChecker(checkQueue, timeout).start()

    checkQueue.join()

    with open(outputPath, "w") as outputFile:
        while not socksProxies.empty():
            outputFile.write(socksProxies.get() + "\n")

    logging.info(f'Testing complete. Working proxies saved to {outputPath}.')

parser = argparse.ArgumentParser(description="SocksHarvester - Check For Valid SOCKS Proxy. A tool to check and list valid SOCKS proxies.")
parser.add_argument("-o", "--output", default="live_proxies.txt", help="Output file for live proxies")
parser.add_argument("-th", "--thread", type=int, default=30, help="Number of concurrent threads")
parser.add_argument("-t", "--timeout", type=float, default=5.0, help="Timeout for each proxy check")
parser.add_argument("-i", "--input", required=True, help="Input file containing proxies")

if __name__ == "__main__":
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logging.error(f"Error: Input file '{args.input}' not found.")
        exit(1)

    show_panel() # Show the panel
    proxies = get_proxies(args.input)
    if proxies:
        start_socker(proxies, args.output, args.thread, args.timeout)
    else:
        logging.error("No proxies found.")
