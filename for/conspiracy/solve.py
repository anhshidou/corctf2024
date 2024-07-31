from scapy.all import *
import ast

# Read the packets from the pcap file
packets = rdpcap("E:\\CTF\\corctf2024\\conspiracy\\challenge.pcap")  # Replace with the path to your pcap file

# Separate packets into messages and keys
messages_packets = []
keys_packets = []

for packet in packets:
    if packet.haslayer(Raw):
        try:
            payload = packet[Raw].load.decode("utf-8", errors="ignore")
            if payload.startswith("["):
                # Payload is a list, either message or keys
                if len(messages_packets) <= len(keys_packets):
                    messages_packets.append(payload)
                else:
                    keys_packets.append(payload)
        except UnicodeDecodeError:
            pass

# Decrypt the messages
original_messages = []
for encrypted_message, key in zip(messages_packets, keys_packets):
    encrypted_message = ast.literal_eval(encrypted_message)
    key = ast.literal_eval(key)
    original_message = "".join(chr(int(enc_msg / k)) for enc_msg, k in zip(encrypted_message, key))
    original_messages.append(original_message)

# Print the decrypted messages
for message in original_messages:
    print(message)
