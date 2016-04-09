import parasite
import sys
import os
if __name__ == "__main__":
    bot = parasite.Parasite()
    bot.collection_time = ("02", "00")
    bot.schedule = [
            ("8:00", "new"),
            ("9:00", "new"),
            ("10:00", "new"),
            ("11:00", "new"),

            #ads

            ("13:00", "new"),

            #ads 

            ("15:00", "new"),
            ("16:00", "new"),
            ("18:00", "new"),
            ("19:00", "new"),

            #ads

            ("21:00", "new"),
            ("21:30", "new"),
            ("22:00", "new"),
            ("23:00", "new"),
            ("23:30", "new"),
            ("00:00", "new"),
            ("00:15", "new"),
            ("00:30", "new"),
            ("00:45", "new"),
            ("01:00", "new"),
            ("01:15", "new"),
            ("01:30", "new"),
            ("01:45", "new"),
        ]

    bot.targets = [
                {
                    "subreddit": "RealGirls",
                    "category": "hot",
                    "post_rules": {
                        "minimal score": 350, #int
                        "over 18": True, #False, True, "Any"
                    },
                    "target_amount": 30
                },
                {
                    "subreddit": "RealGirls",
                    "category": "new",
                    "post_rules": {
                        "minimal score": 300, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 10
                },
                {
                    "subreddit": "realasians",
                    "category": "hot",
                    "post_rules": {
                        "minimal score": 150, #int
                        "over 18": False, #False, True, "Any"
                    },
                    "target_amount": 20
                },

    ]
    bot.prefix = "ero"
    abs_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    bot.vk_group_id = "118861016"
    bot.pics_path = abs_path+'/pics/'
    bot.log_path = abs_path+'/logs/'
    bot.start(sys.argv[1:])
