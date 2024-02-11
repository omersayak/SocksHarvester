# SocksHarvester

SocksHarvester quickly tests SOCKS4/5 proxies and lists the valid ones. Ideal for network professionals with its multi-threading support.

## Features

- Fast SOCKS4 and SOCKS5 proxy testing.
- Multi-threading for efficient proxy checking.
- Outputs valid proxies to a specified file.

## Getting Started

Ensure you have Python 3.6+ installed on your system.

### Installing Dependencies

Install the required libraries using:


    pip install -r requirements.txt


Usage

    python socksharvester.py -i your_proxy_list.txt -o valid_proxies.txt 


Parameters:

    -i or --input: Path to the input file with proxies.
    -o or --output: Path to the output file for valid proxies.
    -th or --thread: (Optional) Number of concurrent threads (default is 30).
    -t or --timeout: (Optional) Timeout in seconds for each proxy check (default is 5.0).


Developer

Developed by Ömer ŞAYAK, SocksHarvester is an open-source tool designed to streamline the process of validating proxy servers for network professionals.
