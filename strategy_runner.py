from Strategy import strategy_chan

if __name__ == "__main__":

    strategy = strategy_chan.ChanStrategy("2025-03-01", "2025-08-08")
    strategy.do_execute()
