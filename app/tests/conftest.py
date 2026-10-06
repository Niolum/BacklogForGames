import os
import tempfile


os.environ['APP_CONFIG__ENVIRONMENT'] = 'testing'
os.environ['APP_CONFIG__LOGS_PATH'] = tempfile.mkdtemp(prefix='backlog-test-logs-')
os.environ['STORAGE_CONFIG__LOCAL_ROOT'] = tempfile.mkdtemp(prefix='backlog-test-storage-')

pytest_plugins = [
    'tests.fixtures.container',
    'tests.fixtures.genre',
    'tests.fixtures.repositories',
]
