import grpc
import banking_pb2
import banking_pb2_grpc

class Branch(banking_pb2_grpc.BankingServiceServicer):
    def __init__(self, branch_id, balance, branches):
        self.branch_id = branch_id
        self.balance = balance
        self.branches = branches

# function to accept requests from customers
    def MsgDelivery(self, request, context):
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
        return banking_pb2.BankingResponse(customer_id=request.id, response_message=str(self.balance))

# performs withdraw operation if possible and returns success or failure message after propagating withdraw
    def Withdraw(self, request, context):
        money = request.money
        if self.balance >= money:
            self.balance -= money
            self.propagate_to_branches(branch_id=self.branch_id, money=-money)
            return banking_pb2.BankingResponse(customer_id=request.id, response_message="success")
        else:
            return banking_pb2.BankingResponse(customer_id=request.id, response_message="failure")

    # performs deposit operation and returns success message after propagating deposit
    def Deposit(self, request, context):
        self.balance += request.money
        self.propagate_to_branches(branch_id=self.branch_id, money=request.money)
        return banking_pb2.BankingResponse(customer_id=request.id,  response_message="success")

    def Propagate_Deposit(self, request, context):
        self.balance += request.money
        return banking_pb2.BankingResponse(customer_id=request.id, response_message="Deposit propagated successfully.")

    def Propagate_Withdraw(self, request, context):
        self.balance -= request.money
        return banking_pb2.BankingResponse(customer_id=request.id, response_message="Withdraw propagated successfully.")

# propagate deposit or withdraw to all branches other than the source branch
    def propagate_to_branches(self, branch_id, money):
        for target_branch_id in self.branches:
            if target_branch_id != branch_id:
                self.propagate_to_branch(branch_id, target_branch_id, money)

    def propagate_to_branch(self, source_branch_id, target_branch_id, money):
        channel = grpc.insecure_channel(f'localhost:{50050+target_branch_id}')
        stub = banking_pb2_grpc.BankingServiceStub(channel)
        if money < 0:
            response = stub.Propagate_Withdraw(banking_pb2.PropagateRequest(id=str(source_branch_id), money=-money))
        else:
            response = stub.Propagate_Deposit(banking_pb2.PropagateRequest(id=str(source_branch_id), money=money))
        print(f'Propagated {money} from Branch {source_branch_id} to Branch {target_branch_id}. Response: {response.response_message}')