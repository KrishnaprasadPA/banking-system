import json
import sys

import banking_pb2
import customer

# Function to process events for a customer
def process_customer_events(id, events):
    responses = []
    currentCustomer=customer.Customer(str(id), events)
    currentCustomer.createStub(id)
    responses = currentCustomer.executeEvents()
    return {'id': id, 'recv': responses}


# Read the input file and process events for each customer
if len(sys.argv) != 2:
    print("Usage: python3 run_customer.py <input_file>")
    sys.exit(1)
input_file = sys.argv[1]
with open(input_file) as f:
    data = json.load(f)
output = []
for item in data:
    if item["type"] == "customer":
        id = item["id"]
        events_data = item["events"]
        events = []
        for event_data in events_data:
            interface = event_data["interface"].upper()
            if interface == "QUERY":
                event = banking_pb2.CustomerEvent(interface=interface)
            else:
                money = event_data.get("money", 0) if "money" in event_data else 0
                event = banking_pb2.CustomerEvent(interface=interface, money=money)
            events.append(event)
        print(f"\nProcessing events for Customer {id}:")
        response = process_customer_events(id, events)

        output.append(response)

# Write the output to a JSON file
with open('output.json', 'w') as outfile:
    json.dump(output, outfile, indent=4)

print("Output written to 'output.json'.")