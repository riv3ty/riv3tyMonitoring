from setuptools import setup, find_packages

setup(
    name="riv3ty-monitoring-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-socketio==5.7.2",
        "psutil==5.9.4",
        "requests==2.28.2"
    ],
    entry_points={
        'console_scripts': [
            'riv3ty-agent=agent:main',
        ],
    },
    author="riv3ty",
    description="System monitoring agent for riv3ty Monitoring",
    python_requires=">=3.7",
)
