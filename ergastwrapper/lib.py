__author__ = "PierreV23 https://github.com/PierreV23"
__copyright__ = "Copyright (C) 2022 Pièrre (A.P.) V"
__license__ = "GNU General Public License v3.0"
__author__forked__ = "" # NOTE: Put your version of `__author__` in here.



import requests
from enum import Enum
import datetime as dt
from .cache import cache



def to_datetime(date, time):
    year, month, day = map(lambda x: int(x), date.split("-"))
    hour, minute, second = map(lambda x: int(x), time[:-1].split(":"))
    return dt.datetime(
            year = year,
            month = month,
            day = day,
            hour = hour,
            minute = minute,
            second = second,
            tzinfo = dt.timezone.utc
        )



class Series(Enum):
    Formula1 = 'f1'
    Formula2 = 'f2' # NOTE: Ergast does not yet support other series besides F1, thus can this be seen as redundant.
    Formula3 = 'f3' # NOTE: Ergast does not yet support other series besides F1, thus can this be seen as redundant.



class SessionType(Enum):
    FirstPractice = 'fp1'
    SecondPractice = 'fp2'
    ThirdPractice = 'fp3'
    Qualifying = 'q'
    Q1 = 'q1'
    Q2 = 'q2'
    Q3 = 'q3'
    Race = 'race'
    Sprint = 'sprint'



class Circuit:
    __circuits = {}

    def __new__(cls, name, *args, **kwargs): # TODO: I once added this, is this even necessary?
        if name in cls.__circuits:
            return cls.__circuits[name]
        new = super().__new__(cls)
        cls.__circuits[name] = new
        return new
    

    def __init__(self,
        name: str,
        country: str,
        circuitid: str,
        locality: str
    ):
        self.name = name
        self.country = country
        self.circuitid = circuitid
        self.locality = locality



class Session:
    __sessions = {}

    def __new__(cls, series, year, round, session_type, *args, **kwargs): # TODO: I once added this, is this even necessary?
        if (series, year, round, session_type.name) in cls.__sessions:
            return cls.__sessions[(series, year, round, session_type.name)]
        new = super().__new__(cls)
        cls.__sessions[(series, year, round, session_type.name)] = new
        return new


    def __init__(
        self,
        series: Series,
        year: int,
        round: int,
        session_type: SessionType,
        datetime: dt.datetime,
        circuit: Circuit
    ):
        self.series = series
        self.year = year
        self.round = round
        self.session_type = session_type
        self.name = session_type.name if session_type.value in 'racesprintq' else session_type.value.upper() #   <- alternatives \/
        # self.name = self.session_type.name #                                                                  <- alternatives /\
        self.datetime = datetime
        self.circuit = circuit



class Weekend:
    def __init__(
        self,
        FirstPractice: Session,
        SecondPractice: Session,
        ThirdPractice: Session,
        Qualifying: Session,
        Q1: Session,
        Q2: Session,
        Q3: Session,
        Sprint: Session,
        Race: Session,
        circuit: Circuit
    ):
        self.FirstPractice = FirstPractice
        self.SecondPractice = SecondPractice
        self._ThirdPractice = ThirdPractice
        self.Qualifying = Qualifying
        self.Q1 = Q1
        self.Q2 = Q2
        self.Q3 = Q3
        self.Race = Race
        self._Sprint = Sprint
        self.sessions = {
            self.FirstPractice,
            self.SecondPractice,
            self.ThirdPractice,
            self.Qualifying,
            self.Q1,
            self.Q2,
            self.Q3,
            self.Race,
            self.Sprint,
        } # NOTE: `self.` is in front of each SessionType so the getters (ThirdPractice and Sprint) are called.
        self.circuit = circuit
    

    def is_sprint_weekend(self):
        return True if self.Sprint else False
    

    @property
    def ThirdPractice(self):
        if self._ThirdPractice == None:
            if self.Sprint == None: # NOTE: This exists purely incase a weekend is bugged.
                return self.SecondPractice
            else:
                return self.Sprint
        else:
            return self._ThirdPractice
    

    @property
    def Sprint(self):
        if self._Sprint == None:
            if self._ThirdPractice == None: # NOTE: This exists purely incase a weekend is bugged.
                return self.Race
            else:
                return self._ThirdPractice
        else:
            return self._Sprint
    

    def get_session(self, sess: SessionType):
        if sess == SessionType.FirstPractice: return self.FirstPractice
        elif sess == SessionType.SecondPractice: return self.SecondPractice
        elif sess == SessionType.ThirdPractice: return self.ThirdPractice
        elif sess == SessionType.Qualifying: return self.Qualifying
        elif sess == SessionType.Q1: return self.Q1
        elif sess == SessionType.Q2: return self.Q2
        elif sess == SessionType.Q3: return self.Q3
        elif sess == SessionType.Race: return self.Race
        elif sess == SessionType.Sprint: return self.Sprint



