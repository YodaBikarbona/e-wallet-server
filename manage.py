import platform
import pdfkit
import os
import subprocess


def _get_pdfkit_config():
    """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
     need to support both since we develop on windows but deploy on Heroku.

    Returns:
        A pdfkit configuration
    """
    if platform.system() == 'Windows':
        return pdfkit.configuration()
    else:
        return pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')
