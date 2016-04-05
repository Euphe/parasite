import parasite
import sys
import os
if __name__ == "__main__":
    bot = parasite.Parasite()
    bot.collection_time = ("01", "00")
    bot.schedule = [
            ("8:00", "new"),
            ("8:30", "new"),
            ("9:00", "new"),
            ("9:30", "new"),
            ("10:30", "new"),
            ("11:00", "new"),

            #ads

            ("12:30", "new"),
            ("13:00", "new"),

            #ads 

            ("15:00", "new"),
            ("16:00", "new"),
            ("17:00", "new"),
            ("18:00", "new"),
            ("19:00", "new"),

            #ads

            ("21:00", "new"),
            ("21:30", "new"),
            ("22:00", "new"),
            ("22:30", "new"),
            ("23:00", "new"),
            ("23:30", "new"),
        ]

    bot.targets = [
                {
                    "subreddit": "aww",
                    "category": "hot",
                    "post_rules": {
                        "minimal score": 100, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 19
                },
                {
                    "subreddit": "aww",
                    "category": "new",
                    "post_rules": {
                        "minimal score": 1, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 10
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
    abs_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    bot.vk_group_id = "118675037"
    bot.pics_path = abs_path+'/pics/'
    bot.log_path = abs_path+'/logs/'
    bot.start(sys.argv[1:])