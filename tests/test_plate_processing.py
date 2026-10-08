from anpr.plate_processor import vote_plate
from anpr.plate_validator import normalize_plate
def test_normalize(): assert normalize_plate('tn 38-ab 1234')=='TN38AB1234'
def test_vote(): assert vote_plate([('TN38 AB1234',.9),('TN38AB1234',.8)])[0]=='TN38AB1234'
