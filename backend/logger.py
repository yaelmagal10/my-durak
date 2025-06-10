class Logger:
    def __init__(self, log_table, bot_index):
        self.log_table = log_table
        self.bot_index = bot_index

    def log(self, message):
        if self.log_table is not None and self.bot_index is not None:
            self.log_table[self.bot_index].append(message)

    def get_logs(self):
        return self.log_table[self.bot_index] if self.log_table and self.bot_index is not None else []
