import os
import time
import matplotlib.pyplot as plt
import pandas as pd
from tqdm.auto import tqdm

from .pacs_load_tester import *

from autoscaler.monitor import *
from autoscaler.controller import *


d_monitor = DeploymentsMonitor()
p_monitor = PodsMonitor()


def _prefix_dict(prefix, dict):
    return {prefix+'_'+k: v for k,v in dict.items()}


def _custom_sensing():
    result = {}
    result.update(
        _prefix_dict('cpu', d_monitor.get_deployments_total_cpu_usage())
    )
    result.update(
        _prefix_dict('monitored_count', d_monitor.get_all_deployments_pod_count())
    )
    result.update(
        _prefix_dict('kubernetes', d_monitor.get_all_deployment_kubernetes_count())
    )
    return result


def start():
    stop_test()
    time.sleep(5)

    HorizontalScaler()._default_replicas()
    time.sleep(5)

    tqdm.pandas()

    loop_timer = TimerClass()
    total_timer = TimerClass()

    user_sequence = [50, 100, 500, 800, 800, 400, 100, 50, 50]

    lt = PACSLoadTester(hatch_rate=1000, temp_stat_max_len=60)
    # add the custom sensing function
    lt.custom_sensing = _custom_sensing
    lt.change_count(user_sequence[0])
    lt.reset_remote_stats()
    # wait for changes to take effect
    time.sleep(10)
    lt.start_capturing()

    loop_time_in_secs = get_loop_time_in_secs('60s')

    loop_timer.tic()
    total_timer.tic()

    arr_results = []
    for i in tqdm(range(len(user_sequence))):
        user_count = user_sequence[i]
        lt.change_count(user_count)
        
        time.sleep(loop_time_in_secs - loop_timer.toc())
        
        loop_timer.tic()
        
        result = lt.get_all_stats()    
        arr_results.append(result)
        
    lt.stop_test()

    # parse the results
    if not os.path.exists('results'):
        os.makedirs('results')

    results = None
    for result in arr_results:
        df_result = pd.DataFrame(data=result)
        
        if results is None:
            results = df_result
        else:
            results = results.append(df_result)

    results, filename = lt.prepare_results_from_df(results)

    filename = filename[:-4]

    res = results

    plt.figure(figsize=(8,18))
    plt.subplot(411)

    plt.plot(res['elapsed_min'], res['current_response_time_average'], label='avg_response_time')
    plt.plot(res['elapsed_min'], res['current_response_time_percentile_95'], label='95th percentile')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Average Response Time (ms)')
    plt.legend()

    plt.subplot(412)
    plt.plot(res['elapsed_min'], res['user_count'])
    plt.xlabel('Time (minutes)')
    plt.ylabel('Num of Users')

    plt.subplot(413)
    plt.plot(res['elapsed_min'], res['total_rps'])
    plt.xlabel('Time (minutes)')
    plt.ylabel('Throughput (req/s)')

    plt.subplot(414)
    plt.plot(res['elapsed_min'], res['current_fail_per_sec'])
    plt.xlabel('Time (minutes)')
    plt.ylabel('Fail Per Second')
    plt.savefig(filename)