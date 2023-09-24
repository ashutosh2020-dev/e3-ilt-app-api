class PercentageData:
    def __init__(self, percentage=0, total=0):
        self.percentage = percentage
        self.total = total

class IssuesData:
    def __init__(self):
        self.recognizePerformance = PercentageData()
        self.teacherSupport = PercentageData()
        self.leaderSupport = PercentageData()
        self.advanceEquality = PercentageData()
        self.othersFlag = PercentageData()
        self.avgIssueRepeat = PercentageData()

class SummaryData:
    def __init__(self):
        self.schoolName = ""
        self.numOfEndMeeting = 0
        self.numOfNotStartedMeeting = 0
        self.numOfInprogressMeeting = 0 
        self.numOfMembers = 0
        self.attendancePercentage = PercentageData()
        self.rockOnTrack = PercentageData()
        self.avgRatings = PercentageData()
        self.avgtoDo = PercentageData()
        self.issues = IssuesData()