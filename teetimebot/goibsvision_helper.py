from bs4 import BeautifulSoup


@staticmethod
def parse_goibsvision_html(html_content):
    parsed_result = []

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    table_elements = soup.find_all("table")

    for table in table_elements:
        title = table.find("td", class_="title").get_text(strip=True)
        time = table.find("td", class_="time").get_text(strip=True)
        players = table.find("input", {"name": "NumberOfPlayers"}).get("value")
        slot_id = table.find("input", {"name": "SlotID"}).get("value")
        price = table.find("div", class_="price").get_text(strip=True)
        parsed_result.append(
            {
                "title": title,
                "time": time,
                "players": players,
                "slot_id": slot_id,
                "price": price,
            }
        )
    return parsed_result
