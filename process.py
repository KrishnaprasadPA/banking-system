import json
import argparse
import threading

from customer import Customer
from branch import Branch

def read_inputs(input_file):
    with open(input_file, 'r') as f:
        input_data = json.load(f)
    return input_data

def process_input(input_data):
    customers = []
    branches = []

    for i in input_data:
        if i['type'] == 'customer':
            customer = Customer(i['id'], i['events'])
            customers.append(customer)
        elif i['type'] == 'branch':
            branch = Branch(i['id'], i['balance'])
            branches.append(branch)

    return customers, branches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input file for banking system")
    parser.add_argument("input_file", help="Path to the input file")
    args = parser.parse_args()

    input_file = args.input_file
    input_data = read_inputs(input_file)
    customers, branches = process_input(input_data)

    # customer_thread = threading.Thread(target=process_customers, args=(customers,))
    # branch_thread = threading.Thread(target=process_branches, args=(branches,))
    for branch in branches:
        print(branch.id, branch.balance)
    for customer in customers:
        print(customer.customer_id, customer.events)


