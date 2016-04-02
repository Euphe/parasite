import parasite
import sys

if __name__ == "__main__":
    parasite = Parasite()
    bot = parasite.Parasite()

    bot.schedule = [
            ("8:30", "new"),
            ("9:00", "new"),
            ("10:30", "new"),
            
            ("12:15", "new"),
            ("13:30", "new"),
            ("14:45", "new"),

            ("16:00", "new"),
            ("17:00", "new"),
            ("18:00", "new"),
            ("19:00", "new"),

            ("21:35", "new"),
            ("22:05", "new"),
            ("23:00", "new"),
        ]

    bot.targets = [
                {
                    "subreddit": "aww",
                    "category": "hot",
                    "post_rules": {
                        "minimal score": 100, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 15
                },
                {
                    "subreddit": "aww",
                    "category": "new",
                    "post_rules": {
                        "minimal score": 1, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 15
                },
                {
                    "subreddit": "cute",
                    "category": "hot",
                    "post_rules": {
                        "minimal score": 10, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 5
                },
    ]
    bot.prefix = "zverota"
    bot.start(sys.argv[1:])