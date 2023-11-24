import json
import sys

import banking_pb2
import customer

# Function to process events for a customer
def process_customer_events(id, events):
    currentCustomer=customer.Customer(str(id), events)
    return currentCustomer.executeEvents()


# Read the input file and process events for each customer
if len(sys.argv) != 2:
    print("Usage: python3 run_customer.py <input_file>")
    sys.exit(1)
input_file = sys.argv[1]
with open(input_file) as f:
    data = json.load(f)
output = []
# group events of customer by id, process them and append results to output
for item in data:
    if item["type"] == "customer":
        id = item["id"]
        events_data = item["events"]
        events = []
        for event_data in events_data:
            interface = event_data["interface"].upper()
            branch = event_data["branch"]
            money = event_data.get("money", 0) if "money" in event_data else 0
            event = banking_pb2.CustomerEvent(interface=interface, money=money, branch=branch)
            events.append(event)
        print(f"\nProcessing events for Customer {id}:")
        output.extend(process_customer_events(id, events))

# Write the output to a JSON file
with open('output.json', 'w') as outfile:
    json.dump(output, outfile, indent=2)

print("Output written to 'output.json'")