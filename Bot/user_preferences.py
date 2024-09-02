import json

class UserPreferences:
    def __init__(self, filename='user_preferences.json'):
        self.filename = filename
        self.preferences = self.load_preferences()

    def load_preferences(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_preferences(self):
        with open(self.filename, 'w') as f:
            json.dump(self.preferences, f)

    def set_user_chains(self, user_id, chains):
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        self.preferences[user_id]['chains'] = chains
        self.save_preferences()

    def set_user_threshold(self, user_id, chain, threshold):
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        if 'thresholds' not in self.preferences[user_id]:
            self.preferences[user_id]['thresholds'] = {}
        self.preferences[user_id]['thresholds'][chain] = threshold
        self.save_preferences()

    def get_user_chains(self, user_id):
        return self.preferences.get(user_id, {}).get('chains', [])

    def get_user_threshold(self, user_id, chain):
        return self.preferences.get(user_id, {}).get('thresholds', {}).get(chain)