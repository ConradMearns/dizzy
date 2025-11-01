class Service:
    def __init__(self):
        self.command_queue = []
        self.event_queue = []

        self.command_map = {
            commands.ExampleCommand = [ procedures.ExampleProcedure ],
        }

        self.procedure_map = {
                procedures.ExampleProcedure: procedures.ExampleProcedureContext(...),
        }

        self.event_map = {
            events.ExampleEvent = [ policy.ExamplePolicy ],
        }

        self.policy_map = {
                policy.ExamplePolicy: policy.ExamplePolicyContext(...),
        }

    def emit_event(self, event):
        self.event_queue.append(event)

    def emit_command(self, command):
        self.command_queue.append(command)

    def run(self):
        while self.command_queue:
            while self.command_queue:
                command = self.command_queue.pop(0) # FIFO
                for procedure in self.command_map[type(command)]:
                    context = self.procedure_map[procedure]
                    procedure(context = context, command = command)

            while self.event_queue:
                event = self.event_queue.pop(0) # FIFO
                for policy in self.event_map(type(event))
                    context = self.policy_map[policy]
                    policy(context = context, event = event)


