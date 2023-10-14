import json
import multiprocessing
import sys

import grpc
import banking_pb2
import banking_pb2_grpc
from concurrent.futures import ThreadPoolExecutor

class Branch(banking_pb2_grpc.BankingServiceServicer):
    def __init__(self, branch_id, initial_balance, branches):
        self.branch_id = branch_id
        self.balance = initial_balance
        self.branches = branches

    def Query(self, request, context):
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message=f'Balance: {self.balance}')

    def Withdraw(self, request, context):
        amount = request.amount
        if self.balance >= amount:
            self.balance -= amount
            self.propagate_to_branches(branch_id=self.branch_id, amount=-amount)
            return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Withdraw successful.")
        else:
            return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Insufficient funds.")

    def Deposit(self, request, context):
        self.balance += request.amount
        self.propagate_to_branches(branch_id=self.branch_id, amount=request.amount)
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Deposit successful.")

    def propagate_to_branches(self, branch_id, amount):
        for target_branch_id in self.branches:
            if target_branch_id != branch_id:
                self.propagate_to_branch(branch_id, target_branch_id, amount)

    def propagate_to_branch(self, source_branch_id, target_branch_id, amount):
        channel = grpc.insecure_channel(f'localhost:5005{target_branch_id}', options=(('grpc.enable_http_proxy', 0),))
        stub = banking_pb2_grpc.BankingServiceStub(channel)

        if amount < 0:
            response = stub.PropagateWithdraw(banking_pb2.WithdrawRequest(customer_id=str(source_branch_id), amount=-amount))
        else:
            response = stub.PropagateDeposit(banking_pb2.DepositRequest(customer_id=str(source_branch_id), amount=amount))

        print(f'Propagated {amount} from Branch {source_branch_id} to Branch {target_branch_id}. Response: {response.response_message}')

def start_branch_server(branch_id, initial_balance, branches):
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    branch = Branch(branch_id, initial_balance, branches)
    banking_pb2_grpc.add_BankingServiceServicer_to_server(branch, server)
    server.add_insecure_port(f'[::]:5005{branch_id}')
    server.start()
    print(f'Branch Server 5005{branch_id} started.')
    server.wait_for_termination()

if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Usage: python run_branch.py <input_file>")
    #     sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        data = json.load(f)

    # Extract branch events
    branch_events = [item for item in data if item["type"] == "branch"]
    branches = {item["id"]: item["balance"] for item in branch_events}
    print(branches.items())

    branch_processes = []
    for branch_id, initial_balance in branches.items():
        p = multiprocessing.Process(target=start_branch_server, args=(branch_id, initial_balance, branches))
        p.start()
        # start_branch_server(branch_id, initial_balance, branches)
        branch_processes.append(p)

    # Wait for all branch processes to complete
    for p in branch_processes:
        p.join()

    # Exiting the program
    print("All branch processes completed. Exiting the program.")