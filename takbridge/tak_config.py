import os
import yaml
import pytak
import asyncio
import logging


class TAKConfig:
    def __init__(self):
        self.logger = logging.getLogger('CoTLogger')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.logger.info('Initializing Sender Node')
        self.config_path = None
        self.config = self.load_config()
        self.sender = None
        self.receiver = None
        self.tx_queue = None
        self.rx_queue = None

    def load_config(self):
        # Load YAML
        config_file_path = self.config_path or os.path.join(os.path.dirname(__file__), 'config/config.yaml')
        with open(config_file_path, 'r') as file:
            config = yaml.safe_load(file)

        tak_config = config['tak_connection']['tak__parameters']

        cert_value = tak_config.get('PYTAK_TLS_CLIENT_CERT', '')
        if cert_value and not os.path.isabs(cert_value):
            base_dir = os.path.dirname(config_file_path)
            cert_path = os.path.join(base_dir, '..', 'certs', 'files', cert_value)
            tak_config['PYTAK_TLS_CLIENT_CERT'] = os.path.normpath(cert_path)

        for key in ["COT_URL", "PYTAK_TLS_CLIENT_CERT"]:
            if key not in tak_config:
                raise ValueError(f"Missing required TAK config key: {key}")

        return tak_config

    async def setup_config(self):
        self.clitool = pytak.CLITool(self.config)
        await self.clitool.setup()
        
        self.tx_queue = self.clitool.tx_queue
        self.rx_queue = self.clitool.rx_queue

        return self.clitool
