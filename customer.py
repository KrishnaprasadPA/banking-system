import grpc
import banking_pb2
import banking_pb2_grpc

class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.stub = []

    def createStub(self, branch_address):
        # Create customer stub and connect to respective branch server
        channel = grpc.insecure_channel(f'localhost:{50050+branch_address}')
        self.stub = banking_pb2_grpc.BankingServiceStub(channel)
        return self.stub

    def executeEvents(self):
        # send events to server, accept responses and append them to return to run_customer.py
        responses = []
        responses_by_branch = {}
        for event in self.events:
            result = self.createStub(event.branch).MsgDelivery(banking_pb2.BankingRequest(id=self.id, interface=event.interface, money=event.money))
            self.recvMsg.append((event,result))
            branch_id = event.branch
            if branch_id not in responses_by_branch:
                responses_by_branch[branch_id] = []
            if event.interface.lower() == "query":
                responses_by_branch[branch_id].append(
                    {"interface": event.interface.lower(), "branch": branch_id, "balance": int(result.response_message)}
                )
            else:
                responses_by_branch[branch_id].append(
                    {"interface": event.interface.lower(), "branch": branch_id, "result": result.response_message}
                )
            # Organize responses by branch ID and format them
        for branch_id, branch_responses in responses_by_branch.items():
            response_item = {"id": int(self.id), "recv": branch_responses}
            responses.append(response_item)

        return responses






