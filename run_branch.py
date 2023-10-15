import json
import multiprocessing
import sys

import branch
import grpc
import banking_pb2_grpc
from concurrent.futures import ThreadPoolExecutor


def start_branch_server(branch_id, initial_balance, branches):
    # Start multiple branch servers
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    branch1 = branch.Branch(branch_id, initial_balance, branches)
    banking_pb2_grpc.add_BankingServiceServicer_to_server(branch1, server)
    server.add_insecure_port(f'[::]:{50050+branch_id}')
    server.start()
    print(f'Branch Server {50050+branch_id} started.')
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 run_branch.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        data = json.load(f)

    # Extract branch events
    branch_events = [item for item in data if item["type"] == "branch"]
    branches = {item["id"]: item["balance"] for item in branch_events}


    branch_processes = []
    for branch_id, initial_balance in branches.items():
        p = multiprocessing.Process(target=start_branch_server, args=(branch_id, initial_balance, branches))
        p.start()
        branch_processes.append(p)

    # Wait for all branch processes to complete
    for p in branch_processes:
        p.join()
