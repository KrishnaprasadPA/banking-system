import grpc
import banking_pb2
import banking_pb2_grpc

class Branch(banking_pb2_grpc.BankingServiceServicer):
    def __init__(self, branch_id, initial_balance, branches):
        self.branch_id = branch_id
        self.balance = initial_balance
        self.branches = branches

    def MsgDelivery(self, request, context):
        if request.

    def Query(self, request, context):
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message=f'balance: {self.balance}')

    def Withdraw(self, request, context):
        money = request.money
        if self.balance >= money:
            self.balance -= money
            self.propagate_to_branches(branch_id=self.branch_id, money=-money)
            return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="success")
        else:
            return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="failure")

    def Deposit(self, request, context):
        self.balance += request.money
        self.propagate_to_branches(branch_id=self.branch_id, money=request.money)
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Deposit successful.")

    def PropagateDeposit(self, request, context):
        self.balance += request.money
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Deposit propagated successfully.")

    def PropagateWithdraw(self, request, context):
        self.balance -= request.money
        return banking_pb2.BankingResponse(customer_id=request.customer_id, response_message="Withdraw propagated successfully.")

    def propagate_to_branches(self, branch_id, money):
        for target_branch_id in self.branches:
            if target_branch_id != branch_id:
                self.propagate_to_branch(branch_id, target_branch_id, money)

    def propagate_to_branch(self, source_branch_id, target_branch_id, money):
        channel = grpc.insecure_channel(f'localhost:{5005 + target_branch_id}')
        stub = banking_pb2_grpc.BankingServiceStub(channel)

        if money < 0:
            response = stub.PropagateWithdraw(banking_pb2.WithdrawRequest(customer_id=str(source_branch_id), money=-money))
        else:
            response = stub.PropagateDeposit(banking_pb2.DepositRequest(customer_id=str(source_branch_id), money=money))

        print(f'Propagated {money} from Branch {source_branch_id} to Branch {target_branch_id}. Response: {response.response_message}')