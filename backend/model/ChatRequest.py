from numpy import long


class ChatRequest:
    def __init__(self):
        self.human_input = ""
        self.conversation_id:int = 0
        self.clear_history:bool = False

    def get_human_input(self) -> str:
        return self.human_input
    def get_conversation_id(self) -> int:
        return self.conversation_id
    def get_clear_history(self) -> bool:
        return self.clear_history

    def set_human_input(self, human_input: str):
        self.human_input = human_input
    def set_clear_history(self, clear_history: bool):
        self.clear_history = clear_history
    def set_conversation_id(self, conversation_id: int):
        self.conversation_id = conversation_id
