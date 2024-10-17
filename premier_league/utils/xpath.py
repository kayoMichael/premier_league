class RANKING:
    CURRENT_RANKING: str = "//div[.//h2[contains(text(), 'League table')]]/following-sibling::table[1]//text()"
    CUP_WINNER: str = "//table[contains(@class, 'infobox vcard')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
    UEFA_WINNER: str = "//table[contains(@class, 'infobox vcalendar')]//tbody//tr[.//th[contains(text(), 'Champions')]]//td//text()"
