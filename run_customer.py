import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import banking_pb2
import customer

# Function to process events for a customer
# def  process_customer_events(id, events):
#     responses = []
#     currentCustomer=customer.Customer(str(id), events)
#     currentCustomer.createStub(id)
#     responses = currentCustomer.executeEvents()
#     return {'id': id, 'type': "customer", 'events': responses}
def process_customer_events(current_customer):
    return {'id': current_customer.id, 'type': "customer", 'events': current_customer.executeEvents()}



# Read the input file and process events for each customer
if len(sys.argv) != 2:
    print("Usage: python3 run_customer.py <input_file>")
    sys.exit(1)
input_file = sys.argv[1]
with open(input_file) as f:
    data = json.load(f)
output = OrderedDict()
customers = []
customer_ids = []
request_ids = []
# group events of customer by id, process them and append results to output
for item in data:
    if item["type"] == "customer":
        id = item["id"]
        customer_ids.append(id)
        events_data = item["customer-requests"]
        events = []
        clock=1
        for event_data in events_data:
            interface = event_data["interface"].upper()
            customer_request_id = event_data["customer-request-id"]
            request_ids.append(customer_request_id)
            # if interface == "QUERY":
            #     event = banking_pb2.CustomerEvent(interface=interface, clock=1)
            # else:
            money = event_data.get("money", 0) if "money" in event_data else 0
            event = banking_pb2.CustomerEvent(customer_request_id=str(customer_request_id), interface=interface, money=money,
                                              clock=clock)
            clock = clock + 1
            events.append(event)
        current_customer = customer.Customer(str(id), events)
        current_customer.createStub(id)
        customers.append(current_customer)
        # print(f"\nProcessing events for Customer {id}:")
        # response = process_customer_events(id, events)
        # output.append(response)
# # Write the output to a JSON file
# with open('output_1.json', 'w') as outfile:
#     json.dump(output, outfile, indent=2)
#
# print("Output written to 'output_1.json'")

# Process customer events concurrently and maintain the order by ID
with ThreadPoolExecutor() as executor:
    results = executor.map(process_customer_events, customers)

    # Collect results in ordered dictionary by customer ID
    for result in results:
        output[result['id']] = result

# Write the output to a JSON file ordered by customer ID
with open('output_1.json', 'w') as outfile:
    json.dump(list(output.values()), outfile, indent=2)

all_branch_events = []

for branch_id in customer_ids:
    filename = f'temp_output_branch_{branch_id}.json'

    try:
        with open(filename, 'r') as file:
            branch_data = json.load(file)
            all_branch_events.append(branch_data)
    except FileNotFoundError:
        print(f"File {filename} not found.")

# Write all branch events to the output_2.json file
with open('output_2.json', 'w') as outfile1:
    json.dump(all_branch_events, outfile1, indent=2)

try:
    for branch_id in customer_ids:
        os.remove(f'temp_output_branch_{branch_id}.json')
except FileNotFoundError:
    print(f'temp_output_branch{branch_id} not found.')

# Write all events to the output_3.json file
all_events = []
for request_id in request_ids:
    filename = f'temp_all_events_{request_id}.json'

    try:
        with open(filename, 'r') as file:
            all_data = json.load(file)
            all_events.extend(all_data)
    except FileNotFoundError:
        print(f"File {filename} not found.")

with open('output_3.json', 'w') as outfile2:
    json.dump(all_events, outfile2, indent=2)

try:
    for request_id in request_ids:
        os.remove(f'temp_all_events_{request_id}.json')
except FileNotFoundError:
    print(f'temp_all_events_{request_id} not found.')

print("Customer output written to 'output_1.json' ordered by customer ID")
print("Branch output written to 'output_2.json' ordered by branch ID")
print("Customer and Branch event flow output written to 'output_3.json'")