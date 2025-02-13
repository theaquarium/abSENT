from datetime import datetime, timedelta, timezone
import yaml
from dataStructs import *
from driver.notifications import *
from database.logger import Logger


class SchoologyListener:
    def __init__(self, textnowCreds, scCreds):
        self.north = SchoolName.NEWTON_NORTH
        self.south = SchoolName.NEWTON_SOUTH
        self.notifications = NotificationDriver(textnowCreds, scCreds)
        # self.restTime = timedelta(seconds=10)

        # Logging:
        self.logger = Logger()

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        sentNorth = False
        sentSouth = False

        if sentNorth == False or sentSouth == False:
            # Convert from UTC --> EST
            date = datetime.now(timezone.utc) - timedelta(hours=5)
            states = self.fetchStates(date)
            # Reads from state file to determine whether notifications have been sent today.
            if not states[self.north] or not states[self.south]:
                # NNHS Runtime.
                if not states[self.north]:
                    # Sends notifications, checks sucess.
                    update = self.notifications.run(date, self.north)
                    if update:
                        # Update statefile and var.
                        self.writeState(self.north, date)
                        sentNorth = True
                        self.logger.sentAbsencesSuccess(
                            SchoolName.NEWTON_NORTH)
                # NSHS Runtime
                if not states[self.south]:
                    # Sends notifications, check sucess.
                    update = self.notifications.run(date, self.south)
                    if update:
                        # Update statefile and var.
                        self.writeState(self.south, date)
                        sentSouth = True
                        self.logger.sentAbsencesSuccess(
                            SchoolName.NEWTON_SOUTH)
                states = self.fetchStates(date)
            else:
                print("USERS ALREADY NOTIFIED.")
                return True
        return sentNorth and sentSouth

    # Function for fetching an up to date state file content.
    def fetchStates(self, date, statePath='state.yml'):
        stateDict = {
            SchoolName.NEWTON_NORTH: False,
            SchoolName.NEWTON_SOUTH: False
        }
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        if state[str(SchoolName.NEWTON_NORTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_NORTH] = True
        if state[str(SchoolName.NEWTON_SOUTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_SOUTH] = True
        return stateDict

    # Function for writing state.
    def writeState(self, school: SchoolName, date, statePath='state.yml'):
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        state[str(school)] = date.strftime('%m/%-d/%Y')
        if school == SchoolName.NEWTON_NORTH:
            state[str(SchoolName.NEWTON_SOUTH)
                  ] = state[str(SchoolName.NEWTON_SOUTH)]
        else:
            state[str(SchoolName.NEWTON_NORTH)
                  ] = state[str(SchoolName.NEWTON_NORTH)]
        # Write new state to state file
        with open('state.yml', 'w') as f:
            yaml.safe_dump(state, f)
        return state
