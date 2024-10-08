class RANKING:
    HEADERS: str = "//table//thead//tr//th//*[self::div or self::abbr][1]//text()[normalize-space()][1]"
    ROWS: str = "//tbody[contains(@class, 'isPL')]//tr//td[position() > 1 and position() <= 10]//text()"
    CUP_WINNER: str = "//table[contains(@class, 'infobox vcard')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    UEFA_WINNER: str = "//table[contains(@class, 'infobox vcalendar')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
