class RANKING:
    CURRENT_RANKING: str = (
        "//div[.//h2[contains(text(), 'League table')]]/following-sibling::table[1]//text()"
    )
    CUP_WINNER: str = (
        "//table[contains(@class, 'infobox vcard')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    )
    UEFA_WINNER: str = (
        "//table[contains(@class, 'infobox vcalendar')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    )


class PLAYERS:
    PLAYER_STATS: str = "//table//tr//td//text()"
    TRANSFER_TABLES: str = '//div[@class="box"]'
    TRANSFER_HEADER: str = './/div[@class="head"]/h2/text()'
    TRANSFER_DATA: str = './/div[@class="data"]//table//tr//text()'


class MATCHES:
    MATCH_REPORT_URL: str = (
        "//td[@data-stat='match_report'][not(../td[@data-stat='notes'][contains(text(), 'Match Cancelled')])]/a[text()='Match Report']/@href"
    )
    GAME_TABLE: str = "//table"
