import parasite
import sys

if __name__ == "__main__":
    parasite = Parasite()
    bot = parasite.Parasite()

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