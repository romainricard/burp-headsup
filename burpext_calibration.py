import sys
import time
from burp import IBurpExtender


class BurpExtender(IBurpExtender):

    def registerExtenderCallbacks(self, callbacks):
        
        def pprogress(text):
            sys.stdout.write(text)
            sys.stdout.flush()

        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Burp head-up calibration tool")

        change_state_durations = []
        same_state_durations = []

        # Initial state
        callbacks.setProxyInterceptionEnabled(False)
        pprogress("Getting data...")
        for i in range(100):

            # Disabled to enabled
            start_time = time.time()
            callbacks.setProxyInterceptionEnabled(True)
            stop_time = time.time()
            change_state_durations.append((stop_time - start_time))

            # Enabled to enabled
            start_time = time.time()
            callbacks.setProxyInterceptionEnabled(True)
            stop_time = time.time()
            same_state_durations.append((stop_time - start_time))

            # Enabled to disabled
            start_time = time.time()
            callbacks.setProxyInterceptionEnabled(False)
            stop_time = time.time()
            change_state_durations.append((stop_time - start_time))

            # Disabled to disabled
            start_time = time.time()
            callbacks.setProxyInterceptionEnabled(False)
            stop_time = time.time()
            same_state_durations.append((stop_time - start_time))

            pprogress(".")

        print("\n\n### Changing state durations ###")
        #print(change_state_durations)
        print("")
        print("Average: {}s\tMin: {}s\tMax: {}s".format(
            sum(change_state_durations) / len(change_state_durations) , min(change_state_durations), max(change_state_durations)
        ))

        print("\n\n### Same state durations ###")
        #print(same_state_durations)
        print("")
        print("Average: {}s\tMin: {}s\tMax: {}s".format(
            sum(same_state_durations) / len(same_state_durations) , min(same_state_durations), max(same_state_durations)
        ))