def get_weekend(year, round, series = Series.Formula1) -> Weekend:
    data = cache.load_from_cache(series.value, year, round)
    if data == False:
        data = requests.get(f'http://ergast.com/api/{series.value}/{year}/{round}.json').json()["MRData"]["RaceTable"]["Races"][0]
        cache.save_cache(series.value, year, round, data)
    dt_FirstPractice = to_datetime(**data["FirstPractice"])
    dt_SecondPractice = to_datetime(**data["SecondPractice"])
    
    dt_Qualifying = to_datetime(**data["Qualifying"])
    dt_Race = to_datetime(**{"date": data["date"], "time": data["time"]})

    circuit = data["Circuit"]
    circuit = Circuit(
        name = circuit["circuitName"],
        country = circuit["Location"]["country"],
        circuitid = circuit["circuitId"],
        locality = circuit["Location"]["locality"]
    )

    FirstPractice = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.FirstPractice,
        datetime = dt_FirstPractice,
        circuit = circuit
    )
    SecondPractice = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.SecondPractice,
        datetime = dt_SecondPractice,
        circuit = circuit
    )
    Qualifying = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.Qualifying,
        datetime = dt_Qualifying,
        circuit = circuit
    )
    Q1 = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.Q1,
        datetime = dt_Qualifying,
        circuit = circuit
    )
    Q2 = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.Q2,
        datetime = dt_Qualifying + dt.timedelta(minutes = 25), # TODO: Not sure its the right timedelta.
        circuit = circuit
    )
    Q3 = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.Q3,
        datetime = dt_Qualifying + dt.timedelta(minutes = 48), # TODO: I think this one is incorrect, will have to check later.
        circuit = circuit
    )
    Race = Session(
        series = series,
        year = year,
        round = round,
        session_type = SessionType.Race,
        datetime = dt_Race,
        circuit = circuit
    )

    if "ThirdPractice" in data:
        dt_ThirdPractice = to_datetime(**data["ThirdPractice"])
        ThirdPractice = Session(
            series = series,
            year = year,
            round = round,
            session_type = SessionType.ThirdPractice,
            datetime = dt_ThirdPractice,
            circuit = circuit
        )
    else:
        ThirdPractice = None
    
    if "Sprint" in data:
        Sprint = to_datetime(**data["Sprint"])
        Sprint = Session(
            series = series,
            year = year,
            round = round,
            session_type = SessionType.Sprint,
            datetime = Sprint,
            circuit = circuit
        )
    else:
        Sprint = None

    weekend = Weekend(
        FirstPractice = FirstPractice,
        SecondPractice = SecondPractice,
        ThirdPractice = ThirdPractice,
        Qualifying = Qualifying,
        Q1 = Q1,
        Q2 = Q2,
        Q3 = Q3,
        Race = Race,
        Sprint = Sprint,
        circuit = circuit,
    )

    return weekend




#wknd = get_weekend(2022, 4, Series.Formula1)

#print(wknd.FirstPractice.datetime.timestamp())

#sess = wknd.get_session(SessionType.ThirdPractice)
#sess_dt = sess.datetime
#print(sess_dt, sess_dt.timestamp(), sess.session_type)
#var = requests.get('http://ergast.com/api/f1/2022/1.json').json()
#print(json.dumps(var, indent=4, sort_keys=True))
# %%

# %%
