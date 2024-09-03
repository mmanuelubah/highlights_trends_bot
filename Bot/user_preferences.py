class UserPreferences:
    def __init__(self):
        self.preferences = {}

    def set_alert(self, user_id, chain, threshold):
        """
        Set an alert threshold for a specific user and chain.
        """
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        if 'alerts' not in self.preferences[user_id]:
            self.preferences[user_id]['alerts'] = {}
        self.preferences[user_id]['alerts'][chain] = threshold

    def get_alert(self, user_id, chain):
        """
        Get the alert threshold for a specific user and chain.
        Returns None if no alert is set.
        """
        return self.preferences.get(user_id, {}).get('alerts', {}).get(chain)

    def remove_alert(self, user_id, chain):
        """
        Remove an alert for a specific user and chain.
        """
        if user_id in self.preferences and 'alerts' in self.preferences[user_id]:
            self.preferences[user_id]['alerts'].pop(chain, None)

    def get_all_alerts(self, user_id):
        """
        Get all alerts for a specific user.
        Returns an empty dict if no alerts are set.
        """
        return self.preferences.get(user_id, {}).get('alerts', {})

    def clear_user_preferences(self, user_id):
        """
        Clear all preferences for a user.
        """
        self.preferences.pop(user_id, None)