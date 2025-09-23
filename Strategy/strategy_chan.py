from . import strategy_enum, base_struct, base_strategy
from Orm import kline_repository
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Chan import CChan
from ChanConfig import CChanConfig


class ChanStrategy(base_strategy.BaseDailyStrategy):

    def strategy_enum(self):
        return strategy_enum.StrategyEnum.CHAN

    def stock_filter(self, s: base_struct.Stock,
                     strategy_context: base_struct.StrategyContext):

        data_src = DATA_SRC.HIKYUU_MYSQL
        lv_list = [KL_TYPE.K_DAY]

        config = CChanConfig({
            "bi_strict": True,
            "trigger_step": False,
            "skip_step": 0,
            "divergence_rate": float("inf"),
            "bsp2_follow_1": False,
            "bsp3_follow_1": False,
            "min_zs_cnt": 0,
            "bs1_peak": False,
            "macd_algo": "peak",
            "bs_type": '1,2,3a,1p,2s,3b',
            "print_warning": True,
            "zs_algo": "normal",
        })

        plot_config = {
            "plot_kline": True,
            "plot_kline_combine": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_eigen": False,
            "plot_zs": True,
            "plot_macd": False,
            "plot_mean": False,
            "plot_channel": False,
            "plot_bsp": True,
            "plot_extrainfo": False,
            "plot_demark": False,
            "plot_marker": False,
            "plot_rsi": False,
            "plot_kdj": False,
        }

        plot_para = {
            "seg": {
                # "plot_trendline": True,
            },
            "bi": {
                # "show_num": True,
                # "disp_end": True,
            },
            "figure": {
                "x_range": 200,
            },
            "marker": {
                # "markers": {  # text, position, color
                #     '2023/06/01': ('marker here', 'up', 'red'),
                #     '2023/06/08': ('marker here', 'down')
                # },
            }
        }
        chan = CChan(
            code=s.market + "." + s.code,
            begin_time=strategy_context.start,
            end_time=strategy_context.end,
            data_src=data_src,
            lv_list=lv_list,
            config=config,
            autype=AUTYPE.QFQ,
        )
        datas = chan.kl_datas
        day_cklist = datas[KL_TYPE.K_DAY]
        if day_cklist:
            if day_cklist.bs_point_lst:
                pass
            pass
        return None
