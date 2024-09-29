class RANKING:
    HEADERS: str = "//table//thead//tr//th//*[self::div or self::abbr][1]//text()[normalize-space()][1]"
    ROWS: str = "//tbody[contains(@class, 'isPL')]//tr//td[position() > 1 and position() <= 10]//text()"
