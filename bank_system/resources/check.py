from domain.resource.work_item import WorkItem

class Check(WorkItem):

    def __init__(self, id_, account_number, value):
        self.id_ = id_
        self.account_number = account_number
        self.value = value
