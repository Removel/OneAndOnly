import time
import threading


class SnowflakeIdGenerator:
    """
    雪花算法ID生成器
    生成64位的唯一ID，结构如下：
    - 1位：符号位（始终为0）
    - 41位：时间戳（毫秒级）
    - 10位：机器ID（5位数据中心ID + 5位工作机器ID）
    - 12位：序列号
    
    支持单机每毫秒生成4096个ID
    """
    
    def __init__(self, datacenter_id: int = 0, worker_id: int = 0):
        """
        初始化雪花算法生成器
        :param datacenter_id: 数据中心ID (0-31)
        :param worker_id: 工作机器ID (0-31)
        """
        if datacenter_id < 0 or datacenter_id > 31:
            raise ValueError("数据中心ID必须在0-31之间")
        if worker_id < 0 or worker_id > 31:
            raise ValueError("工作机器ID必须在0-31之间")
        
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        
        # 时间戳起始点（2024-01-01 00:00:00）
        self.epoch = 1704067200000
        
        # 序列号
        self.sequence = 0
        
        # 上次生成ID的时间戳
        self.last_timestamp = -1
        
        # 线程锁
        self.lock = threading.Lock()
    
    def _current_millis(self) -> int:
        """
        获取当前时间戳（毫秒）
        :return: 当前时间戳
        """
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        """
        等待下一毫秒
        :param last_timestamp: 上次生成ID的时间戳
        :return: 新的时间戳
        """
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp
    
    def generate_id(self) -> int:
        """
        生成雪花算法ID
        :return: 唯一ID
        """
        with self.lock:
            timestamp = self._current_millis()
            
            # 时钟回拨检查
            if timestamp < self.last_timestamp:
                raise RuntimeError(f"时钟回拨检测，拒绝生成ID。当前时间戳：{timestamp}，上次时间戳：{self.last_timestamp}")
            
            # 同一毫秒内，序列号递增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 序列号最大4095
                if self.sequence == 0:
                    # 序列号溢出，等待下一毫秒
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # 新的毫秒，序列号重置
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            # 组装ID
            id = ((timestamp - self.epoch) << 22) | \
                 (self.datacenter_id << 17) | \
                 (self.worker_id << 12) | \
                 self.sequence
            
            return id


# 全局雪花算法生成器实例（单机部署，数据中心ID=0，工作机器ID=0）
snowflake_generator = SnowflakeIdGenerator(datacenter_id=0, worker_id=0)

def generate_snowflake_id() -> int:
    """
    生成雪花算法ID的便捷函数
    :return: 唯一ID
    """
    return snowflake_generator.generate_id()