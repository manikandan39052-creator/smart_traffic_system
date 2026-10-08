from datetime import datetime,timedelta
from violations.no_parking import NoParkingRule
def test_no_parking_lifecycle():
 r=NoParkingRule(10,5); start=datetime.now(); assert r.update((1,'NP'),True,start) is None; assert r.update((1,'NP'),True,start+timedelta(seconds=10))=='warning'; assert r.update((1,'NP'),True,start+timedelta(seconds=15))=='confirmed'; assert r.update((1,'NP'),True,start+timedelta(seconds=16)) is None
