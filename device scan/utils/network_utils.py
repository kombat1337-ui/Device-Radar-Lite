import socket
import ipaddress

def get_local_subnet():
    """
    Determines the local IPv4 subnet (assumes /24 mask)
    by opening a UDP socket to a public IP.
    Returns a string like '192.168.1.0/24'.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    net = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return str(net)
