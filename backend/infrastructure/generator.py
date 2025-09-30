from application.lead.interfaces import InsightGenerator
import random

class InsightGenerator(InsightGenerator):
    def gen(self, content: str) -> dict:
        intents = ["buy", "support", "spam", "job", "other"]
        priorities = ["P0", "P1", "P2", "P3"]
        actions = ["call", "email", "ignore", "qualify"]
        return {
            "intent": random.choice(intents),
            "priority": random.choice(priorities),
            "next_action": random.choice(actions),
            "confidence": round(random.random(), 3),
            "tags": ["auto"],
        }