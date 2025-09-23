from . import strategy_enum, base_struct, base_strategy
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import BSP_TYPE
from BuySellPoint import BS_Point
from Plot.PlotDriver import CPlotDriver
from typing import Optional
import datetime
from pathlib import Path


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
            "plot_macd": True,
            "plot_mean": False,
            "plot_channel": False,
            "plot_bsp": True,
            "plot_extrainfo": False,
            "plot_demark": False,
            "plot_marker": False,
            "plot_rsi": False,
            "plot_kdj": False,
            "plot_segzs": True,
            "plot_segbsp": True
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
        # week_chan = CChan(
        #     code=s.market + "." + s.code,
        #     begin_time=strategy_context.start,
        #     end_time=strategy_context.end,
        #     data_src=data_src,
        #     lv_list=[KL_TYPE.K_WEEK],
        #     config=config,
        #     autype=AUTYPE.QFQ,
        # )

        point = 0
        reasons = []
        point, reasons = self.handle_chan_result(chan)
        # w_point, w_reasons = self.handle_chan_result(week_chan)
        if point > 0:
            label_dir = self.get_date_label()
            yyyymm = label_dir[:6]
            folder_path = Path(f"./TempDir/{yyyymm}")

            # 创建目录
            folder_path.mkdir(parents=True, exist_ok=True)

            file_path = folder_path / label_dir / f"{s.name}_{s.code}.png"
            reason_label = ",".join(reasons)
            if not file_path.exists() and "二" in reason_label:
                plot_driver = CPlotDriver(
                    chan,
                    plot_config=plot_config,
                    plot_para=plot_para,
                )
                plot_driver.save2img(file_path)
            return base_struct.ChooseEntity(s, reasons, point)

        return None

    def handle_chan_result(self, chan: CChan):
        datas = chan.kl_datas
        day_cklist = datas[chan.lv_list[0]]
        if day_cklist and day_cklist.bs_point_lst:
            point = 0
            reasons = []

            format_str = "%Y-%m-%d"
            end = datetime.datetime.strptime(
                self.end, format_str
            )

            for _, v in enumerate(day_cklist.bs_point_lst.bsp1_list):
                if not v.is_buy:
                    continue
                interval = end - v.klu.time.to_datetime()
                if interval.days > 3:
                    continue

                _reasons: list[str] = []
                _point = 0
                for vt in v.type:
                    if vt == BSP_TYPE.T1:
                        reason = "一买"
                        _point += 10
                        _reasons.append(reason)
                    if vt == BSP_TYPE.T2:
                        reason = "二买"
                        _point += 100
                        _reasons.append(reason)
                    if vt == BSP_TYPE.T1P:
                        reason = "类一买"
                        _point += 10
                        _reasons.append(reason)
                    if vt == BSP_TYPE.T2S:
                        reason = "类二买"
                        _point += 90
                        _reasons.append(reason)
                    if vt == BSP_TYPE.T3B:
                        reason = "三买"
                        _point += 50
                        _reasons.append(reason)

                if _point > 0:
                    point += _point
                    reasons.extend(_reasons)
                    return point, reasons
        return 0, []

    # def try_open(self, chan: CChan, lv) -> Optional[CCustomBSP]:
    #     data = chan[lv]
    #     if lv != len(chan.lv_list)-1 and data.bi_list:  # 当前级别不是最低级别，且至少有一笔
    #         if qjt_bsp := self.cal_qjt_bsp(data, chan[lv + 1]):  # 计算区间套
    #             return qjt_bsp

    # def cal_qjt_bsp(self, data: CKLine_List, sub_lv_data: CKLine_List) -> Optional[CCustomBSP]:
    #     last_klu = data[-1][-1]
    #     last_bsp_lst = data.bs_point_lst.getLastestBspList()
    #     if len(last_bsp_lst) == 0:
    #         return None
    #     last_bsp = last_bsp_lst[0]
    #     if last_bsp.klu.idx != last_klu.idx:  # 当前K线是父级别的买卖点
    #         return None
    #     for sub_bsp in sub_lv_data.cbsp_strategy:  # 对于次级别的买卖点
    #         if sub_bsp.klu.sup_kl.idx == last_klu.idx and \  # 如果是父级别K线下的次级别K线
    #         sub_bsp.type2str().find("1") >= 0:  # 且是一类买卖点
    #         return CCustomBSP(
    #                 bsp=last_bsp,
    #                 klu=last_klu,
    #                 bs_type=last_bsp.qjt_type(),  # 返回区间套买卖点
    #                 is_buy=last_bsp.is_buy,
    #                 target_klc=sub_bsp.target_klc[-1].sup_kl.klc,
    #                 price=sub_bsp.open_price,
    #             )
    #     return None
