import grpc
import time
import banking_pb2
import banking_pb2_grpc

class Customer:
    def __init__(self, customer_id, events):
        self.customer_id = customer_id
        self.events = events
        self.recvMsg = []
        self.stub = None

    def createStub(self, branch_address):
        channel = grpc.insecure_channel(branch_address)
        self.stub = banking_pb2_grpc.BankingServiceStub(channel)

    def executeEvents(self):
        for event in self.events
        for event in self.events:
            if event.interface == 'QUERY':
                response = self.stub.Query(banking_pb2.QueryRequest(customer_id=self.customer_id))
                self.recvMsg.append((event, response))
            elif event.interface == 'DEPOSIT':
                response = self.stub.Deposit(banking_pb2.DepositRequest(customer_id=self.customer_id, amount=event.amount))
                self.recvMsg.append((event, response))
            elif event.interface == 'WITHDRAW':
                response = self.stub.Withdraw(banking_pb2.WithdrawRequest(customer_id=self.customer_id, amount=event.amount))
                self.recvMsg.append((event, response))
            else:
                print(f"Unknown event type: {event.interface}")

        # Print received messages
        for event, response in self.recvMsg:
            print(f"Event: {event.interface}, Amount: {event.amount}, Response: {response.success}")