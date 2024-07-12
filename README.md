# Flask Temp Server

## Overview

Wouldn't it be nice to have a UI hosted by your powerful batch server so you can avoid the hassle of spinning up and maintaining a Docker container? This application serves as a temporary web server, designed to be a front-end interface for a batch processing system. Upon startup, it operates like a standard batch job but with the added feature of providing a password-protected web interface. It automatically emails the administration group with instructions for accessing the UI along with the randomly generated password. The application also includes a shutdown feature, which can be triggered either automatically after a set period or manually by the user, ensuring the server doesn't run indefinitely. It is build on the Flask-Admin framework so you can add your custom model objects right into it.

## Features

- **Email Notifications:** Automatically sends an email to the administration group with detailed login instructions, facilitating easy access to the web interface.
- **Flexible Shutdown Mechanisms:** Supports automatic shutdown based on a predefined time limit or upon a direct user request, enhancing security and resource management.

## Prerequisites

To ensure a smooth setup and operation of the Flask Temp Server, the following prerequisites must be met:

- **Python Environment:** Python 3.6 or higher must be installed on your system. This is essential for running the Flask application and its dependencies.

## Installation

Clone the project from the repository. Setup your conda or venv based on the following requirements.

If the project doesn't work due to breaking changes in the newer libraries then see setup your environment using the requirements.txt file.

## Getting Started

You will need to create the database schema so the application and read/write to the database. Enter the flask shell and create the necessary tables by running the following commands.

```sh
flask shell
db.create_all()
quit()
```

Finally start the application by running the following command. `python app.py --notify_email some@email.com --timeout_minutes 10000`. The timeout can be set to any amount of time or leave it off to let the server run indefinitely.

## Contributing

We highly encourage contributions to the Flask Temp Server project! If you're interested in making improvements or adding new features, please start by opening an issue to discuss your ideas. This ensures a collaborative and effective approach to implementing significant changes.

## License

Flask Temp Server is made available under the MIT License. For more details, please refer to the LICENSE file included in this repository.

## Contact

Should you have any questions, require support, or wish to provide feedback, please don't hesitate to reach out to us at [email@example.com](mailto:email@example.com).
