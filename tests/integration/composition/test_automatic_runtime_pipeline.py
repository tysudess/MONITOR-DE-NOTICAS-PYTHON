from __future__ import annotations

from datetime import datetime
import time
from pathlib import Path

from monitor_noticias.app.paths import AppPaths
from monitor_noticias.app.preferences import SharedPreferences
from monitor_noticias.app.runtime_runners import RuntimeNewsRunner
from monitor_noticias.automation import AutomationService, AutomationSettings
from monitor_noticias.database import NewsDb
from monitor_noticias.models import News
from monitor_noticias.repositories import NewsRepository

class FakeClock:
    def __init__(self,now): self.value=now
    def now_ms(self): return self.value
    def local_datetime(self): return datetime.fromtimestamp(self.value/1000)
class FakeGoogle:
    def collect(self,query):
        now=int(time.time()*1000)
        return [News(title="Marinha em operação",source="Fonte",date=now,link="https://example.test/auto",snippet="Marinha",capturedAt=now)]
class FakeLatest: pass
class NoVideo:
    def search_videos(self,**kwargs): raise AssertionError

def test_automatic_tick_uses_real_runtime_runner_repository_and_database(tmp_path: Path):
    paths=AppPaths(tmp_path); paths.ensure_runtime_dirs(); prefs=SharedPreferences(paths.data/"prefs"/"monitor_prefs.properties")
    db=NewsDb(paths.news_db)
    for term in db.listTerms(): db.removeTerm(term)
    db.addTerm("MARINHA")
    prefs.update(desktop_automatic_monitoring=True,desktop_news_automatic=True,desktop_demand_automatic=False,desktop_video_automatic=False,desktop_auto_news_at=0)
    repository=NewsRepository(db,google=FakeGoogle(),latest=FakeLatest(),national_sources=())
    runner=RuntimeNewsRunner(repository,prefs,())
    now=int(time.time()*1000); service=AutomationService(AutomationSettings(prefs),runner,NoVideo(),clock=FakeClock(now))
    service.tick()
    deadline=time.time()+5
    while service.state.newsBusy and time.time()<deadline: time.sleep(0.01)
    assert not service.state.newsBusy
    assert db.listNews(10)[0].link=="https://example.test/auto"
    assert service.settings.last_news_auto_at==now
    service.close(); db.close()
