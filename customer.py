import grpc
import banking_pb2
import banking_pb2_grpc
import time

class Customer:
    def __init__(self, customer_id, events):
        self.customer_id = customer_id
        self.events = events
        self.stub = None
        self.recvMsg = []

    def createStub(self):
        # Initialize gRPC stub
        channel = grpc.insecure_channel('localhost:50051')  # Adjust the address and port
        self.stub = banking_pb2_grpc.BankingServiceStub(channel)

    def executeEvents(self):
        for event in self.events:
            if event['interface'] == 'query':
                query_event = banking_pb2.CustomerEvent(
                    customer_id=str(self.customer_id),
                    event_type=banking_pb2.CustomerEvent.EventType.QUERY,
                    amount=0,  # For query, amount can be 0
                    event_id=event['id']
                )
                response = self.stub.ProcessCustomerEvents(query_event)
                self.recvMsg.append(response)

            elif event['interface'] == 'deposit':
                deposit_event = banking_pb2.CustomerEvent(
                    customer_id=str(self.customer_id),
                    event_type=banking_pb2.CustomerEvent.EventType.DEPOSIT,
                    amount=event['money'],
                    event_id=event['id']
                )
                response = self.stub.ProcessCustomerEvents(deposit_event)
                self.recvMsg.append(response)

            elif event['interface'] == 'withdraw':
                withdraw_event = banking_pb2.CustomerEvent(
                    customer_id=str(self.customer_id),
                    event_type=banking_pb2.CustomerEvent.EventType.WITHDRAW,
                    amount=event['money'],
                    event_id=event['id']
                )
                response = self.stub.ProcessCustomerEvents(withdraw_event)
                self.recvMsg.append(response)