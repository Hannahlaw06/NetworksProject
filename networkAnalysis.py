import subprocess
import speedtest
import time
from datetime import datetime
import psutil
import requests
import csv


csv_header = ['Timestamp', 'Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Download Time (s)', 'Upload Time (s)', 'Ping (ms)', 'Data Sent (KB)', 'Data Received (KB)']

#file to save data to
def initialize_csv(file_name='network_analysis.csv'):
    #Initialize CSV file with header if it doesn't exist
    try:
        with open(file_name, mode='r') as file:
            pass  # File exists, no need to write header
    except FileNotFoundError:
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(csv_header)  # Write header

def save_to_csv(data, file_name='network_analysis.csv'):
    #Save results to a CSV file
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def get_server_input():
    server = input("Enter the server address (IP or domain): ")
    return server

#up/download rate
def upDown():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Mbps
    upload_speed = st.upload() / 1_000_000  # Mbps
    return download_speed, upload_speed

#transfer times
def transTime(url, destination):
    start_time = time.time()
    response = requests.get(url, stream=True)
    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    end_time = time.time()
    return end_time - start_time

#sys response times
def pingTest(hostName):
    try:
        response = subprocess.run(["ping", "-c", "4", hostName], capture_output=True, text=True)
        if response.returncode == 0:
            print(f"Ping to {hostName}")
            print(response.stdout)
        else:
            print(f"Failed to ping {hostName}")
    except Exception as e:
        print(f"Error while pinging {hostName}: {e}")



def netAnalysis(file_to_test, file_name='network_analysis.csv'):
    server = get_server_input()
    initialize_csv(file_name)

    print("Running upload/download speed test...")
    download_speed, upload_speed = upDown()
    print(f"Download Speed: {download_speed:.2f} Mbps")
    print(f"Upload Speed: {upload_speed:.2f} Mbps")

        # Example: Measure file transfer time
    print("\nMeasuring file transfer time...")
    file_url = file_to_test
    destination = "samplefile.zip"
    transfer_time = transTime(file_url, destination)
    print(f"File transferred in {transfer_time:.2f} seconds")

    print("\nMeasuring system response time...")
    pingTest(server)
        


netAnalysis("https://crouton.net/crouton.png", "network_analysis.csv")