from cli import CommandLineInterface
from accountant import Accountant

# fetch command line options from user
cli = CommandLineInterface()
cli.run()

# get an accountant and pass him the options
accountant = Accountant(cli.options)

# let accountant compute the tax and create report
accountant.compute_tax()
accountant.write_report()