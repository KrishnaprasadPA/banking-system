import json
import os

import grpc
import banking_pb2
import banking_pb2_grpc

class Branch(banking_pb2_grpc.BankingServiceServicer):
    def __init__(self, branch_id, balance, branches):
        self.branch_id = branch_id
        self.balance = balance
        self.branches = branches
        self.branch_events = []
        self.branch_clock = 0

# function to accept requests from customers
    def MsgDelivery(self, request, context):
        # self.branch_clock = request.clock
        self.branch_clock += 1
        request.clock += 1
        self.log_event(request.customer_request_id, request.clock, request.interface.lower(), f"event_recv from customer {self.branch_id}")
        if request.interface == "QUERY":
            return self.Query(request,context)
        elif request.interface == "WITHDRAW":
            return self.Withdraw(request, context)
        elif request.interface == "DEPOSIT":
            return self.Deposit(request, context)
        else:
            return

# returns balance
    def Query(self, request, context):
         return banking_pb2.BankingResponse(customer_id=request.id, response_message=f"balance: {self.balance}")

# performs withdraw operation if possible and returns success or failure message after propagating withdraw
    def Withdraw(self, request, context):
        money = request.money
        if self.balance >= money:
            self.balance -= money
            self.propagate_to_branches(request=request,branch_id=self.branch_id, money=-money)
            return banking_pb2.BankingResponse(customer_id=request.id, response_message="success")
        else:
            return banking_pb2.BankingResponse(customer_id=request.id, response_message="failure")

    # performs deposit operation and returns success message after propagating deposit
    def Deposit(self, request, context):
        self.balance += request.money
        self.propagate_to_branches(request=request,branch_id=self.branch_id, money=request.money)
        return banking_pb2.BankingResponse(customer_id=request.id,  response_message="success")

    def Propagate_Deposit(self, request, context):
        self.balance += request.money
        self.branch_clock += 1
        request.clock += 1
        self.log_event(request.customer_request_id, request.clock, "propagate_deposit", f"event_recv from branch {request.id}")
        return banking_pb2.BankingResponse(customer_id=request.id, response_message="Deposit propagated successfully.")

    def Propagate_Withdraw(self, request, context):
        self.balance -= request.money
        self.branch_clock += 1
        request.clock += 1
        self.log_event(request.customer_request_id, request.clock, "propagate_withdraw", f"event_recv from branch {request.id}")
        return banking_pb2.BankingResponse(customer_id=request.id, response_message="Withdraw propagated successfully.")

# propagate deposit or withdraw to all branches other than the source branch
    def propagate_to_branches(self, request, branch_id, money):
        for target_branch_id in self.branches:
            if target_branch_id != branch_id:
                self.propagate_to_branch(request, branch_id, target_branch_id, money)

    def propagate_to_branch(self, request, source_branch_id, target_branch_id, money):
        channel = grpc.insecure_channel(f'localhost:{50050+target_branch_id}')
        stub = banking_pb2_grpc.BankingServiceStub(channel)
        if money < 0:
            response = stub.Propagate_Withdraw(
                banking_pb2.PropagateRequest(customer_request_id=request.customer_request_id, id=str(source_branch_id),
                                             money=-money, clock=request.clock))
            self.branch_clock += 1
            request.clock += 1
            self.log_event(request.customer_request_id, request.clock, "propagate_withdraw", f"event_sent to branch {target_branch_id}")
        else:
            response = stub.Propagate_Deposit(
                banking_pb2.PropagateRequest(customer_request_id=request.customer_request_id, id=str(source_branch_id),
                                             money=money, clock=request.clock))
            self.branch_clock += 1
            request.clock += 1
            self.log_event(request.customer_request_id, request.clock, "propagate_deposit", f"event_sent to branch {target_branch_id}")
        print(f'Propagated {money} from Branch {source_branch_id} to Branch {target_branch_id}. Response: {response.response_message}')

    def log_event(self, customer_request_id, logical_clock, interface, comment):
        branch_event = {
            "customer-request-id": customer_request_id,
            "logical_clock": self.branch_clock,
            "interface": interface,
            "comment": comment
        }
        event = {
            "id": self.branch_id,
            "customer-request-id": customer_request_id,
            "type": "branch",
            "logical_clock": logical_clock,
            "interface": interface,
            "comment": comment
        }

        self.branch_events.append(branch_event)
        self.write_events_to_file()

        try:
            with open(f'temp_all_events_{customer_request_id}.json', 'r') as infile:
                existing_list = json.load(infile)
        except FileNotFoundError:
            existing_list = []

        # Add the new event to the existing list
        existing_list.append(event)

# Write the updated list to the file, overwriting its existing contents
        with open(f'temp_all_events_{customer_request_id}.json', 'w') as outfile:
            json.dump(existing_list, outfile, indent=2)

        # try:
        #     with open('output_3.json', 'r') as infile:
        #         existing_list = json.load(infile)
        #         # if not isinstance(existing_list, list):
        #         #     # If it's not a list, create a new list with the existing data
        #         #     existing_list = [existing_list]
        #         existing_list.append(event)
        #         json.dump(existing_list, outfile, indent=2)
        # except FileNotFoundError:
        #     with open('output_3.json', 'w') as file:
        #         json.dump([event], file, indent=2)

    def write_events_to_file(self):
        # Group the events by branch ID
        output = {"id": self.branch_id, "type": "branch", "events": self.branch_events}

        # Write the events to the file as JSON
        with open(f'temp_output_branch_{self.branch_id}.json', 'w') as outfile2:
            json.dump(output, outfile2, indent=2)
