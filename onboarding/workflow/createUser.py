from SpiffWorkflow.specs import Simple

class CreateUser(Simple):
    def _on_complete_hook(self, my_task):
        
