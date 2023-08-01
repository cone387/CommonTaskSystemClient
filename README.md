# CommonTaskSystemClient



## callback的运行是放在Schedule中还是Executor中
1. 如果放在Schedule中，那么多线程模式运行的适合就不好处理callback
2. 如果放在Executor中，如果没有找到对应的Executor，那么也运行不了callback， 但其实是想上传日志的。