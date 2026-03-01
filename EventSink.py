class EventSink:
    """
    Minimal event sink.
    LevelLogic or ObjectiveManager can own one.
    """

    def on_event(self, event):
        pass