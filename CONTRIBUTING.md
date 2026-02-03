# Contributing to Timer CLI

First off, thank you for considering contributing to Timer CLI! It's people like you that make Timer CLI such a great tool.

## How Can I Contribute?

### Reporting Bugs
This section guides you through submitting a bug report for Timer CLI. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related bugs.

Before creating bug reports, please check this list as you might find out that you don't need to create one:
*   [Search the issue tracker](https://github.com/krishnakanthb13/timer_cli/issues) to see if the bug has already been reported.

### Suggesting Enhancements
This section guides you through submitting an enhancement suggestion for Timer CLI, including completely new features and minor improvements to existing functionality.

*   [Search the issue tracker](https://github.com/krishnakanthb13/timer_cli/issues) to see if the enhancement has already been suggested.

### Pull Requests
The process which described below should be followed to submit a pull request:

1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the TUI remains flicker-free and responsive.
5.  Issue that pull request!

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/krishnakanthb13/timer_cli.git
   cd timer_cli
   ```

2. Install in editable mode:
   ```bash
   pip install -e .
   ```

3. Run the application:
   ```bash
   python -m src.main
   ```

## Styleguide
*   Use standard Python PEP 8 style.
*   Keep `curses` logic separate from core models where possible.
*   Ensure all logs use the `log_action` helper.

## License
By contributing, you agree that your contributions will be licensed under its GPL v3 License.
