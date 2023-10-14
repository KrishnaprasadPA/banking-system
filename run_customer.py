import json
import time
import grpc
import banking_pb2
import banking_pb2_grpc

# Function to process events for a customer
def process_customer_events(customer_id, events):
    # Establish a gRPC channel to the respective branch
    channel = grpc.insecure_channel(f'localhost:5005{customer_id}', options=(('grpc.enable_http_proxy', 0),))
    stub = banking_pb2_grpc.BankingServiceStub(channel)


    responses = []

    for event in events:
        time.sleep(1)  # Simulate 1 second delay between events


        if event.interface == "QUERY":
            response = stub.Query(banking_pb2.QueryRequest(customer_id=str(customer_id)))
            responses.append({'interface': 'query', 'result': f'balance: {response.balance}'})

        elif event.interface == "DEPOSIT":
            request = banking_pb2.DepositRequest(customer_id=str(customer_id), amount=event.money)
            response = stub.Deposit(request)
            responses.append({'interface': 'deposit', 'result': response.result})

        elif event.interface == "WITHDRAW":
            request = banking_pb2.WithdrawRequest(customer_id=str(customer_id), amount=event.money)
            response = stub.Withdraw(request)
            responses.append({'interface': 'withdraw', 'result': response.result})

    return {'id': customer_id, 'recv': responses}

# Read the input file and process events for each customer
with open('input.json', 'r') as file:
    data = json.load(file)

output = []

for item in data:
    if item["type"] == "customer":
        customer_id = item["id"]
        events_data = item["events"]
        events = []
        for event_data in events_data:
            interface = event_data["interface"].upper()
            # print(event_data)

            if interface == "QUERY":
                event = banking_pb2.CustomerEvent(interface=interface)
                # print(event)
                # print("if block")
            else:
                money = event_data.get("money", 0) if "money" in event_data else 0
                event = banking_pb2.CustomerEvent(interface=interface, money=money)

            events.append(event)
            # print(events)

        print(f"\nProcessing events for Customer {customer_id}:")
        response = process_customer_events(customer_id, events)
        output.append(response)

# Write the output to a JSON file
with open('output.json', 'w') as outfile:
    json.dump(output, outfile, indent=4)

print("Output written to 'output.json'.")