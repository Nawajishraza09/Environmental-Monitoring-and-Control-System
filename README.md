# Environmental-Monitoring-and-Control-System
The Environmental Monitoring and Control System (EMCS) is a comprehensive, solution aimed  at detecting, analyzing and managing key environmental parameters. 

# Key Features

- Real-time Data Monitoring: IoT-based sensors and API which keeps track air, water, and weather conditions. 
- Interactive Dashboard: A user-friendly interface to visualize environmental data.

# Technologies Used

- Project Build System: fman build system, please visit this site fore more "https://build-system.fman.io/" and "https://fman.io/"
- Programming Language: Python 3.7.12 
- Library: Pyqt5, qss, webengineview, json
- API: OpenWeather API
- Visualization: (OpenLayer) QWebEngine map compatibility
- Logging: Python Logging Module

# Setup/Run

- Clone the repository: git clone or download the file
- Run the application in terminal: Execute the command "fbs run" in the command prompt/terminal in which current folder where "src" folder is present, errors may oocurs due to missing python library/packages not correctly installed into the systemm and the build system properly.

# Usage

Welcome Module:

- This is the welcome screen of the application which only shows small info about the environment.

Air Quality Mudule:

- Value fetched based on the ip based location or selected location.
- Shows real-time air quality data of various differents gases like, NO, NO2, SO2, O3, NH3, PM2.5, PM.10
- Shows AQI calculated using weighted factors.
- Visualization usnig real-time line maps with different layers.

Water Quality Module:

- Shows different parameter values of the sensors which can be integrated later on but will only give false provided input value mean simulate on the false value.
- Draw graph level to show variation in level of different values.
- Visualizes different quality meter.

Weather Forecast Module:

- Value fetched based on the ip based location or selected location.
- Fetching real-time weather data from weather forecast APIs.
- Show different parameters and its values.
- Different Qt-Frame (cards) for visualization.

# Future Enhancements

- The project provides a solid foundation for future enhancements and practical deployments across large geographic and industrial scales.
- Several areas offer opportunities for expansion are moving some AI processing to the edge (e.g., on-device inference using ESP32 or Raspberry Pi) would reduce latency and make the system usable in remote or low-connectivity areas.
- Incorporating drone-based imaging can enhance vegetation at scale, covering large farm areas or forests efficiently.
- Developing a companion mobile app will enable farmers and field agents to upload data, view alerts, and receive recommendations instantly, even offline.
- Secure storage and validation of environmental data using blockchain could ensure traceability, transparency, and tamper-proof monitoring—especially useful for policy audits.
- By integrating actuators and decision rules, the system could be extended to automate irrigation, lighting, or nutrient supply in controlled agricultural environments.
- Expanding the climate module to integrate with real-time global hazard APIs could strengthen the system's capabilities in disaster response and mitigation.
- Collaborations with agricultural institutions, NGOs, or government agencies could allow pilot testing and field validation of the EMCS platform in real rural or urban environments.
