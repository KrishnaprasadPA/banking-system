import banking_pb2_grpc
import banking_pb2

class Branch:
    def __init__(self, id, initial_balance):
        self.id = id
        self.balance = initial_balance

    def process_event(self, event):
        if event.event_type == CustomerEvent.EventType.DEPOSIT:
            self.balance += event.amount
            return BranchEvent(event_id=event.event_id, event_type=BranchEvent.EventType.PROPAGATE_DEPOSIT, amount=event.amount, branch_id=self.id)
        elif event.event_type == CustomerEvent.EventType.WITHDRAW:
            if event.amount > self.balance:
                return BranchEvent(event_id=event.event_id, event_type=BranchEvent.EventType.PROPAGATE_WITHDRAW, amount=event.amount, branch_id=self.id)
            else:
                self.balance -= event.amount
                return BranchEvent(event_id=event.event_id, event_type=BranchEvent.EventType.PROPAGATE_WITHDRAW, amount=event.amount, branch_id=self.id)
        elif event.event_type == CustomerEvent.EventType.QUERY:
            return None  # Query event does not affect the branch

# Define BranchEvent as mentioned in the .proto file
class BranchEvent:
    def __init__(self, event_id, event_type, amount, branch_id):
        self.event_id = event_id
        self.event_type = event_type
        self.amount = amount
        self.branch_id = branch_id