import argparse, sys
import logging
import getpass

from irida_sistr_results.irida_connector import IridaConnector
from irida_sistr_results.irida_api import IridaAPI
from irida_sistr_results.irida_sistr_results import IridaSistrResults
from irida_sistr_results.sistr_writer import SistrCsvWriterShort, SistrExcelWriter

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Compile SISTR results from an IRIDA instance into a table.')

	parser.add_argument('--irida-url', action='store', dest='irida_url', help='The URL to the IRIDA instance.')
	parser.add_argument('--client-id', action='store', dest='client_id', help='The client id for an IRIDA instance.')
	parser.add_argument('--client-secret', action='store', dest='client_secret', help='The client secret for the IRIDA instance.')
	parser.add_argument('--username', action='store', dest='username', help='The username for the IRIDA instance.')
	parser.add_argument('--password', action='store', dest='password', help='The password for the IRIDA instance. Prompts for password if left blank.')
	parser.add_argument('--verbose', action='store_true', dest='verbose', help='Turn on verbose logging.')
	parser.add_argument('--project', action='append', dest='projects', help='Projects to scan for SISTR results. If left blank will scan all projects the user has access to.')
	parser.add_argument('--tabular', action='store_true', dest='tabular', help='Print results to stdout as tab-deliminited file.')
	parser.add_argument('--to-excel-file', action='store', dest='excel_file', help='Print results to the given excel file.')

	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()
	arg_dict = vars(args)

	if not arg_dict['tabular'] and (arg_dict['excel_file'] is None):
		logging.error("Must use one of --tabular or --to-excel-file [excel-file]")
		parser.print_help()
		sys.exit(1)

	if (arg_dict['verbose']):
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
	else:
		logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
	
	if arg_dict['password'] is None:
		arg_dict['password']=getpass.getpass('Enter password:')
	
	connector = IridaConnector(arg_dict['client_id'],arg_dict['client_secret'],arg_dict['username'],arg_dict['password'], arg_dict['irida_url'])
	irida_api = IridaAPI(connector)
	irida_results = IridaSistrResults(irida_api,True,True)
	
	sistr_list=irida_results.get_sistr_results(arg_dict['projects'][0])
	
	if arg_dict['tabular']:
		writer=SistrCsvWriterShort(arg_dict['irida_url'],sys.stdout)
		writer.write(sistr_list)
		writer.close()

	if arg_dict['excel_file'] is not None:
		writer=SistrExcelWriter(arg_dict['irida_url'], arg_dict['excel_file'])
		writer.write(sistr_list)
		writer.close()
