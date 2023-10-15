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
        channel = grpc.insecure_channel(f'localhost:{50050+branch_address}')
        self.stub = banking_pb2_grpc.BankingServiceStub(channel)

    def executeEvents(self):
            # for event in self.events
            responses = []
            for event in self.events:
                result = self.stub.MsgDelivery(banking_pb2.BankingRequest(id=self.id, interface=event.interface, money= event.money))
                self.recvMsg.append((event,result))
                responses.append({'interface': event.interface.lower(), 'result': result.response_message})
            return responses