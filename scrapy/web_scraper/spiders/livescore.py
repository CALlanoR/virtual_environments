import scrapy

class LiveScore(scrapy.Spider):
    name = "LiveScore"

    start_urls = [
        "https://www.livescore.cz/yesterday.php"
    ]

    def parse(self, response):
        # Basically, we extracted all the HTML <tr></tr> elements from the page.
        # Then, we looped through them to find out whether each is a tournament or a match.
        # If it’s a tournament, we extracted its name. 
        # In the case of a match, we extracted its time, state, and name and score of both teams.


        table_tr = response.css('tr')

        tournaments = []

        for tr in table_tr:
          if tr.css('.tournament'):
            tournaments.append({
                    'name': tr.css('.nation a::text').get(),
                    'matches': []
                })
          elif tr.css('.match'):
            team_score = tr.css('.col-score strong::text').get()

            if team_score is not None:
                team_1_score = team_score.split(':')[0]
                team_2_score = team_score.split(':')[1]
            else:
                team_1_score = None
                team_2_score = None

            tournaments[-1]['matches'].append({
                'time': tr.css('.match .col-time time::attr(datetime)').get(),
                'state': tr.css('.match .col-state span::text').get(),
                'team_1_name': tr.css('.col-home a::text').get(),
                'team_1_score': team_1_score,
                'team_2_name': tr.css('.col-guest a::text').get(),
                'team_2_score': team_2_score
            })

        for t in tournaments:
            yield {
                'tournament': t
            }