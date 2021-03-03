from sentence_list import SentenceList

class Controller():
    def __init__(self, sentence_lists):
        super().__init__()

        self.sentence_lists = sentence_lists
        self.current_list = None
        self.get_start_list() # Get initial sentence list
        self.deleted_lists = []
        self.current_sentence = ""
        self.sentence_active = False

    def get_start_list(self):
        """Get first sentence list"""
        if self.sentence_lists:
            self.current_list = self.sentence_lists[0]
        else:
            self.current_list = SentenceList()

    def print_all_lists(self):
        """For testing purposes to see all sentence lists """
        for sentence_list in self.sentence_lists:
            print(sentence_list.sentences)
            print(sentence_list.title)
            print(sentence_list.num_correct)