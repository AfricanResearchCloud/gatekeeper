from SpiffWorkflow.serializer.json import JSONSerializer
from createUser import CreateUser

class OnboardingSerializer(JSONSerializer):
    def serialize_create_user(self, task_spec):
        return self.serialize_task_spec(task_spec)

    def deserialize_create_user(self, wf_spec, s_state):
        spec = CreateUser(wf_spec, s_state['name'])
        self.deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec
