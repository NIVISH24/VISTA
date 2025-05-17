from setuptools import setup, find_packages

setup(
    name="linux-agent-local",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'psutil',
        'pyudev',
        'pynput',
        'sounddevice',
        'numpy',
        'scipy',
        'python-daemon'
    ],
    entry_points={
        'console_scripts': [
            'linux-agent-local=agent.main:main',
        ],
    },
    data_files=[
        ('/lib/systemd/system', ['systemd/linux-agent-local.service']),
        ('/var/log/linux-agent', [])
    ],
    python_requires='>=3.6',
)