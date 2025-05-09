from typing import Optional


class RANKING:
    CURRENT_RANKING: str = "//table[.//tr[1]/*[1][contains(normalize-space(), 'Pos')]]//tr//text()[normalize-space()]"
    CUP_WINNER: str = "//table[contains(@class, 'infobox vcard')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    UEFA_WINNER: str = "//table[contains(@class, 'infobox vcalendar')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    TEAMS: str = "//table[.//tr[1]/*[1][contains(normalize-space(), 'Pos')]]//tr[position() > 1]/th[1]//text()[normalize-space()]"


class PLAYERS:
    PLAYER_STATS: str = "//div[@class='data']//table//tr//td//text()"
    TRANSFER_TABLES: str = '//div[@class="box"]'
    TRANSFER_HEADER: str = './/div[@class="head"]/h2/text()'
    TRANSFER_DATA: str = './/div[@class="data"]//table//tr//text()'


class MATCHES:
    @staticmethod
    def match_report_url(match_week: Optional[int] = 1) -> str:
        return f"//td[@data-stat='match_report'][not(../td[@data-stat='notes'][contains(text(), 'Match Cancelled') or contains(text(), 'Match awarded')])][../th[@data-stat='gameweek' and number(text()) >= number({match_week})]]/a[text()='Match Report']/@href"

    NEXT_MATCH_ROW: str = (
        f"//td[@data-stat='match_report']/a[text()='Head-to-Head']/@href"
    )
    A_TAG: str = "'.//a//text()'"
    GAME_TABLE: str = "//table"
    GAME_HEADER: str = '//div[contains(text(), "Matchweek")]//text()'
    GAME_STATS: str = '//div[@class="scorebox"]/div'
    GAME_VENUE_DATE: str = "./span//@data-venue-date"
    GAME_VENUE_TIME: str = "./span//@data-venue-time"
    GAME_GOALS: str = './/div[@class="score"]//text()'
