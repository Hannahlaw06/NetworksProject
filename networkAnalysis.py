import subprocess

#up/down rate
def test_speed(hostName):
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Mbps
    upload_speed = st.upload() / 1_000_000  # Mbps
    return download_speed, upload_speed

#transfer times

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