import json

import grpc
import banking_pb2
import banking_pb2_grpc

class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.stub = None

    def createStub(self, branch_address):
        # Create customer stub and connect to respective branch server
        channel = grpc.insecure_channel(f'localhost:{50050+branch_address}')
        self.stub = banking_pb2_grpc.BankingServiceStub(channel)

    def executeEvents(self):
        # send events to server, accept responses and append them to return to run_customer.py
        responses = []
        for event in self.events:
            # Write events to output_3.json file
            customer_event = {"id": self.id, 'customer-request-id': event.customer_request_id, "type": "customer",
                              'logical_clock': event.clock, 'interface': event.interface.lower(),
                              'comment': f"event_sent from customer {self.id}"}
            # try:
            #     with open('output_3.json', 'r+') as outfile:
            #         existing_list = json.load(outfile)
            #         if not isinstance(existing_list, list):
            #             # If it's not a list, create a new list with the existing data
            #             existing_list = [existing_list]
            #         existing_list.append(customer_event)
            #         outfile.seek(0)
            #         json.dump(existing_list, outfile, indent=2)
            # except FileNotFoundError:
            #     with open('output_3.json', 'w') as file:
            #         json.dump([customer_event], file, indent=2)
            try:
                with open(f'temp_all_events_{event.customer_request_id}.json', 'r') as infile:
                    existing_list = json.load(infile)
            except FileNotFoundError:
                existing_list = []

            # Add the new event to the existing list
            existing_list.append(customer_event)

            # Write the updated list to the file, overwriting its existing contents
            with open(f'temp_all_events_{event.customer_request_id}.json', 'w') as outfile:
                json.dump(existing_list, outfile, indent=2)

            # Compute result
            result = self.stub.MsgDelivery(
                banking_pb2.BankingRequest(customer_request_id=event.customer_request_id,id=self.id, interface=event.interface, money=event.money,clock=event.clock))
            self.recvMsg.append((event, result))
            print(f"Processing customer {self.id}, request {event.customer_request_id}")
            responses.append({'customer-request-id': event.customer_request_id, 'logical_clock': event.clock,
                              'interface': event.interface.lower(), 'comment': f"event_sent from customer {self.id}"})
        return responses
