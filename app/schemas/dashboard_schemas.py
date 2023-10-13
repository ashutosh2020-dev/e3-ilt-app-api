from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime



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
        self.id=0
        self.name = ""
        self.numOfEndMeeting = 0
        self.numOfNotStartedMeeting = 0
        self.numOfInprogressMeeting = 0 
        self.numOfMembers = 0
        self.attendancePercentage = PercentageData()
        self.rockOnTrack = PercentageData()
        self.avgRatings = PercentageData()
        self.avgtoDo = PercentageData()
        self.issues = IssuesData()

class DashboardFilterParamaters(BaseModel):
    schoolId : Optional[List[int]] =[]
    distictId : Optional[List[int]] =[]
    districtAggregateFlag: bool=False
    startDate:datetime = datetime(datetime.now().year,8,1)
    endDate:datetime = datetime(datetime.now().year+1,6,30)